# How to Do Offline/Air-Gapped Signing

OPNet supports a two-phase transaction workflow where construction (requiring network access) is separated from signing (requiring private keys). This is essential for air-gapped security, hardware wallets, and multi-party signing scenarios.

## Overview

The offline signing system works in three phases:

1. **Phase 1 (Online)** -- Build the transaction, fetch UTXOs, serialize the complete state
2. **Transfer** -- Move the serialized state to the offline device (USB, QR code, file)
3. **Phase 2 (Offline)** -- Import state, sign with private key, export signed transaction hex
4. **Broadcast** -- Move signed hex back to online machine and broadcast

All operations use `OfflineTransactionManager`, which is a static class.

## Phase 1: Export on Online Machine

The online machine has access to UTXOs and fee estimates but does NOT have the private key. Use a watch-only signer (public key only) to build the transaction.

### Export a Funding (BTC Transfer) Transaction

```typescript
import {
    OfflineTransactionManager,
    EcKeyPair,
} from '@btc-vision/transaction';
import { networks } from '@btc-vision/bitcoin';

// Watch-only signer (public key only -- no private key on this machine)
const watchOnlySigner = EcKeyPair.fromPublicKey(publicKeyHex, networks.bitcoin);

const serializedState = OfflineTransactionManager.exportFunding({
    signer: watchOnlySigner,
    mldsaSigner: null,
    network: networks.bitcoin,
    from: 'bc1p...sender',
    to: 'bc1p...receiver',
    utxos: fetchedUtxos,       // UTXOs fetched from the network
    feeRate: 10,                // sat/vB
    priorityFee: 0n,
    gasSatFee: 0n,
    amount: 50000n,             // Amount in satoshis
});

// Validate before transfer
console.log('Valid:', OfflineTransactionManager.validate(serializedState));

// Inspect the state (optional)
const inspected = OfflineTransactionManager.inspect(serializedState);
console.log('Type:', inspected.header.transactionType);
console.log('Fee rate:', inspected.baseParams.feeRate);
console.log('UTXOs:', inspected.utxos.length);

// Transfer serializedState (base64 string) to offline machine
```

### Export a Contract Interaction

```typescript
const interactionState = OfflineTransactionManager.exportInteraction(
    {
        signer: watchOnlySigner,
        mldsaSigner: null,
        network: networks.bitcoin,
        from: 'bc1p...sender',
        to: 'bc1p...contractAddress',
        utxos: myUtxos,
        feeRate: 15,
        priorityFee: 330n,
        gasSatFee: 10000n,
        calldata: encodedCalldata,   // ABI-encoded function call
    },
    {
        compiledTargetScript: toHex(compiledScript),
        randomBytes: toHex(randomBytes),  // MUST be preserved for determinism
    },
);
```

### Export a Deployment

```typescript
import { Compressor } from '@btc-vision/transaction';
import { toHex } from '@btc-vision/bitcoin';

const bytecode = await Compressor.compress(contractWasm);
const randomBytes = crypto.getRandomValues(new Uint8Array(32));

const deployState = OfflineTransactionManager.exportDeployment(
    {
        signer: watchOnlySigner,
        mldsaSigner: null,
        network: networks.bitcoin,
        from: 'bc1p...deployer',
        to: 'bc1p...contract',
        utxos: myUtxos,
        feeRate: 15,
        priorityFee: 330n,
        gasSatFee: 10000n,
        bytecode,
        challenge: myChallenge,
    },
    {
        compiledTargetScript: toHex(compiledScript),
        randomBytes: toHex(randomBytes),
    },
);
```

## Phase 2: Sign on Offline Machine

The offline machine has the private key but no network access.

### Simple: Import, Sign, and Export in One Call

```typescript
import {
    OfflineTransactionManager,
    EcKeyPair,
} from '@btc-vision/transaction';
import { networks } from '@btc-vision/bitcoin';

// Load private key on air-gapped machine
const offlineSigner = EcKeyPair.fromWIF('L1...privateKeyWIF', networks.bitcoin);

// Import, sign, and export the signed transaction hex
const signedTxHex = await OfflineTransactionManager.importSignAndExport(
    serializedState,     // Base64 string from Phase 1
    { signer: offlineSigner },
);

console.log('Signed TX hex:', signedTxHex);
// Transfer signedTxHex back to online machine
```

### Advanced: Manual Control

If you need more control over the signing process:

```typescript
// Step 1: Import and reconstruct the builder
const builder = OfflineTransactionManager.importForSigning(
    serializedState,
    { signer: offlineSigner },
);

// Step 2: Inspect the builder before signing (optional)
console.log('Transaction type:', builder.type);

// Step 3: Sign and export
const signedTxHex = await OfflineTransactionManager.signAndExport(builder);
```

### With Quantum Signer

