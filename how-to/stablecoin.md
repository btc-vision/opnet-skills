# How to Build a Stablecoin on OPNet

This guide shows how to build a USDC-style stablecoin on OPNet by extending the OP20 base class with role-based access control, pausability, blacklisting, and minter allowances.

## Overview

A stablecoin on OPNet extends `OP20` and adds:
- **Role-based access control** using bit flags (Admin, Minter, Pauser, Blacklister)
- **Pausable transfers** to freeze all operations in emergencies
- **Address blacklisting** to comply with regulations
- **Minter allowances** to cap how much each minter can create
- **Collateral verification** via Bitcoin transaction outputs

## Step 1: Define Roles as Bit Flags

Use powers of 2 so multiple roles can be stored in a single `u256` per address:

```typescript
// Roles -- MUST be powers of 2 for bitwise operations
enum Role {
    ADMIN = 1,        // 2^0 = 0001
    MINTER = 2,       // 2^1 = 0010
    PAUSER = 4,       // 2^2 = 0100
    BLACKLISTER = 8,  // 2^3 = 1000
}
```

A single `AddressMemoryMap` stores all roles per address. An account with Admin + Minter has the value `3` (binary: `0011`).

```typescript
// Check role using bitwise AND
public hasRole(account: Address, role: u256): bool {
    const roles = this._roles.get(account);
    return !SafeMath.and(roles, role).isZero();
}

// Grant role using bitwise OR
private _grantRole(account: Address, role: u256): void {
    const currentRoles = this._roles.get(account);
    const newRoles = SafeMath.or(currentRoles, role);
    this._roles.set(account, newRoles);
}

// Revoke role using bitwise AND with inverted mask
private _revokeRole(account: Address, role: u256): void {
    const currentRoles = this._roles.get(account);
    const invertedRole = SafeMath.xor(role, u256.Max);
    const newRoles = SafeMath.and(currentRoles, invertedRole);
    this._roles.set(account, newRoles);
}
```

## Step 2: Implement the Stablecoin Contract

```typescript
import { u256 } from '@btc-vision/as-bignum/assembly';
import {
    OP20,
    OP20InitParameters,
    Blockchain,
    Address,
    Calldata,
    BytesWriter,
    SafeMath,
    Revert,
    NetEvent,
    StoredBoolean,
    StoredAddress,
    AddressMemoryMap,
    ABIDataTypes,
} from '@btc-vision/btc-runtime/runtime';

@final
export class Stablecoin extends OP20 {
    // Storage pointers -- never reorder these across upgrades
    private rolesPointer: u16 = Blockchain.nextPointer;
    private masterMinterPointer: u16 = Blockchain.nextPointer;
    private pausedPointer: u16 = Blockchain.nextPointer;
    private blacklistPointer: u16 = Blockchain.nextPointer;
    private minterAllowancePointer: u16 = Blockchain.nextPointer;

    // Stored values
    private _roles: AddressMemoryMap;
    private _masterMinter: StoredAddress;
    private _paused: StoredBoolean;
    private _blacklist: AddressMemoryMap;
    private _minterAllowance: AddressMemoryMap;

    public constructor() {
        super();
        this._roles = new AddressMemoryMap(this.rolesPointer);
        this._masterMinter = new StoredAddress(this.masterMinterPointer, Address.zero());
        this._paused = new StoredBoolean(this.pausedPointer, false);
        this._blacklist = new AddressMemoryMap(this.blacklistPointer);
        this._minterAllowance = new AddressMemoryMap(this.minterAllowancePointer);
    }

    public override onDeployment(calldata: Calldata): void {
        const name = calldata.readString();
        const symbol = calldata.readString();
        const admin = calldata.readAddress();
        const masterMinter = calldata.readAddress();

        // Initialize: no max supply, 6 decimals (USDC-style)
        this.instantiate(new OP20InitParameters(
            u256.Max,  // No max supply
            6,         // 6 decimals
            name,
            symbol,
        ));

        // Set up initial roles
        this._grantRole(admin, u256.fromU64(Role.ADMIN));
        this._grantRole(admin, u256.fromU64(Role.PAUSER));
        this._grantRole(admin, u256.fromU64(Role.BLACKLISTER));
        this._masterMinter.value = masterMinter;
    }

    // ... role management, minting, pausing, blacklisting methods
}
```

