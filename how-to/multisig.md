# How to Build Multisig Transactions on OPNet

OPNet supports M-of-N multi-signature transactions using Taproot script trees and a PSBT (Partially Signed Bitcoin Transaction) workflow. This guide shows how to create, sign, and broadcast multisig transactions.

## Overview

A multisig transaction requires M signatures out of N possible signers before it can be broadcast. OPNet uses `MultiSignTransaction` which creates Taproot-based multisig scripts. The PSBT workflow allows signatures to be collected from different parties independently.

The flow is:

1. **Create** -- First signer creates the PSBT with the transaction structure
2. **Collect** -- Pass the PSBT to other signers who add their signatures
3. **Finalize** -- Once M signatures are collected, finalize and broadcast

## Generate a Multisig Address

Before creating transactions, generate the multisig address where funds will be locked:

```typescript
import { P2TR_MS, P2MR_MS } from '@btc-vision/transaction';
import { networks } from '@btc-vision/bitcoin';

const pubkeys = [pubkeyA, pubkeyB, pubkeyC];  // Uint8Array[] of public keys

// Standard P2TR multisig address (bc1p...)
const p2trAddress = P2TR_MS.generateMultiSigAddress(
    pubkeys,
    2,                    // 2-of-3
    networks.bitcoin,
);

// Quantum-safe P2MR multisig address (bc1z...)
// Eliminates the key-path spend (no NUMS point needed)
const p2mrAddress = P2MR_MS.generateMultiSigAddress(
    pubkeys,
    2,                    // 2-of-3
    networks.bitcoin,
);
```

## Step 1: First Signer Creates the PSBT

```typescript
import {
    MultiSignTransaction,
    EcKeyPair,
    UTXO,
} from '@btc-vision/transaction';
import { networks } from '@btc-vision/bitcoin';

const network = networks.bitcoin;

// Three participants
const signerA = EcKeyPair.fromWIF(process.env.KEY_A!, network);
const signerB = EcKeyPair.fromWIF(process.env.KEY_B!, network);
const signerC = EcKeyPair.fromWIF(process.env.KEY_C!, network);

const pubkeys = [signerA.publicKey, signerB.publicKey, signerC.publicKey];

// UTXOs locked in the multisig address
const vaultUtxos: UTXO[] = [
    {
        transactionId: 'abcd1234...'.padEnd(64, '0'),
        outputIndex: 0,
        value: 200000n,
        scriptPubKey: {
            hex: '5120...',
            address: 'bc1p...multisigAddress',
        },
    },
];

// Create the multisig transaction
const multiSigTx = new MultiSignTransaction({
    network,
    utxos: vaultUtxos,
    feeRate: 10,                              // sat/vB
    pubkeys,
    minimumSignatures: 2,                      // 2-of-3
    receiver: 'bc1p...recipientAddress',       // Where to send funds
    requestedAmount: 100000n,                  // Amount in satoshis
    refundVault: 'bc1p...vaultAddress',        // Remaining funds go here
    // useP2MR: true,                          // Uncomment for quantum-safe P2MR
});

// Sign and get the PSBT
const psbt = await multiSigTx.signPSBT();

// Export as base64 for transport to other signers
const psbtBase64 = psbt.toBase64();
console.log('PSBT (send to next signer):', psbtBase64);
```

## Step 2: Second Signer Adds Their Signature

