# How to Build a DEX on OPNet (NativeSwap Pattern)

Building a decentralized exchange on OPNet requires fundamentally different patterns than Ethereum DEXes because **OPNet contracts cannot hold BTC**. This guide explains the NativeSwap approach: virtual reserves, two-phase commits, queue impact, slashing, and mandatory CSV timelocks.

## The Core Problem

On Ethereum, a Uniswap-style AMM holds both tokens in a smart contract pool. On OPNet:

- Smart contracts **cannot custody BTC** (Bitcoin's UTXO model does not allow this)
- Tokens (OP20) live in contract state and can be held by contracts
- BTC lives in UTXOs controlled by Bitcoin scripts

This means a traditional `x * y = k` pool where both assets are in the contract does not work for BTC/token pairs. The NativeSwap pattern solves this with **virtual reserves**.

## Virtual Reserves

Instead of physically holding BTC, the AMM tracks a **virtual BTC reserve** -- a number in contract storage that represents how much BTC "should" be in the pool. The token side is real (held in contract state), but the BTC side is virtual.

```typescript
// Contract storage
private virtualBtcReservePointer: u16 = Blockchain.nextPointer;
private tokenReservePointer: u16 = Blockchain.nextPointer;

private _virtualBtcReserve: StoredU256;  // Virtual -- not actual BTC
private _tokenReserve: StoredU256;       // Real -- actual tokens in contract
```

The AMM formula still uses `x * y = k`, but the BTC side is verified through Bitcoin transaction outputs rather than contract balance.

## Two-Phase Commit (Reservation System)

Because Bitcoin transactions take time to confirm and prices can move, NativeSwap uses a **reservation system** to lock prices:

### Phase 1: Reserve

The user calls the contract to reserve a swap at the current price. The contract:

1. Calculates the output amount using the AMM formula
2. Locks (reserves) the output tokens
3. Records the reservation with an expiry
4. Returns the required BTC payment details

```typescript
// Simplified reservation logic
@method(
    { name: 'tokenOut', type: ABIDataTypes.ADDRESS },
    { name: 'amountIn', type: ABIDataTypes.UINT256 },
)
@returns({ name: 'reservationId', type: ABIDataTypes.UINT256 })
public reserve(calldata: Calldata): BytesWriter {
    const tokenOut = calldata.readAddress();
    const amountIn = calldata.readU256();

    // Calculate output using AMM formula
    const amountOut = this.getAmountOut(amountIn);

    // Lock the output tokens
    this.lockedTokens.set(reservationId, amountOut);
    this.reservationExpiry.set(reservationId,
        Blockchain.block.numberU256 + RESERVATION_TIMEOUT_BLOCKS);

    // Store reservation details
    this.reservations.set(reservationId, /* ... */);

    const writer = new BytesWriter(32);
    writer.writeU256(reservationId);
    return writer;
}
```

### Phase 2: Execute

After the user sends the BTC payment (confirmed on Bitcoin), they call the contract to complete the swap. The contract verifies the BTC was actually sent by checking transaction outputs.

```typescript
@method({ name: 'reservationId', type: ABIDataTypes.UINT256 })
@returns({ name: 'success', type: ABIDataTypes.BOOL })
public execute(calldata: Calldata): BytesWriter {
    const reservationId = calldata.readU256();

    // Verify reservation exists and has not expired
    // Verify BTC payment via Blockchain.tx.outputs
    // Transfer locked tokens to the buyer
    // Update virtual reserves

    return new BytesWriter(0);
}
```

### Why Two Phases?

| Problem | Solution |
|---------|----------|
| BTC takes time to confirm | Reservation locks the price |
| Price can move between reserve and execute | Reservation guarantees the quoted rate |
| User might not send BTC | Reservation expires, tokens unlock |
| Front-running | Reservation is per-user, not broadcast |

## Queue Impact (Logarithmic Scaling)

When multiple sellers queue up to sell tokens for BTC, the pending sell pressure affects the effective price. NativeSwap uses **logarithmic scaling** for queue impact:

```
effectivePrice = basePrice * (1 - log2(1 + pendingSellVolume / dailyVolume) * impactFactor)
```

This means:
- Small pending sells have minimal impact
- Large pending sells progressively reduce the price
- The impact scales logarithmically, not linearly (prevents cliff effects)

The queue impact discourages large dump orders and encourages smaller, more gradual selling.

## Slashing (Anti-Manipulation)

To prevent queue manipulation (reserving large sells to suppress price, then canceling), NativeSwap implements **slashing**:

- If a seller cancels a reservation or lets it expire, a percentage of their staked tokens is slashed
- The slashed amount goes to the pool (benefits LPs) or is burned
- Slash percentage increases with reservation size relative to pool

```typescript
// Simplified slashing check
private calculateSlash(reservationAmount: u256, poolSize: u256): u256 {
    // Base slash: 1% of reservation
    // Scales up with size relative to pool
    const ratio = SafeMath.div(
        SafeMath.mul(reservationAmount, u256.fromU64(10000)),
        poolSize
    );
    // Minimum 1%, maximum 10%
    const slashBps = SafeMath.min(
        SafeMath.max(ratio, u256.fromU64(100)),
        u256.fromU64(1000)
    );
    return SafeMath.div(
        SafeMath.mul(reservationAmount, slashBps),
        u256.fromU64(10000)
    );
}
```

## CSV Timelocks (MANDATORY for Sellers)

**All seller addresses MUST use CSV (CheckSequenceVerify) timelocks.** This is not optional -- it is a consensus requirement for NativeSwap.

CSV timelocks ensure that BTC received by sellers cannot be immediately spent, preventing:
- Flash loan attacks (borrow BTC, sell tokens, repay BTC)
- Rapid buy/sell cycling to manipulate reserves
- Atomic arbitrage that drains the pool

```
Seller receives BTC -> CSV timelock (e.g., 6 blocks) -> BTC becomes spendable
```

The timelock is enforced at the Bitcoin script level, not the contract level. When the NativeSwap contract constructs the payment output for a seller, it includes a CSV constraint in the output script.

## Using MotoSwap (Existing DEX)

If you want to interact with an existing DEX rather than build one, OPNet has MotoSwap (similar to Uniswap V2). Here is how to use it:

### Setup

```typescript
import {
    getContract,
    IMotoswapRouterContract,
    IMotoswapFactoryContract,
    IOP20Contract,
    MOTOSWAP_ROUTER_ABI,
    MotoSwapFactoryAbi,
    OP_20_ABI,
    JSONRpcProvider,
    TransactionParameters,
} from 'opnet';
import { Wallet, Mnemonic, MLDSASecurityLevel, Address, AddressTypes } from '@btc-vision/transaction';
import { networks } from '@btc-vision/bitcoin';

const network = networks.regtest;
const provider = new JSONRpcProvider({ url: 'https://regtest.opnet.org', network });
const mnemonic = new Mnemonic('your words ...', '', network, MLDSASecurityLevel.LEVEL2);
const wallet = mnemonic.deriveUnisat(AddressTypes.P2TR, 0);

const router = getContract<IMotoswapRouterContract>(
    routerAddress, MOTOSWAP_ROUTER_ABI, provider, network, wallet.address,
);
```

### Get a Price Quote

```typescript
const amountIn = 100_000_000n;  // 1 WBTC (8 decimals)
const path = [wbtcAddress, motoAddress];

const result = await router.getAmountsOut(amountIn, path);
const expectedOutput = result.properties.amountsOut[1];
console.log('Expected output:', expectedOutput);
```

### Execute a Swap

```typescript
// 1. Approve the router to spend your tokens
const tokenIn = getContract<IOP20Contract>(
    wbtcAddress, OP_20_ABI, provider, network, wallet.address,
);

const approve = await tokenIn.increaseAllowance(router.address, amountIn);
await approve.sendTransaction({
    signer: wallet.keypair,
    mldsaSigner: wallet.mldsaKeypair,
    refundTo: wallet.p2tr,
    maximumAllowedSatToSpend: 10000n,
    feeRate: 10,
    network,
});

// 2. Execute the swap with slippage protection
const minOutput = expectedOutput - (expectedOutput * 200n / 10000n);  // 2% slippage
const deadline = BigInt(Math.floor(Date.now() / 1000) + 600);        // 10 min

const swap = await router.swapExactTokensForTokensSupportingFeeOnTransferTokens(
    amountIn, minOutput, path, wallet.address, deadline,
);

const receipt = await swap.sendTransaction({
    signer: wallet.keypair,
    mldsaSigner: wallet.mldsaKeypair,
    refundTo: wallet.p2tr,
    maximumAllowedSatToSpend: 20000n,
    feeRate: 10,
    network,
});

console.log('Swap TX:', receipt.transactionId);
```

## Architecture Summary

```
NativeSwap DEX Architecture:

+-------------------+
|   Virtual BTC     |  (number in storage, not actual BTC)
|   Reserve         |
+-------------------+
         |
    AMM Formula (x * y = k)
         |
+-------------------+
|   Token Reserve   |  (actual OP20 tokens held by contract)
+-------------------+

Swap Flow:
1. User calls reserve() -> locks price + output tokens
2. User sends BTC on Bitcoin L1 -> with CSV timelock on seller output
3. User calls execute() -> contract verifies BTC outputs, releases tokens
4. Virtual BTC reserve updated

Queue Management:
- Pending sells create queue impact (logarithmic scaling)
- Cancellations are slashed (anti-manipulation)
- CSV timelocks prevent flash loan attacks
```

## References

- [Advanced Swaps (MotoSwap)](../docs/opnet/examples/advanced-swaps.md) -- Using the MotoSwap DEX
- [MotoSwap ABIs](../docs/opnet/abi-reference/motoswap-abis.md) -- ABI definitions for MotoSwap contracts
- [Transaction Configuration](../docs/opnet/contracts/transaction-configuration.md) -- Advanced transaction options
