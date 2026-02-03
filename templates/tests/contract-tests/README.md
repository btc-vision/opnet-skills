# OPNet Contract Tests Template

A production-ready unit test project for OPNet smart contracts.

## Quick Start

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Run all tests:**
   ```bash
   npm test
   ```

3. **Run specific tests:**
   ```bash
   npm run test:token
   ```

## Writing Tests

### Basic Test Structure

```typescript
import { opnet, OPNetUnit, Assert, Blockchain } from '@btc-vision/unit-test-framework';
import { MyContract } from './contracts/MyContract';

await opnet('My Contract Tests', async (vm: OPNetUnit) => {
    let contract: MyContract;

    vm.beforeEach(async () => {
        Blockchain.dispose();
        Blockchain.clearContracts();
        await Blockchain.init();

        contract = new MyContract(deployerAddress, contractAddress);
        Blockchain.register(contract);
        await contract.init();
    });

    vm.afterEach(() => {
        contract.dispose();
        Blockchain.dispose();
    });

    await vm.it('should do something', async () => {
        const result = await contract.someMethod();
        Assert.expect(result).toEqual(expectedValue);
    });
});
```

### Assertions

```typescript
Assert.expect(value).toEqual(expected);
Assert.expect(value).toNotEqual(other);
Assert.expect(value).toBeDefined();
Assert.expect(value).toBeUndefined();
Assert.expect(value).toBeGreaterThan(other);
Assert.expect(value).toBeLessThan(other);
Assert.expect(array).toDeepEqual(expected);
Assert.expect(address).toEqualAddress(expected);

// Async error testing
await Assert.expect(async () => {
    await contract.methodThatThrows();
}).toThrow();
```

### Blockchain Utilities

```typescript
// Generate addresses
const address = Blockchain.generateRandomAddress();

// Set sender for transactions
Blockchain.setSender(address);

// Mine blocks
Blockchain.mineBlock();

// Gas tracking
Blockchain.enableGasTracking();
const gasUsed = Blockchain.getGasUsed();
Blockchain.disableGasTracking();

// State management
Blockchain.backupState();
Blockchain.restoreState();
```

### Testing Events

```typescript
await vm.it('should emit event', async () => {
    await contract.someMethod();

    const events = contract.getEvents();
    const myEvent = events.find(e => e.name === 'MyEvent');

    Assert.expect(myEvent).toBeDefined();
    // Check event data...
});
```

## Test Categories

- **Unit Tests**: Test individual contract methods
- **Integration Tests**: Test contract interactions
- **Gas Tests**: Measure gas consumption
- **Security Tests**: Test access control, reentrancy, overflow

## Directory Structure

```
contract-tests/
├── src/
│   ├── tests/
│   │   ├── OP20.test.ts    # Token tests
│   │   ├── OP721.test.ts   # NFT tests
│   │   └── setup.ts        # Test utilities
│   └── index.ts            # Entry point
├── tsconfig.json
├── gulpfile.js
├── package.json
└── README.md
```

## Best Practices

1. **Always clean up** in `afterEach` to prevent state leakage
2. **Test edge cases**: zero values, max values, unauthorized callers
3. **Test events**: Verify correct events are emitted
4. **Test reverts**: Ensure invalid operations revert properly
5. **Track gas**: Monitor gas consumption for optimization