```typescript
const signedTxHex = await OfflineTransactionManager.importSignAndExport(
    serializedState,
    {
        signer: offlineSigner,
        mldsaSigner: offlineQuantumSigner,  // QuantumBIP32Interface
    },
);
```

## Phase 3: Broadcast

Back on the online machine, broadcast the signed transaction:

```typescript
await provider.sendRawTransaction(signedTxHex);
console.log('Transaction broadcast successfully');
```

## Fee Bumping (RBF)

If a transaction is stuck, you can rebuild it with a higher fee rate using the original serialized state:

```typescript
// Option A: Rebuild state with new fees, then sign separately
const bumpedState = OfflineTransactionManager.rebuildWithNewFees(
    originalState,
    25,  // New fee rate: 25 sat/vB (was 10)
);

const signedBumped = await OfflineTransactionManager.importSignAndExport(
    bumpedState,
    { signer: offlineSigner },
);

// Option B: Rebuild + sign in one call
const signedBumped = await OfflineTransactionManager.rebuildSignAndExport(
    originalState,
    25,  // New fee rate
    { signer: offlineSigner },
);

// Option C: Override multiple fee parameters
const signedBumped = await OfflineTransactionManager.importSignAndExport(
    originalState,
    {
        signer: offlineSigner,
        newFeeRate: 25,
        newPriorityFee: 500n,
        newGasSatFee: 20000n,
    },
);
```

## Multisig Offline Workflow

For multi-signature transactions where each signer adds their signature independently on separate offline machines:

```typescript
// Step 1: Export multisig (online coordinator)
const multisigState = OfflineTransactionManager.exportMultiSig({
    signer: coordinatorSigner,
    mldsaSigner: null,
    network: networks.bitcoin,
    utxos: sharedUtxos,
    feeRate: 10,
    from: 'bc1p...multisig',
    pubkeys: [pubkey1, pubkey2, pubkey3],
    minimumSignatures: 2,
    receiver: 'bc1p...destination',
    requestedAmount: 100000n,
    refundVault: 'bc1p...refund',
});

// Step 2: First signer adds signature (offline)
const result1 = await OfflineTransactionManager.multiSigAddSignature(
    multisigState,
    signer1,
);
console.log('Signer 1 signed:', result1.signed);
console.log('Complete:', result1.final);

// Step 3: Second signer adds signature (offline)
const result2 = await OfflineTransactionManager.multiSigAddSignature(
    result1.state,   // Pass the updated state
    signer2,
);

// Step 4: Check status and finalize (online)
const status = OfflineTransactionManager.multiSigGetSignatureStatus(result2.state);
console.log(`Signatures: ${status.collected}/${status.required}`);

if (status.isComplete) {
    const signedTxHex = OfflineTransactionManager.multiSigFinalize(result2.state);
    await provider.sendRawTransaction(signedTxHex);
    console.log('Multisig transaction broadcast!');
}
```

## Inspection and Validation Utilities

```typescript
// Validate integrity (checksum and format)
const isValid = OfflineTransactionManager.validate(serializedState);

// Inspect without signing
const state = OfflineTransactionManager.inspect(serializedState);
console.log('Transaction type:', state.header.transactionType);
console.log('From:', state.baseParams.from);
console.log('To:', state.baseParams.to);

// Get transaction type
const type = OfflineTransactionManager.getType(serializedState);

// Format conversion
const hexState = OfflineTransactionManager.toHex(serializedState);
const base64State = OfflineTransactionManager.fromHex(hexState);
```

## Serialization Format

The serialized state uses a binary format with:
- Magic byte `0x42` ('B' for Bitcoin)
- Header with format/consensus versions, transaction type, chain ID, timestamp
- Complete UTXO data and transaction parameters
- Precomputed scripts and random bytes (for deterministic reconstruction)
- Double SHA-256 checksum for integrity verification

**Critical:** The `randomBytes` field must be preserved exactly. If different random bytes are used during reconstruction, the resulting scripts will differ and the transaction will be invalid.

## All Export Methods

| Method | Purpose |
|--------|---------|
| `exportFunding()` | BTC transfer transaction |
| `exportDeployment()` | Contract deployment (requires compiled script + random bytes) |
| `exportInteraction()` | Contract interaction (requires compiled script + random bytes) |
| `exportMultiSig()` | Multi-signature transaction |
| `exportCustomScript()` | Custom Bitcoin script transaction |
| `exportCancel()` | Transaction cancellation |
| `exportFromBuilder()` | Export from pre-built transaction builder |

## References

- [Offline Transaction Signing](../docs/transaction/offline/offline-transaction-signing.md) -- Complete API reference
- [Multisig Transactions](../docs/transaction/transaction-building/multisig-transactions.md) -- Multisig details
- [Transaction Factory](../docs/transaction/transaction-building/transaction-factory.md) -- Transaction construction