## Step 3: Controlled Minting with Allowances

Each minter has a limited supply cap. The master minter configures allowances:

```typescript
@method(
    { name: 'minter', type: ABIDataTypes.ADDRESS },
    { name: 'allowance', type: ABIDataTypes.UINT256 },
)
@returns({ name: 'success', type: ABIDataTypes.BOOL })
public configureMinter(calldata: Calldata): BytesWriter {
    this.onlyMasterMinter();

    const minter = calldata.readAddress();
    const allowance = calldata.readU256();

    // Grant minter role if new
    if (!this.hasRole(minter, u256.fromU64(Role.MINTER))) {
        this._grantRole(minter, u256.fromU64(Role.MINTER));
    }

    this._minterAllowance.set(minter, allowance);
    return new BytesWriter(0);
}

@method(
    { name: 'to', type: ABIDataTypes.ADDRESS },
    { name: 'amount', type: ABIDataTypes.UINT256 },
)
@returns({ name: 'success', type: ABIDataTypes.BOOL })
@emit('Mint')
public mint(calldata: Calldata): BytesWriter {
    this.onlyRole(u256.fromU64(Role.MINTER));
    this.whenNotPaused();

    const to = calldata.readAddress();
    const amount = calldata.readU256();
    const minter = Blockchain.tx.sender;

    this.notBlacklisted(to);
    this.notBlacklisted(minter);

    // Check and deduct allowance
    const allowance = this._minterAllowance.get(minter);
    if (allowance < amount) {
        throw new Revert('Minter allowance exceeded');
    }
    this._minterAllowance.set(minter, SafeMath.sub(allowance, amount));

    this._mint(to, amount);
    return new BytesWriter(0);
}
```

## Step 4: Pausable Transfers

```typescript
private whenNotPaused(): void {
    if (this._paused.value) {
        throw new Revert('Pausable: paused');
    }
}

@method()
@returns({ name: 'success', type: ABIDataTypes.BOOL })
@emit('Paused')
public pause(_calldata: Calldata): BytesWriter {
    this.onlyRole(u256.fromU64(Role.PAUSER));
    this._paused.value = true;
    return new BytesWriter(0);
}

@method()
@returns({ name: 'success', type: ABIDataTypes.BOOL })
@emit('Unpaused')
public unpause(_calldata: Calldata): BytesWriter {
    this.onlyRole(u256.fromU64(Role.PAUSER));
    this._paused.value = false;
    return new BytesWriter(0);
}
```

## Step 5: Blacklist System

```typescript
private notBlacklisted(account: Address): void {
    if (!this._blacklist.get(account).isZero()) {
        throw new Revert('Blacklisted');
    }
}

@method({ name: 'account', type: ABIDataTypes.ADDRESS })
@returns({ name: 'success', type: ABIDataTypes.BOOL })
@emit('Blacklisted')
public blacklist(calldata: Calldata): BytesWriter {
    this.onlyRole(u256.fromU64(Role.BLACKLISTER));
    const account = calldata.readAddress();
    this._blacklist.set(account, u256.One);  // Non-zero = blacklisted
    return new BytesWriter(0);
}

@method({ name: 'account', type: ABIDataTypes.ADDRESS })
@returns({ name: 'success', type: ABIDataTypes.BOOL })
@emit('UnBlacklisted')
public unBlacklist(calldata: Calldata): BytesWriter {
    this.onlyRole(u256.fromU64(Role.BLACKLISTER));
    const account = calldata.readAddress();
    this._blacklist.set(account, u256.Zero);  // Zero = not blacklisted
    return new BytesWriter(0);
}
```

