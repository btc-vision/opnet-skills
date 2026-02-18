# How to Do Airdrops on OPNet

OPNet has two separate address systems -- Bitcoin addresses (bc1p/bc1q, derived from tweaked public keys) and OPNet addresses (ML-DSA public key hashes, 32 bytes). This dual-address architecture means you **cannot** simply loop through a list of recipients and transfer tokens like you would on Ethereum. Instead, you must use a **claim-based pattern**.

## Why Loop-and-Transfer Does Not Work

On Ethereum, airdropping is straightforward: iterate over a list of addresses and call `transfer()` for each. On OPNet, this fails for two reasons:

1. **Two address systems**: A user's Bitcoin address (used for BTC transactions) is not the same as their OPNet address (used for smart contract state). The contract stores balances keyed by OPNet (ML-DSA) addresses, but your airdrop list likely contains Bitcoin addresses.

2. **No address linkage by default**: The contract has no way to know which OPNet address corresponds to which Bitcoin address unless the user proves it.

### The Banana Locker Analogy

Think of it like an office building with lockers:

- **Bitcoin address** = the key to the front door of the building (your tweaked public key)
- **OPNet address** = the combination to your personal locker inside (your ML-DSA public key hash)

If someone puts a banana (tokens) in locker #42, but you only have a front door key, you cannot open the locker. You need to prove you own both the front door key AND locker #42. The claim pattern is how the user proves they own the front door key (Bitcoin address) so the contract can deposit into their locker (OPNet address).

## The Claim-Based Airdrop Pattern

### Step 1: Deploy an Airdrop Contract with Allocations

Deploy a contract that stores allocations keyed by the tweaked public key (Bitcoin identity). During deployment, the deployer provides a Merkle root or a direct mapping of eligible addresses and amounts.

```typescript
// Contract side (AssemblyScript)
import {
    OP_NET,
    Blockchain,
    Address,
    Calldata,
    BytesWriter,
    SafeMath,
    Revert,
    NetEvent,
    AddressMemoryMap,
    StoredString,
    sha256,
    encodeSelector,
    Selector,
} from '@btc-vision/btc-runtime/runtime';
// NOTE: @method, @returns, @emit, @final, and ABIDataTypes are compile-time
// globals from @btc-vision/opnet-transform. Do NOT import them.
import { u256 } from '@btc-vision/as-bignum/assembly';

class AirdropClaimed extends NetEvent {
    public constructor(
        public readonly claimant: Address,
        public readonly amount: u256
    ) {
        super('AirdropClaimed');
    }

    protected override encodeData(writer: BytesWriter): void {
        writer.writeAddress(this.claimant);
        writer.writeU256(this.amount);
    }
}

@final
export class AirdropContract extends OP_NET {
    // Selector for claim method
    private readonly claimSelector: Selector = encodeSelector('claim(bytes)');

    // Allocations keyed by tweaked public key hash
    private allocationsPointer: u16 = Blockchain.nextPointer;
    private claimedPointer: u16 = Blockchain.nextPointer;
    private tokenAddressPointer: u16 = Blockchain.nextPointer;

    private _allocations: AddressMemoryMap;
    private _claimed: AddressMemoryMap;
    private _tokenAddress: StoredString;

    public constructor() {
        super();
        this._allocations = new AddressMemoryMap(this.allocationsPointer);
        this._claimed = new AddressMemoryMap(this.claimedPointer);
        this._tokenAddress = new StoredString(this.tokenAddressPointer);
    }

    public callMethod(calldata: Calldata): BytesWriter {
        const selector = calldata.readSelector();
        switch (selector) {
            case this.claimSelector:
                return this.claim(calldata);
            default:
                return super.callMethod(calldata);
        }
    }

    @method({ name: 'signature', type: ABIDataTypes.BYTES })
    @returns({ name: 'success', type: ABIDataTypes.BOOL })
    @emit('AirdropClaimed')
    private claim(calldata: Calldata): BytesWriter {
        const signature = calldata.readBytesWithLength();

        // Build the message the user signed (includes contract address for replay protection)
        const message = new BytesWriter(64);
        message.writeAddress(Blockchain.contract.address);
        message.writeAddress(Blockchain.tx.sender);
        const messageHash = sha256(message.getBuffer());

        // Verify the signature against the transaction origin (tweaked public key)
        // This proves the caller owns the Bitcoin address in the allocation list
        if (!Blockchain.verifySignature(
            Blockchain.tx.origin,  // ExtendedAddress with tweaked public key
            signature,
            messageHash,
            false  // Use consensus-aware verification
        )) {
            throw new Revert('Invalid signature');
        }

        // Look up allocation by the origin's identity
        const originAddress = Blockchain.tx.origin;
        const allocation = this._allocations.get(originAddress);

        if (allocation.isZero()) {
            throw new Revert('No allocation for this address');
        }

        // Check not already claimed
        if (!this._claimed.get(originAddress).isZero()) {
            throw new Revert('Already claimed');
        }

        // Mark as claimed
        this._claimed.set(originAddress, u256.One);

        // Mint tokens to the caller's OPNet address (ML-DSA identity)
        // Or transfer from contract's token balance
        // this._mint(Blockchain.tx.sender, allocation);

        this.emitEvent(new AirdropClaimed(Blockchain.tx.sender, allocation));

        const writer = new BytesWriter(1);
        writer.writeBoolean(true);
        return writer;
    }
}
```