```typescript
import { MultiSignTransaction } from '@btc-vision/transaction';
import { Psbt } from '@btc-vision/bitcoin';

// Receive the PSBT from the first signer
const psbt2 = Psbt.fromBase64(psbtBase64, { network });

// Check if this signer has already signed (prevent duplicates)
const alreadySigned = MultiSignTransaction.verifyIfSigned(
    psbt2,
    signerB.publicKey,
);

if (!alreadySigned) {
    // Add signature
    const result = MultiSignTransaction.signPartial(
        psbt2,
        signerB,                // This signer's keypair
        0,                      // originalInputCount (inputs before multisig)
        [2],                    // minimums per input (need 2 signatures)
    );

    console.log('Signature added:', result.signed);
    console.log('Threshold reached:', result.final);

    if (result.final) {
        // 2-of-3 threshold reached -- finalize and broadcast
        const finalized = MultiSignTransaction.attemptFinalizeInputs(
            psbt2,
            0,                  // startIndex of multisig inputs
            [pubkeys],          // orderedPubKeys per input
            true,               // isFinal
        );

        if (finalized) {
            const tx = psbt2.extractTransaction();
            const txHex = tx.toHex();
            console.log('Broadcast this:', txHex);

            // Broadcast via provider
            // await provider.sendRawTransaction(txHex);
        }
    } else {
        // Need more signatures -- forward to next signer
        const updatedPsbt = psbt2.toBase64();
        console.log('Forward to next signer:', updatedPsbt);
    }
}
```

## Step 3: Third Signer (If Needed)

If the second signer did not reach the threshold, the same process repeats:

```typescript
const psbt3 = Psbt.fromBase64(updatedPsbtBase64, { network });

const result = MultiSignTransaction.signPartial(
    psbt3,
    signerC,
    0,
    [2],
);

if (result.final) {
    MultiSignTransaction.attemptFinalizeInputs(psbt3, 0, [pubkeys], true);
    const tx = psbt3.extractTransaction();
    await provider.sendRawTransaction(tx.toHex());
    console.log('Transaction broadcast!');
}
```

## Reconstruct from Base64

If you need to rebuild a `MultiSignTransaction` from a received PSBT:

```typescript
const multiSigTx = MultiSignTransaction.fromBase64({
    psbt: psbtBase64,
    network,
    utxos: vaultUtxos,
    feeRate: 10,
    pubkeys: [pubkeyA, pubkeyB, pubkeyC],
    minimumSignatures: 2,
    receiver: 'bc1p...recipient',
    requestedAmount: 100000n,
    refundVault: 'bc1p...vault',
});
```

## Key Static Methods

| Method | Purpose |
|--------|---------|
| `MultiSignTransaction.fromBase64()` | Reconstruct from PSBT base64 string |
| `MultiSignTransaction.signPartial()` | Add a partial signature from one signer |
| `MultiSignTransaction.verifyIfSigned()` | Check if a public key has already signed |
| `MultiSignTransaction.attemptFinalizeInputs()` | Finalize after collecting enough signatures |
| `MultiSignTransaction.dedupeSignatures()` | Merge signatures from different PSBT copies |

## Output Structure

The multisig transaction creates two outputs:

```
Multisig UTXOs (inputs)
    |
    +---> Receiver: requestedAmount
    |
    +---> Refund Vault: totalInputValue - requestedAmount
```

The refund vault receives any remaining funds after the requested amount is sent to the receiver.

## Best Practices

1. **Consistent key ordering.** All signers must use the same `pubkeys` array order when constructing or reconstructing the transaction.

2. **Verify before forwarding.** Use `verifyIfSigned()` to prevent a signer from accidentally signing twice.

3. **Use base64 for transport.** PSBT base64 is compact and safe for transmission between signers (email, encrypted message, QR code).

4. **Check `result.final` after each signature.** Broadcast as soon as the threshold is met -- do not collect unnecessary extra signatures.

5. **Consider P2MR for quantum safety.** Set `useP2MR: true` to use P2MR (BIP 360) outputs instead of P2TR. P2MR eliminates the quantum-vulnerable internal pubkey.

6. **Validate the refund amount.** Ensure `requestedAmount` does not exceed total UTXO value to avoid negative refund.

## References

- [Multisig Transactions](../docs/transaction/transaction-building/multisig-transactions.md) -- Full API reference
- [Offline Transaction Signing](../docs/transaction/offline/offline-transaction-signing.md) -- Multisig offline workflow
- [Transaction Factory](../docs/transaction/transaction-building/transaction-factory.md) -- Other transaction types