## Step 6: Override Transfers for Checks

Override `transfer` and `transferFrom` to add pause and blacklist checks:

```typescript
@method(
    { name: 'to', type: ABIDataTypes.ADDRESS },
    { name: 'amount', type: ABIDataTypes.UINT256 },
)
@returns({ name: 'success', type: ABIDataTypes.BOOL })
@emit('Transfer')
public override transfer(calldata: Calldata): BytesWriter {
    this.whenNotPaused();
    this.notBlacklisted(Blockchain.tx.sender);

    const to = calldata.readAddress();
    this.notBlacklisted(to);

    const fullCalldata = new Calldata(calldata.buffer);
    return super.transfer(fullCalldata);
}

@method(
    { name: 'from', type: ABIDataTypes.ADDRESS },
    { name: 'to', type: ABIDataTypes.ADDRESS },
    { name: 'amount', type: ABIDataTypes.UINT256 },
)
@returns({ name: 'success', type: ABIDataTypes.BOOL })
@emit('Transfer')
public override transferFrom(calldata: Calldata): BytesWriter {
    this.whenNotPaused();

    const from = calldata.readAddress();
    const to = calldata.readAddress();

    this.notBlacklisted(Blockchain.tx.sender);
    this.notBlacklisted(from);
    this.notBlacklisted(to);

    const fullCalldata = new Calldata(calldata.buffer);
    return super.transferFrom(fullCalldata);
}
```

## Collateral Verification via Bitcoin Outputs

Since OPNet contracts cannot hold BTC, collateral verification uses the verify-don't-custody pattern. The contract checks that the minting transaction includes a Bitcoin output sending collateral to the correct custody address:

```typescript
private verifyCollateral(amount: u256): void {
    const requiredCollateral = this.calculateCollateral(amount);
    let collateralFound = false;

    const outputs = Blockchain.tx.outputs;
    for (let i = 0; i < outputs.length; i++) {
        const output = outputs[i];
        if (output.address.equals(this.collateralVaultAddress) &&
            u256.fromU64(output.value) >= requiredCollateral) {
            collateralFound = true;
            break;
        }
    }

    if (!collateralFound) {
        throw new Revert('Insufficient collateral');
    }
}
```

## Role Hierarchy

```
Admin (Role.ADMIN = 1)
  - Can grant/revoke all roles
  - Can update master minter
  - Has emergency powers

Master Minter (stored address)
  - Configure minter allowances
  - Add/remove minters

Minter (Role.MINTER = 2)
  - Mint up to allowance
  - Burn own tokens

Pauser (Role.PAUSER = 4)
  - Pause all transfers
  - Unpause

Blacklister (Role.BLACKLISTER = 8)
  - Add addresses to blacklist
  - Remove from blacklist
```

## Comparison with Solidity

| Feature | Solidity (OpenZeppelin) | OPNet |
|---------|------------------------|-------|
| Role storage | `mapping(bytes32 => mapping(address => bool))` | Single `AddressMemoryMap` with bit flags |
| Role definition | `keccak256("MINTER_ROLE")` | `enum Role { MINTER = 2 }` |
| Pausable | `ERC20Pausable` extension | Manual `StoredBoolean` |
| Blacklist | `mapping(address => bool)` | `AddressMemoryMap` (u256, non-zero = true) |
| Modifiers | `whenNotPaused`, `onlyRole()` | Inline function calls |
| Multiple inheritance | `is ERC20, Pausable, AccessControl` | Single `extends OP20` |

## References

- [Stablecoin Example](../docs/btc-runtime/examples/stablecoin.md) -- Complete implementation with all code
- [OP20 Token](../docs/btc-runtime/contracts/op20-token.md) -- OP20 base class reference
- [Storage System](../docs/btc-runtime/core-concepts/storage-system.md) -- AddressMemoryMap and pointers
