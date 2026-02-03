# Generic OPNet Contract Template

A minimal but complete OPNet smart contract template demonstrating core patterns.

## Features

- Storage patterns (StoredU256, StoredString, StoredBoolean)
- Access control (owner-only functions)
- Custom events
- Pausable pattern
- Method decorators (@method, @returns, @emit)

## Quick Start

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Modify `assembly/MyContract.ts`** to implement your logic.

3. **Build the contract:**
   ```bash
   npm run build
   ```

## Storage Patterns

### Primitive Storage
```typescript
const myPointer: u16 = Blockchain.nextPointer;
private readonly myValue: StoredU256 = new StoredU256(myPointer, u256.Zero);

// Read
const value: u256 = this.myValue.value;

// Write
this.myValue.value = newValue;
```

### Map Storage
```typescript
private readonly balances: StoredMapU256 = new StoredMapU256(pointer);

// Read
const balance: u256 = this.balances.get(addressKey);

// Write
this.balances.set(addressKey, newBalance);
```

## Decorator Reference

### @method
Marks a function as callable via the contract ABI:
```typescript
@method({ name: 'param1', type: ABIDataTypes.UINT256 })
public myMethod(calldata: Calldata): BytesWriter { ... }
```

### @returns
Specifies return types:
```typescript
@returns({ name: 'result', type: ABIDataTypes.UINT256 })
```

### @emit
Declares events emitted by the method:
```typescript
@emit('MyEvent')
```

## Critical Rules

1. **Constructor runs on EVERY call** - use `onDeployment()` for initialization
2. **Contracts CANNOT hold BTC** - use verify-don't-custody pattern
3. **All storage must use unique pointers** - use `Blockchain.nextPointer`
4. **Use SafeMath for arithmetic** - prevents overflow/underflow
5. **Always validate inputs** - check for zero addresses, bounds, etc.

## Directory Structure

```
generic/
├── assembly/
│   ├── index.ts        # Entry point (DO NOT MODIFY)
│   ├── MyContract.ts   # Your contract implementation
│   └── tsconfig.json   # TypeScript config
├── asconfig.json       # AssemblyScript build config
├── package.json        # Dependencies
└── README.md           # This file
```
