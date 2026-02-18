# How to Integrate Oracles on OPNet

OPNet does not have a built-in oracle service like Chainlink on Ethereum. Instead, you build your own oracle contract (or use a community oracle) that aggregates price feeds from multiple authorized sources. This guide covers the oracle contract pattern, price feed updates, and consuming oracle data from other contracts.

## Overview

The oracle pattern on OPNet:

1. **Deploy an oracle contract** that stores prices per asset
2. **Authorize oracle nodes** that can submit price updates
3. **Aggregate prices** using median calculation for manipulation resistance
4. **Protect against stale data** using block height checks

> **CRITICAL: Never use `medianTimestamp` for time-dependent contract logic.** Bitcoin's Median Time Past (MTP) can be manipulated by miners within a +/- 2 hour window. Always use `Blockchain.block.number` (block height) which is strictly monotonic and tamper-proof. The actual btc-runtime contracts (OP20, OP721, OP20S, Upgradeable) ALL use `block.number` for deadlines.
5. **Consume prices** from other contracts via cross-contract calls

## Step 1: Oracle Contract Structure

```typescript
import { u256 } from '@btc-vision/as-bignum/assembly';
import {
    OP_NET,
    Blockchain,
    Address,
    Calldata,
    BytesWriter,
    SafeMath,
    Revert,
    NetEvent,
    StoredU256,
    StoredU64,
    StoredU32,
    StoredAddressArray,
    AddressMemoryMap,
    ABIDataTypes,
    sha256,
    encodePointer,
    EMPTY_POINTER,
} from '@btc-vision/btc-runtime/runtime';

class PriceUpdated extends NetEvent {
    public constructor(
        public readonly asset: Address,
        public readonly price: u256,
        public readonly blockNumber: u64,
    ) {
        super('PriceUpdated');
    }

    protected override encodeData(writer: BytesWriter): void {
        writer.writeAddress(this.asset);
        writer.writeU256(this.price);
        writer.writeU64(this.blockNumber);
    }
}

@final
export class MultiOracle extends OP_NET {
    // Oracle node list
    private oraclesPointer: u16 = Blockchain.nextPointer;
    private oracles: StoredAddressArray;

    // Configuration
    private minOraclesPointer: u16 = Blockchain.nextPointer;
    private maxDeviationPointer: u16 = Blockchain.nextPointer;
    private maxStalenessPointer: u16 = Blockchain.nextPointer;

    private _minOracles: StoredU32;
    private _maxDeviation: StoredU256;  // Basis points (100 = 1%)
    private _maxStaleness: StoredU64;   // Blocks (144 blocks ≈ 24 hours)

    // Aggregated prices per asset
    private pricesPointer: u16 = Blockchain.nextPointer;
    private timestampsPointer: u16 = Blockchain.nextPointer;

    private _prices: AddressMemoryMap;
    private _timestamps: AddressMemoryMap;

    // Individual oracle submissions (keyed by oracle+asset hash)
    private oraclePricesPointer: u16 = Blockchain.nextPointer;
    private oracleTimestampsPointer: u16 = Blockchain.nextPointer;

    public constructor() {
        super();
        this.oracles = new StoredAddressArray(this.oraclesPointer);
        this._minOracles = new StoredU32(this.minOraclesPointer, 1);
        this._maxDeviation = new StoredU256(this.maxDeviationPointer, EMPTY_POINTER);
        this._maxStaleness = new StoredU64(this.maxStalenessPointer, 6); // 6 blocks default (~1 hour)
        this._prices = new AddressMemoryMap(this.pricesPointer);
        this._timestamps = new AddressMemoryMap(this.timestampsPointer);
    }

    public override onDeployment(calldata: Calldata): void {
        const minOracles = calldata.readU32();
        const maxDeviation = calldata.readU256();
        const maxStaleness = calldata.readU64();
        const initialOracles = calldata.readAddressArray();

        this._minOracles.value = minOracles;
        this._maxDeviation.value = maxDeviation;
        this._maxStaleness.value = maxStaleness;

        for (let i = 0; i < initialOracles.length; i++) {
            this.oracles.push(initialOracles[i]);
        }
    }

    // ... methods below
}
```

## Step 2: Price Feed Updates with Access Control

Only authorized oracle nodes can submit prices:

```typescript
@method(
    { name: 'asset', type: ABIDataTypes.ADDRESS },
    { name: 'price', type: ABIDataTypes.UINT256 },
)
@returns({ name: 'success', type: ABIDataTypes.BOOL })
@emit('PriceUpdated')
public submitPrice(calldata: Calldata): BytesWriter {
    const oracle = Blockchain.tx.sender;

    // Only authorized oracles can submit
    if (!this.isOracle(oracle)) {
        throw new Revert('Not authorized oracle');
    }

    const asset = calldata.readAddress();
    const price = calldata.readU256();

    // Store this oracle's individual submission
    const key = this.oracleAssetKey(oracle, asset);
    this.setOraclePrice(key, price);
    this.setOracleBlock(key, Blockchain.block.number);

    // Try to update the aggregated price
    this.tryUpdatePrice(asset);

    return new BytesWriter(0);
}

private isOracle(addr: Address): bool {
    const length = this.oracles.length;
    for (let i: u64 = 0; i < length; i++) {
        if (this.oracles.get(i).equals(addr)) {
            return true;
        }
    }
    return false;
}
```

## Step 3: Price Aggregation (Median)

The aggregation collects fresh prices from all oracles and calculates the median:

```typescript
private tryUpdatePrice(asset: Address): void {
    const prices: u256[] = [];
    const currentBlock: u64 = Blockchain.block.number;
    const maxStale = this._maxStaleness.value;

    // Collect valid (non-stale) prices from all oracles
    const oracleCount = this.oracles.length;
    for (let i: u64 = 0; i < oracleCount; i++) {
        const oracle = this.oracles.get(i);
        const key = this.oracleAssetKey(oracle, asset);
        const price = this.getOraclePrice(key);
        const blockNumber = this.getOracleBlock(key);

        if (price.isZero()) continue;                    // No submission yet
        if (currentBlock - blockNumber > maxStale) continue; // Stale

        prices.push(price);
    }

    // Need minimum number of fresh prices
    if (u32(prices.length) < u32(this._minOracles.value)) {
        return;
    }

    // Calculate median
    const medianPrice = this.calculateMedian(prices);

    // Check deviation from current price (anti-manipulation)
    const currentPrice = this._prices.get(asset);
    if (!currentPrice.isZero()) {
        if (!this.withinDeviation(currentPrice, medianPrice)) {
            return;  // Price moved too much -- potential manipulation
        }
    }

    // Update aggregated price
    this._prices.set(asset, medianPrice);
    this._timestamps.set(asset, u256.fromU64(currentBlock));

    this.emitEvent(new PriceUpdated(asset, medianPrice, currentBlock));
}

private calculateMedian(prices: u256[]): u256 {
    const len = prices.length;

    // Bubble sort (fine for small arrays of oracle count)
    for (let i = 0; i < len; i++) {
        for (let j = i + 1; j < len; j++) {
            if (prices[j] < prices[i]) {
                const temp = prices[i];
                prices[i] = prices[j];
                prices[j] = temp;
            }
        }
    }

    const mid = len / 2;
    if (len % 2 == 0) {
        return SafeMath.div(
            SafeMath.add(prices[mid - 1], prices[mid]),
            u256.fromU64(2),
        );
    }
    return prices[mid];
}

private withinDeviation(oldPrice: u256, newPrice: u256): bool {
    const maxDev = this._maxDeviation.value;
    const basisPoints = u256.fromU64(10000);
    const maxChange = SafeMath.div(SafeMath.mul(oldPrice, maxDev), basisPoints);
    const lowerBound = SafeMath.sub(oldPrice, maxChange);
    const upperBound = SafeMath.add(oldPrice, maxChange);
    return newPrice >= lowerBound && newPrice <= upperBound;
}
```

## Step 4: Reading Prices (with Staleness Check)

```typescript
@method({ name: 'asset', type: ABIDataTypes.ADDRESS })
@returns(
    { name: 'price', type: ABIDataTypes.UINT256 },
    { name: 'timestamp', type: ABIDataTypes.UINT64 },
)
public getPrice(calldata: Calldata): BytesWriter {
    const asset = calldata.readAddress();

    const price = this._prices.get(asset);
    const blockNumber: u64 = this._timestamps.get(asset).toU64();

    // Reject stale prices
    const currentBlock: u64 = Blockchain.block.number;
    if (currentBlock - blockNumber > this._maxStaleness.value) {
        throw new Revert('Price is stale');
    }

    if (price.isZero()) {
        throw new Revert('Price not available');
    }

    const writer = new BytesWriter(40);
    writer.writeU256(price);
    writer.writeU64(timestamp);
    return writer;
}
```

## Step 5: Consuming Oracle Data from Another Contract

To use oracle prices from a DeFi contract, make a cross-contract call:

```typescript
// In your DeFi contract
import { Blockchain } from '@btc-vision/btc-runtime/runtime';

private getOraclePrice(oracleAddress: Address, asset: Address): u256 {
    // Build the calldata for getPrice(asset)
    const callWriter = new BytesWriter(36);
    callWriter.writeSelector(0x41976e09);  // getPrice(address) selector
    callWriter.writeAddress(asset);

    // Make the cross-contract call (pass BytesWriter directly, not getBuffer())
    const result = Blockchain.call(
        oracleAddress,
        callWriter,
        true,  // stopOnFailure = true (revert if call fails)
    );

    // Parse the response: result.data is a BytesReader
    const price = result.data.readU256();
    // const timestamp = result.data.readU64();  // if needed

    return price;
}

// Use in your contract logic
public calculateLoanValue(calldata: Calldata): BytesWriter {
    const collateralAsset = calldata.readAddress();
    const collateralAmount = calldata.readU256();

    // Get price from oracle
    const price = this.getOraclePrice(this._oracleAddress.value, collateralAsset);

    // Calculate value: amount * price / precision
    const value = SafeMath.div(
        SafeMath.mul(collateralAmount, price),
        u256.fromU64(1_000_000),  // 6 decimal price precision
    );

    const writer = new BytesWriter(32);
    writer.writeU256(value);
    return writer;
}
```

## Oracle Management

The deployer can add and remove oracle nodes:

```typescript
@method({ name: 'oracle', type: ABIDataTypes.ADDRESS })
@returns({ name: 'success', type: ABIDataTypes.BOOL })
public addOracle(calldata: Calldata): BytesWriter {
    this.onlyDeployer(Blockchain.tx.sender);
    const oracle = calldata.readAddress();

    // Check for duplicates
    const length = this.oracles.length;
    for (let i: u64 = 0; i < length; i++) {
        if (this.oracles.get(i).equals(oracle)) {
            throw new Revert('Oracle already exists');
        }
    }

    this.oracles.push(oracle);
    return new BytesWriter(0);
}

@method({ name: 'oracle', type: ABIDataTypes.ADDRESS })
@returns({ name: 'success', type: ABIDataTypes.BOOL })
public removeOracle(calldata: Calldata): BytesWriter {
    this.onlyDeployer(Blockchain.tx.sender);
    const oracle = calldata.readAddress();

    // Find and remove (swap with last, then pop)
    let found = false;
    const length = this.oracles.length;
    for (let i: u64 = 0; i < length; i++) {
        if (this.oracles.get(i).equals(oracle)) {
            if (i < length - 1) {
                this.oracles.set(i, this.oracles.get(length - 1));
            }
            this.oracles.pop();
            found = true;
            break;
        }
    }

    if (!found) throw new Revert('Oracle not found');
    if (this.oracles.length < u64(this._minOracles.value)) {
        throw new Revert('Would go below minimum oracles');
    }

    return new BytesWriter(0);
}
```

## Deployment Parameters

When deploying the oracle contract, pass configuration in the calldata:

```typescript
const deployCalldata = new BytesWriter(128);
deployCalldata.writeU32(3);                              // minOracles: need 3 fresh prices
deployCalldata.writeU256(u256.fromU64(500));            // maxDeviation: 5% (500 basis points)
deployCalldata.writeU64(6);                              // maxStaleness: 6 blocks (~1 hour)
deployCalldata.writeAddressArray([oracle1, oracle2, oracle3]);
```

## Comparison with Chainlink (Ethereum)

| Feature | Chainlink (Ethereum) | OPNet Oracle |
|---------|---------------------|--------------|
| Architecture | External oracle network + proxy | Self-contained contract |
| Price source | Chainlink nodes | Your authorized oracle nodes |
| Aggregation | Off-chain aggregation | On-chain median calculation |
| Timing | `block.timestamp` | `Blockchain.block.number` (use block height, NOT medianTimestamp -- miners can manipulate MTP) |
| Staleness | `updatedAt` check | Built-in `maxStaleness` |
| Deviation | Heartbeat + deviation trigger | Built-in `maxDeviation` |
| Dependencies | Chainlink contracts + feeds | None (self-contained) |

## Best Practices

1. **Use at least 3 oracle nodes.** Median of 3+ values resists single-source manipulation.

2. **Set appropriate staleness in blocks.** 6 blocks (~1 hour) is common; fewer for volatile assets. 144 blocks is approximately 24 hours on Bitcoin.

3. **Set deviation thresholds.** 5% (500 basis points) prevents sudden jumps from manipulated feeds.

4. **Use `Blockchain.block.number` instead of `medianTimestamp`.** Bitcoin's median time past can be manipulated by miners within a +/- 2 hour window. Block height is strictly monotonic and tamper-proof.

5. **Store the oracle address in consuming contracts.** Use `StoredAddress` so the oracle can be updated if needed.

6. **Always check for stale/zero prices.** Never use a price without validating freshness.

## References

- [Oracle Integration Example](../docs/btc-runtime/examples/oracle-integration.md) -- Complete implementation
- [Cross-Contract Calls](../docs/btc-runtime/advanced/cross-contract-calls.md) -- How to call between contracts
- [Storage System](../docs/btc-runtime/core-concepts/storage-system.md) -- Pointers and storage maps
