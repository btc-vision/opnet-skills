# How to Upgrade OPNet Smart Contracts

OPNet supports native bytecode replacement -- no proxy patterns needed. When a contract upgrades, its address and storage persist, but the execution logic changes. This guide covers the `Upgradeable` base class, the `UpgradeablePlugin`, the `onUpdate` lifecycle hook, and storage migration patterns.

## Two Approaches

| Approach | When to Use |
|----------|-------------|
| **Extend `Upgradeable`** | Your contract does not already extend another base class |
| **Register `UpgradeablePlugin`** | Your contract extends `OP20`, `OP721`, or another base class |

## Approach 1: Extending Upgradeable

If your contract's primary base class is `OP_NET`, switch to extending `Upgradeable` instead:

```typescript
import {
    Upgradeable,
    Calldata,
    BytesWriter,
    encodeSelector,
    Selector,
    ADDRESS_BYTE_LENGTH,
} from '@btc-vision/btc-runtime/runtime';

@final
export class MyContract extends Upgradeable {
    // Timelock: 144 blocks = ~24 hours
    protected readonly upgradeDelay: u64 = 144;

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

            // Your custom methods here
            case encodeSelector('myMethod'):
                return this.myMethod(calldata);

            default:
                return super.execute(method, calldata);
        }
    }

    private myMethod(calldata: Calldata): BytesWriter {
        // Business logic
        return new BytesWriter(0);
    }
}
```

## Approach 2: Using the UpgradeablePlugin

If you already extend `OP20` or `OP721`, use the plugin approach -- no changes to `execute()` needed:

```typescript
import {
    OP20,
    UpgradeablePlugin,
} from '@btc-vision/btc-runtime/runtime';

@final
export class MyToken extends OP20 {
    public constructor() {
        super();
        // Register the plugin -- upgrade methods are handled automatically
        this.registerPlugin(new UpgradeablePlugin(144)); // 144 blocks = ~24 hours
    }

    // No need to modify execute() -- the plugin handles:
    // - submitUpgrade(address)
    // - applyUpgrade(address)
    // - cancelUpgrade()
    // - pendingUpgrade()
    // - upgradeDelay()
}
```

The plugin works because when your contract's `execute()` falls through to `super.execute()`, the base `OP_NET` class checks all registered plugins before throwing "Method not found".

## The Upgrade Workflow

```
Step 1: Deploy the new contract version as a separate contract
        -> Returns: newContractAddress

Step 2: Call submitUpgrade(newContractAddress)
        -> Starts the timelock countdown
        -> Emits: UpgradeSubmitted event

Step 3: Wait for the delay period (e.g., 144 blocks = ~24 hours)
        -> Users can monitor pending upgrades and exit if they distrust the change

Step 4: Call applyUpgrade(newContractAddress, migrationCalldata)
        -> VM replaces bytecode
        -> Calls onUpdate() on the new bytecode
        -> Emits: UpgradeApplied event
        -> New bytecode takes effect at the next block

Step 5 (optional): Call cancelUpgrade() to abort a pending upgrade
```

## Recommended Delay Values

| Contract Type | Blocks | Approximate Time |
|---------------|--------|------------------|
| Test / Development | 1-6 | Minutes |
| Standard DeFi | 144 | ~24 hours |
| High-value vaults | 1008 | ~1 week |
| Governance contracts | 4320 | ~1 month |

## The onUpdate Lifecycle Hook

When bytecode is replaced, the VM calls `onUpdate()` on the **new** contract version. This is where you perform storage migrations and initialize new fields.

### Basic onUpdate

```typescript
@final
export class MyContractV2 extends Upgradeable {
    protected readonly upgradeDelay: u64 = 144;

    // New storage added in V2
    private newFeaturePointer: u16 = Blockchain.nextPointer;
    private _newFeature: StoredU256;

    public constructor() {
        super();
        this._newFeature = new StoredU256(this.newFeaturePointer, EMPTY_POINTER);
    }

    public override onUpdate(calldata: Calldata): void {
        super.onUpdate(calldata);  // Always call super (notifies plugins)

        // Initialize new storage with a default value
        if (this._newFeature.value === u256.Zero) {
            this._newFeature.value = u256.fromU64(100);
        }
    }

    // ... execute() and other methods
}
```

### Version-Based Migrations

For contracts that may skip versions, pass a version number in the calldata:

```typescript
public override onUpdate(calldata: Calldata): void {
    super.onUpdate(calldata);

    // Read the version we are migrating FROM
    const fromVersion = calldata.readU64();

    if (fromVersion === 1) {
        this.migrateFromV1();
    } else if (fromVersion === 2) {
        this.migrateFromV2();
    }
}

private migrateFromV1(): void {
    // Migration from V1 to V3
    this._newFeatureA.value = u256.fromU64(100);
    this._newFeatureB.value = u256.fromU64(200);
}

private migrateFromV2(): void {
    // Migration from V2 to V3
    this._newFeatureB.value = u256.fromU64(200);
}
```

