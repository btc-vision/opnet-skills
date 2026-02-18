# How to Sign Messages on OPNet

OPNet supports three signature schemes: Schnorr (BIP340), Taproot-tweaked Schnorr, and quantum-resistant ML-DSA (FIPS 204). The `MessageSigner` singleton provides a unified API that works across browser and backend environments.

## Three Signing Approaches

### 1. Auto Methods (RECOMMENDED)

Auto methods detect whether you are in a browser (with OP_WALLET extension) or backend (with local keypair) and delegate accordingly. Always use these unless you have a specific reason not to.

```typescript
import { MessageSigner } from '@btc-vision/transaction';

// Schnorr signing
// Browser: omit keypair -> OP_WALLET signs
const schnorrSigned = await MessageSigner.signMessageAuto('Hello, OPNet!');

// Backend: provide keypair -> local signing
const schnorrSigned = await MessageSigner.signMessageAuto('Hello, OPNet!', keypair);

// Taproot-tweaked Schnorr signing
// Browser: OP_WALLET handles tweaking internally
const tweakedSigned = await MessageSigner.tweakAndSignMessageAuto('Taproot message');

// Backend: keypair + network required
const tweakedSigned = await MessageSigner.tweakAndSignMessageAuto(
    'Taproot message',
    keypair,
    network,
);

// ML-DSA (quantum-resistant) signing
// Browser: OP_WALLET handles ML-DSA
const mldsaSigned = await MessageSigner.signMLDSAMessageAuto('Quantum message');

// Backend: provide ML-DSA keypair
const mldsaSigned = await MessageSigner.signMLDSAMessageAuto(
    'Quantum message',
    wallet.mldsaKeypair,
);
```

**Decision flow:**

| Scenario | keypair parameter | What happens |
|----------|-------------------|--------------|
| Browser with OP_WALLET | Omitted | OP_WALLET signs via extension |
| Backend with keypair | Provided | Local signing with private key |
| Browser without OP_WALLET | Omitted | Throws clear error |

### 2. Contract-Side Verification

Inside a smart contract (AssemblyScript), use `Blockchain.verifySignature()` for consensus-aware verification:

```typescript
import { Blockchain } from '@btc-vision/btc-runtime/runtime';

// Consensus-aware: uses Schnorr now, auto-switches to ML-DSA after quantum deadline
const isValid: bool = Blockchain.verifySignature(
    Blockchain.tx.origin,  // ExtendedAddress (has both key types)
    signature,              // Signature bytes
    messageHash,            // 32-byte SHA256 hash
    false,                  // false = auto, true = force ML-DSA
);

// Force quantum-resistant verification (always ML-DSA)
const isValidQuantum: bool = Blockchain.verifySignature(
    Blockchain.tx.origin,
    signature,
    messageHash,
    true,  // Force ML-DSA regardless of consensus flags
);
```

**Important:** The first parameter must be an `ExtendedAddress` (not a plain `Address`). Use `Blockchain.tx.origin` which contains both:
- `tweakedPublicKey` (32 bytes) for Schnorr/Taproot
- `mldsaPublicKey` (1,312 bytes for Level2) for quantum-resistant ML-DSA

### 3. Direct ECDSA/Schnorr Methods (DEPRECATED)

These low-level methods work only in backend environments and will break when the quantum consensus flag flips. Avoid them.

```typescript
// DEPRECATED -- use signMessageAuto() instead
const signed = MessageSigner.signMessage(keypair, message);

// DEPRECATED -- use tweakAndSignMessageAuto() instead
const signed = MessageSigner.tweakAndSignMessage(keypair, message, network);

// DEPRECATED -- use signMLDSAMessageAuto() instead
const signed = MessageSigner.signMLDSAMessage(mldsaKeypair, message);
```

## Frontend Example (Browser with OP_WALLET)

```typescript
import { MessageSigner } from '@btc-vision/transaction';

async function signAndSubmit() {
    // Check wallet availability
    if (!MessageSigner.isOPWalletAvailable()) {
        alert('Please install the OP_WALLET extension');
        return;
    }

    // Sign a challenge message (OP_WALLET prompts the user)
    const signed = await MessageSigner.signMessageAuto('Authenticate to MyDApp');

    console.log('Signature:', signed.signature);   // 64-byte Uint8Array
    console.log('Message hash:', signed.message);   // 32-byte SHA256

    // For quantum-resistant signing
    const quantumSigned = await MessageSigner.signMLDSAMessageAuto(
        'Quantum-safe authentication',
    );

    console.log('ML-DSA signature size:', quantumSigned.signature.length);  // 2420 bytes
    console.log('ML-DSA public key:', quantumSigned.publicKey);
    console.log('Security level:', quantumSigned.securityLevel);
}
```

## Backend Example (Node.js with Local Keypair)