### Step 2: User Signs a Claim Message

On the client side, the user signs a message proving they own the Bitcoin address. Use the Auto methods so the code works in both browser and backend environments.

```typescript
// Client side (TypeScript)
import { MessageSigner } from '@btc-vision/transaction';

// Browser: OP_WALLET signs automatically (no keypair needed)
const signed = await MessageSigner.tweakAndSignMessageAuto(
    'claim-airdrop:' + contractAddress,
);

// Backend: provide keypair explicitly
const signed = await MessageSigner.tweakAndSignMessageAuto(
    'claim-airdrop:' + contractAddress,
    wallet.keypair,
    network,
);
```

### Step 3: Contract Verifies and Distributes

When the user calls `claim()` with their signature:

1. The contract builds the expected message hash
2. It calls `Blockchain.verifySignature()` to verify the signature matches `Blockchain.tx.origin` (the tweaked public key)
3. It looks up the allocation for that tweaked public key
4. It mints/transfers tokens to `Blockchain.tx.sender` (the caller's OPNet/ML-DSA address)

## Alternative: Off-Chain Merkle Proof

For large airdrops (thousands of recipients), storing all allocations on-chain is expensive. Use a Merkle tree instead:

1. Build a Merkle tree off-chain from the allocation list
2. Store only the Merkle root in the contract
3. Users provide their Merkle proof when claiming
4. Contract verifies the proof and the signature

```typescript
// Simplified Merkle verification in contract
private verifyMerkleProof(
    leaf: Uint8Array,
    proof: Uint8Array[],
    root: Uint8Array
): bool {
    let hash = leaf;
    for (let i = 0; i < proof.length; i++) {
        const combined = new BytesWriter(64);
        // Compare bytes lexicographically using memory.compare
        if (memory.compare(changetype<usize>(hash), changetype<usize>(proof[i]), 32) < 0) {
            combined.writeBytes(hash);
            combined.writeBytes(proof[i]);
        } else {
            combined.writeBytes(proof[i]);
            combined.writeBytes(hash);
        }
        hash = sha256(combined.getBuffer());
    }
    // Compare byte content, not references
    return memory.compare(changetype<usize>(hash), changetype<usize>(root), 32) == 0;
}
```

## Summary

| Approach | Ethereum | OPNet |
|----------|----------|-------|
| Direct transfer loop | Works | Does NOT work (two address systems) |
| Claim with signature | Optional optimization | **Required pattern** |
| Address used for allocation | Same ETH address | Tweaked public key (Bitcoin identity) |
| Address receiving tokens | Same ETH address | ML-DSA address (OPNet identity) |
| Proof mechanism | None needed | `Blockchain.verifySignature()` |

## References

- [Signature Verification](../docs/btc-runtime/advanced/signature-verification.md) -- Contract-side verification API
- [MessageSigner](../docs/transaction/keypair/message-signer.md) -- Client-side signing (Auto methods)