Then pass the version when calling `applyUpgrade`:

```typescript
// From the upgrade transaction calldata:
// applyUpgrade(newAddress, migrationCalldata)
// where migrationCalldata contains: u64(1)  -- "from version 1"
```

## Storage Compatibility Rules

Storage layout compatibility is YOUR responsibility. The VM does not validate or migrate storage.

### What Persists Across Upgrades

- Contract address (unchanged)
- All storage slots (unchanged)
- Contract deployer identity

### What Changes

- Execution logic (bytecode only)

### Storage Pointer Rules

```typescript
// V1 -- Original contract
class MyContractV1 extends Upgradeable {
    private balancePointer: u16 = Blockchain.nextPointer;      // Pointer 1
    private allowancePointer: u16 = Blockchain.nextPointer;    // Pointer 2
}

// V2 -- CORRECT: Add new pointers at the END
class MyContractV2 extends Upgradeable {
    private balancePointer: u16 = Blockchain.nextPointer;      // Pointer 1 (same)
    private allowancePointer: u16 = Blockchain.nextPointer;    // Pointer 2 (same)
    private newFeaturePointer: u16 = Blockchain.nextPointer;   // Pointer 3 (NEW)
}

// V2 -- WRONG: Changing order BREAKS storage!
class MyContractV2Bad extends Upgradeable {
    private newFeaturePointer: u16 = Blockchain.nextPointer;   // Pointer 1 (was balance!)
    private balancePointer: u16 = Blockchain.nextPointer;      // Pointer 2 (was allowance!)
    private allowancePointer: u16 = Blockchain.nextPointer;    // Pointer 3 (new slot)
}
```

**Rules:**
1. Never remove or reorder existing pointers
2. Always add new pointers at the end
3. Document pointer assignments with comments
4. Test upgrades thoroughly on testnet/regtest first

## Monitoring Upgrades

Add view methods so users can check upgrade status:

```typescript
case encodeSelector('getPendingUpgrade'):
    return this.getPendingUpgradeInfo();
case encodeSelector('getUpgradeStatus'):
    return this.getUpgradeStatusInfo();

// ...

private getPendingUpgradeInfo(): BytesWriter {
    const response = new BytesWriter(32);
    response.writeAddress(this.pendingUpgradeAddress);
    return response;
}

private getUpgradeStatusInfo(): BytesWriter {
    const response = new BytesWriter(17);
    response.writeBoolean(this.hasPendingUpgrade);
    response.writeU64(this.pendingUpgradeBlock);
    response.writeU64(this.upgradeEffectiveBlock);
    return response;
}
```

## Upgrade Events

The `Upgradeable` base class emits these events automatically:

| Event | When | Data |
|-------|------|------|
| `UpgradeSubmitted` | `submitUpgrade()` called | sourceAddress, submitBlock, effectiveBlock |
| `UpgradeApplied` | `applyUpgrade()` called | sourceAddress, appliedAtBlock |
| `UpgradeCancelled` | `cancelUpgrade()` called | sourceAddress, cancelledAtBlock |

## Security Considerations

1. **Only the deployer can upgrade.** Both `submitUpgrade` and `applyUpgrade` check `onlyDeployer`.

2. **Source must be a deployed contract.** `submitUpgrade` validates that the source address is an existing contract, preventing last-minute malicious deployments.

3. **Address must match.** `applyUpgrade` requires the address parameter to match the pending upgrade, preventing front-running substitution attacks.

4. **Activation boundary.** Transactions in the same block as `applyUpgrade` execute against old bytecode. New bytecode takes effect at the next block.

## Comparison with Ethereum

| Feature | Ethereum (UUPS Proxy) | OPNet (Upgradeable) |
|---------|----------------------|---------------------|
| Mechanism | delegatecall to implementation | Native VM bytecode replacement |
| Storage | Proxy storage, collision risk | Same contract, no collision |
| Proxy overhead | Yes | None |
| Timelock | Separate contract (optional) | Built-in |
| Cancel upgrade | Custom implementation | Built-in |
| Complexity | High (proxy patterns) | Low (single VM opcode) |

## References

- [Upgradeable Base Class](../docs/btc-runtime/contracts/upgradeable.md) -- Full API and class reference
- [Contract Upgrades Guide](../docs/btc-runtime/advanced/contract-upgrades.md) -- In-depth mechanics and examples
- [Plugins](../docs/btc-runtime/advanced/plugins.md) -- Plugin system details