```typescript
import {
    MessageSigner,
    EcKeyPair,
    Mnemonic,
    MLDSASecurityLevel,
    QuantumBIP32Factory,
} from '@btc-vision/transaction';
import { networks, toHex } from '@btc-vision/bitcoin';

const network = networks.bitcoin;
const securityLevel = MLDSASecurityLevel.LEVEL2;

// Generate or load a wallet
const mnemonic = Mnemonic.generate(undefined, '', network, securityLevel);
const wallet = mnemonic.derive(0);

// --- Schnorr signing ---
const message = 'Backend authentication';
const schnorrSigned = MessageSigner.signMessage(wallet.keypair, message);
console.log('Schnorr signature:', toHex(schnorrSigned.signature));

// Verify Schnorr
const schnorrValid = MessageSigner.verifySignature(
    wallet.keypair.publicKey,  // Pass the original (untweaked) public key
    message,                    // Original message (not hash)
    schnorrSigned.signature,
);
console.log('Schnorr valid:', schnorrValid);  // true

// --- Tweaked Schnorr signing ---
const tweakedSigned = MessageSigner.tweakAndSignMessage(wallet.keypair, message, network);

// Verify tweaked (pass the UNTWEAKED key -- method tweaks internally)
const tweakedValid = MessageSigner.tweakAndVerifySignature(
    wallet.keypair.publicKey,
    message,
    tweakedSigned.signature,
);
console.log('Tweaked valid:', tweakedValid);  // true

// --- ML-DSA signing ---
const quantumSigned = MessageSigner.signMLDSAMessage(wallet.mldsaKeypair, message);
console.log('ML-DSA signature size:', quantumSigned.signature.length);  // 2420 bytes

// Verify ML-DSA with original keypair
const mldsaValid = MessageSigner.verifyMLDSASignature(
    wallet.mldsaKeypair,
    message,
    quantumSigned.signature,
);
console.log('ML-DSA valid:', mldsaValid);  // true

// Verify ML-DSA with public-key-only reconstruction (for remote verification)
const publicKeyOnly = QuantumBIP32Factory.fromPublicKey(
    quantumSigned.publicKey,
    wallet.chainCode,
    network,
    securityLevel,
);

const remoteValid = MessageSigner.verifyMLDSASignature(
    publicKeyOnly,
    message,
    quantumSigned.signature,
);
console.log('Remote ML-DSA valid:', remoteValid);  // true
```

## Universal Code Pattern

Write code that works in both browser and backend without modification:

```typescript
import { MessageSigner } from '@btc-vision/transaction';
import type { UniversalSigner } from '@btc-vision/ecpair';
import type { QuantumBIP32Interface } from '@btc-vision/transaction';

async function signChallenge(
    challenge: string,
    keypair?: UniversalSigner,
    mldsaKeypair?: QuantumBIP32Interface,
) {
    // Schnorr signature (works in both environments)
    const schnorr = await MessageSigner.signMessageAuto(challenge, keypair);

    // ML-DSA signature (works in both environments)
    const quantum = await MessageSigner.signMLDSAMessageAuto(challenge, mldsaKeypair);

    return { schnorr, quantum };
}

// Browser usage (OP_WALLET handles everything):
// const result = await signChallenge('my-challenge');

// Backend usage (provide keypairs):
// const result = await signChallenge('my-challenge', wallet.keypair, wallet.mldsaKeypair);
```

## Verification Methods Summary

| Method | Environment | Input | Returns |
|--------|-------------|-------|---------|
| `MessageSigner.verifySignature()` | Browser/Backend | publicKey, message, signature | `boolean` |
| `MessageSigner.tweakAndVerifySignature()` | Browser/Backend | untweakedPublicKey, message, signature | `boolean` |
| `MessageSigner.verifyMLDSASignature()` | Browser/Backend | keypairObject, message, signature | `boolean` |
| `MessageSigner.verifyMLDSAWithOPWallet()` | Browser only | message, MLDSASignedMessage | `Promise<boolean \| null>` |
| `Blockchain.verifySignature()` | Contract only | ExtendedAddress, signature, hash, forceMLDSA | `bool` |

## Common Mistakes

1. **Forgetting `await` on Auto methods** -- they return Promises, not direct values
2. **Passing already-tweaked key to `tweakAndVerifySignature`** -- it tweaks internally, so pass the original key
3. **Omitting `network` for tweaked backend signing** -- `tweakAndSignMessageAuto(msg, keypair)` throws; must be `tweakAndSignMessageAuto(msg, keypair, network)`
4. **Pre-hashing the message** -- all verification methods hash internally with SHA-256; pass the original message
5. **Mismatched ML-DSA security levels** -- the level used for `QuantumBIP32Factory.fromPublicKey()` must match the signing level

## References

- [MessageSigner API](../docs/transaction/keypair/message-signer.md) -- Complete API reference with all methods
- [Quantum Message Signing Guide](../docs/transaction/quantum-support/04-message-signing.md) -- ML-DSA signing details
- [Signature Verification (Contract)](../docs/btc-runtime/advanced/signature-verification.md) -- In-contract verification
