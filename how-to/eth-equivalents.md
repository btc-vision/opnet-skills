# Ethereum to OPNet Feature Mapping

This guide maps common Ethereum/Solidity patterns to their OPNet equivalents. OPNet smart contracts are written in AssemblyScript (a TypeScript-like language that compiles to WASM) and run on Bitcoin L1.

## Quick Reference Table

| Ethereum Feature | OPNet Equivalent | Notes |
|------------------|------------------|-------|
| ERC-20 | OP20 | Use `increaseAllowance` instead of `approve` |
| ERC-721 | OP721 | Same general interface, AssemblyScript syntax |
| `msg.sender` | `Blockchain.tx.sender` | ML-DSA (OPNet) address, 32 bytes |
| `tx.origin` | `Blockchain.tx.origin` | ExtendedAddress (tweaked public key) |
| `ecrecover()` | `Blockchain.verifySignature()` | Supports Schnorr + ML-DSA, consensus-aware |
| `CREATE` / `CREATE2` | Deploy separately, link via stored addresses | No in-contract deployment |
| `selfdestruct` | Not available | Contracts cannot be destroyed |
| Solidity | AssemblyScript | Custom fork with closure support |
| `keccak256()` | `sha256()` (preferred) or Keccak256 available | SHA256 is cheaper in the VM |
| ETH balance / `msg.value` | Verify Bitcoin outputs via `Blockchain.tx.outputs` | Contracts cannot hold BTC |
| ReentrancyGuard | `ReentrancyGuard` base class | All methods protected by default |
| `block.timestamp` | `Blockchain.block.number` (use block height, NOT medianTimestamp -- miners can manipulate MTP) | Bitcoin block height is strictly monotonic and tamper-proof |
| `block.number` | `Blockchain.block.number` | Bitcoin block height |
| Proxy upgrade (UUPS) | `Upgradeable` base class / `UpgradeablePlugin` | Native bytecode replacement, no proxy |
| `require()` / `revert()` | `throw new Revert('message')` | AssemblyScript error handling |
| `mapping(address => uint)` | `AddressMemoryMap` | Pointer-based storage |
| `uint256` | `u256` (from `@btc-vision/as-bignum`) | 256-bit unsigned integer |
| Events (`emit`) | `this.emitEvent(new MyEvent(...))` | Extend `NetEvent` class |
| Modifiers | Regular function calls | No modifier syntax in AssemblyScript |
| `abi.encode()` | `BytesWriter` | Manual serialization |
| `abi.decode()` | `Calldata` reader methods | Manual deserialization |

> **CRITICAL: Never use `medianTimestamp` for time-dependent contract logic.** Bitcoin's Median Time Past (MTP) can be manipulated by miners within a +/- 2 hour window. Always use `Blockchain.block.number` (block height) which is strictly monotonic and tamper-proof. The actual btc-runtime contracts (OP20, OP721, OP20S, Upgradeable) ALL use `block.number` for deadlines.

## Detailed Comparisons

### Token Standards: ERC-20 vs OP20

```solidity
// Solidity ERC-20
contract MyToken is ERC20 {
    constructor() ERC20("MyToken", "MTK") {
        _mint(msg.sender, 1000000 * 10**18);
    }
}
```

```typescript
// OPNet OP20
import { OP20, OP20InitParameters, Blockchain } from '@btc-vision/btc-runtime/runtime';
import { u256 } from '@btc-vision/as-bignum/assembly';

@final
export class MyToken extends OP20 {
    public override onDeployment(calldata: Calldata): void {
        this.instantiate(new OP20InitParameters(
            u256.fromU64(1_000_000),  // Max supply
            18,                        // Decimals
            'MyToken',
            'MTK',
        ));

        this._mint(Blockchain.tx.sender, u256.fromU64(1_000_000));
    }
}
```

**Key difference:** OPNet uses `increaseAllowance` / `decreaseAllowance` instead of `approve`. This avoids the well-known ERC-20 approve race condition.

### Sender Identity: msg.sender vs Blockchain.tx.sender

On Ethereum, `msg.sender` is a single 20-byte address. On OPNet, there are two identities per transaction:

| | Ethereum | OPNet |
|---|---|---|
| **Smart contract identity** | `msg.sender` (20 bytes) | `Blockchain.tx.sender` (32 bytes, ML-DSA public key hash) |
| **Bitcoin/signing identity** | N/A | `Blockchain.tx.origin` (ExtendedAddress with tweaked pubkey) |
| **Type** | `address` | `Address` / `ExtendedAddress` |

```typescript
// OPNet contract
const caller: Address = Blockchain.tx.sender;          // ML-DSA address (OPNet identity)
const origin: ExtendedAddress = Blockchain.tx.origin;  // Bitcoin identity (tweaked pubkey)
```

### Signature Verification: ecrecover vs verifySignature

```solidity
// Solidity -- ecrecover (complex, error-prone)
function verify(bytes32 hash, uint8 v, bytes32 r, bytes32 s) public pure returns (address) {
    address recovered = ecrecover(hash, v, r, s);
    require(recovered != address(0), "Invalid signature");
    return recovered;
}
```

```typescript
// OPNet -- verifySignature (simple, safe, quantum-ready)
const isValid = Blockchain.verifySignature(
    Blockchain.tx.origin,  // ExtendedAddress (auto-loads public key)
    signature,              // Full signature bytes (no v, r, s splitting)
    messageHash,            // 32-byte message hash
    true,                   // Force ML-DSA for quantum resistance
);
```

**Advantages of OPNet approach:**
- No v, r, s splitting -- single signature parameter
- Automatic public key loading from address
- Quantum-resistant ML-DSA option
- No silent failures (returns `false`, never `address(0)`)
- No signature malleability

### Contract Deployment: CREATE vs Separate Deploy

Ethereum allows contracts to deploy other contracts via `CREATE` / `CREATE2`. OPNet does not support in-contract deployment. Instead:

1. Deploy contracts separately as independent transactions
2. Store the deployed contract's address in your contract
3. Use cross-contract calls to interact

```typescript
// OPNet -- store linked contract addresses
private oraclePointer: u16 = Blockchain.nextPointer;
private _oracleAddress: StoredAddress;

public constructor() {
    super();
    this._oracleAddress = new StoredAddress(this.oraclePointer, Address.zero());
}

// Admin sets the oracle address after deployment
public setOracle(calldata: Calldata): BytesWriter {
    this.onlyDeployer(Blockchain.tx.sender);
    this._oracleAddress.value = calldata.readAddress();
    return new BytesWriter(0);
}
```

### Reentrancy Protection

```solidity
// Solidity -- OpenZeppelin ReentrancyGuard
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract MyVault is ReentrancyGuard {
    function withdraw() external nonReentrant {
        // Only this function is protected
    }

    function deposit() external {
        // NOT protected unless you add nonReentrant
    }
}
```

```typescript
// OPNet -- ReentrancyGuard base class
import { ReentrancyGuard, ReentrancyLevel } from '@btc-vision/btc-runtime/runtime';

@final
export class MyVault extends ReentrancyGuard {
    protected readonly reentrancyLevel: ReentrancyLevel = ReentrancyLevel.STANDARD;

    public constructor() {
        super();
    }

    // ALL methods are protected by default (opt-out, not opt-in)
    public withdraw(calldata: Calldata): BytesWriter { /* protected */ }
    public deposit(calldata: Calldata): BytesWriter { /* also protected */ }

    // Exclude read-only methods if desired
    protected override isSelectorExcluded(selector: Selector): boolean {
        if (selector === encodeSelector('balanceOf')) return true;
        return super.isSelectorExcluded(selector);
    }
}
```

**Key difference:** OPNet protects ALL methods by default (opt-out via `isSelectorExcluded`). Solidity requires you to add `nonReentrant` to each function (opt-in).

### ETH Balance vs Bitcoin Outputs

Ethereum contracts can hold ETH and check `msg.value`. OPNet contracts **cannot hold BTC**. They use a verify-don't-custody pattern:

```typescript
// OPNet -- verify Bitcoin outputs instead of holding BTC
// Check that the transaction includes the expected BTC payment
const outputs = Blockchain.tx.outputs;
for (let i = 0; i < outputs.length; i++) {
    const output = outputs[i];
    // Verify payment was sent to the expected address
    if (output.address.equals(expectedRecipient) && output.value >= requiredAmount) {
        // Payment verified -- proceed with contract logic
    }
}
```

### Contract Upgrades: Proxy vs Native Replacement

```solidity
// Solidity -- UUPS Proxy pattern (complex)
import "@openzeppelin/contracts/proxy/utils/UUPSUpgradeable.sol";

contract MyContractV1 is UUPSUpgradeable {
    function _authorizeUpgrade(address) internal override onlyOwner {}
}
```

```typescript
// OPNet -- Native bytecode replacement (simple)
import { Upgradeable } from '@btc-vision/btc-runtime/runtime';

@final
export class MyContract extends Upgradeable {
    protected readonly upgradeDelay: u64 = 144; // ~24 hours timelock

    public override execute(method: Selector, calldata: Calldata): BytesWriter {
        switch (method) {
            case encodeSelector('submitUpgrade'):
                return this.submitUpgrade(calldata.readAddress());
            case encodeSelector('applyUpgrade'): {
                const sourceAddress = calldata.readAddress();
                const remainingLength = calldata.byteLength - ADDRESS_BYTE_LENGTH;
                const updateCalldata = new BytesWriter(remainingLength);
                if (remainingLength > 0) {
                    updateCalldata.writeBytes(calldata.readBytes(remainingLength));
                }
                return this.applyUpgrade(sourceAddress, updateCalldata);
            }
            case encodeSelector('cancelUpgrade'):
                return this.cancelUpgrade();
            default:
                return super.execute(method, calldata);
        }
    }
}
```

**No proxy needed.** OPNet replaces bytecode natively via a VM opcode. Storage persists across upgrades.

### Hash Functions

```solidity
// Solidity
bytes32 hash = keccak256(abi.encodePacked(data));
```

```typescript
// OPNet -- SHA256 (preferred, cheaper in the VM)
import { sha256 } from '@btc-vision/btc-runtime/runtime';

const hash = sha256(data);  // Returns Uint8Array (32 bytes)
```

Keccak256 is also available in the VM but SHA256 is the standard choice on OPNet since it aligns with Bitcoin's native hash function.

### Events

```solidity
// Solidity
event Transfer(address indexed from, address indexed to, uint256 value);
emit Transfer(msg.sender, recipient, amount);
```

```typescript
// OPNet
class TransferEvent extends NetEvent {
    constructor(
        public readonly from: Address,
        public readonly to: Address,
        public readonly value: u256,
    ) {
        super('Transfer');
    }

    protected override encodeData(writer: BytesWriter): void {
        writer.writeAddress(this.from);
        writer.writeAddress(this.to);
        writer.writeU256(this.value);
    }
}

// Emit
this.emitEvent(new TransferEvent(from, to, amount));
```

## Things That Do Not Exist on OPNet

| Ethereum Feature | OPNet Status |
|------------------|--------------|
| `selfdestruct` | Not available |
| `delegatecall` | Not available (upgrades use bytecode replacement) |
| `CREATE` / `CREATE2` | Deploy separately |
| Receive/fallback functions | Not applicable |
| `msg.value` (native token in call) | Verify Bitcoin outputs instead |
| Gas refunds (SSTORE) | Not applicable |
| `payable` modifier | Not applicable |
| Assembly/Yul | WASM is the execution target |
| `Buffer` | Removed -- use `Uint8Array` everywhere |

## References

- [ReentrancyGuard](../docs/btc-runtime/contracts/reentrancy-guard.md) -- Reentrancy protection details
- [Upgradeable Contracts](../docs/btc-runtime/contracts/upgradeable.md) -- Upgrade mechanism
- [Signature Verification](../docs/btc-runtime/advanced/signature-verification.md) -- Full comparison with ecrecover
- [OP20 API](../docs/btc-runtime/api-reference/op20.md) -- Token standard reference
- [Blockchain Environment](../docs/btc-runtime/core-concepts/blockchain-environment.md) -- Transaction context
