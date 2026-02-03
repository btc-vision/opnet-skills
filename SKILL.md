# OPNet Development Skill

A comprehensive skill for building on OPNet - Bitcoin's L1 consensus layer for trustless smart contracts.

## What is OPNet

OPNet is a **Bitcoin L1 consensus layer** enabling smart contracts directly on Bitcoin. It is:

- **NOT a metaprotocol** - It's a full consensus layer
- **Fully trustless** - No centralized components
- **Permissionless** - Anyone can participate
- **Decentralized** - Relies on Bitcoin PoW + OPNet epoch SHA1 mining

### Security Model

After 20 blocks, an epoch is buried deep enough that changing it requires rewriting Bitcoin history at **millions of dollars per hour**, making OPNet state **more final than Bitcoin's 6-confirmation security**.

The **checksum root** for each epoch is a cryptographic fingerprint of the entire state. If even one bit differs, the checksum changes completely and proof fails, making **silent state corruption impossible**.

### Key Principles

1. **Contracts are WebAssembly** (AssemblyScript) - Deterministic execution
2. **NON-CUSTODIAL** - Contracts NEVER hold BTC
3. **Verify-don't-custody** - Contracts verify L1 tx outputs, not hold funds
4. **Partial reverts** - Only consensus layer execution reverts; Bitcoin transfers are ALWAYS valid
5. **No gas token** - Uses Bitcoin directly

---

## ENFORCEMENT RULES (NON-NEGOTIABLE)

### Before Writing ANY Code

**YOU MUST:**

1. **READ `docs/core/typescript-law/` COMPLETELY** - These are strict TypeScript rules
2. **VERIFY project configuration matches standards** in `configs/`

### Configuration Verification Checklist

- [ ] `tsconfig.json` matches `configs/frontend/` (frontend) or strict ES2025 (contracts/plugins)
- [ ] `eslint.config.js` exists and enforces strict TypeScript
- [ ] `.prettierrc` exists with correct settings
- [ ] **NO `any` type anywhere** - This is FORBIDDEN
- [ ] ES2025 compliant
- [ ] Unit tests exist and pass

### IF ANY CHECK FAILS → REFUSE TO CODE UNTIL FIXED

Misconfigured projects lead to **exploits and critical vulnerabilities**.

---

## TypeScript Law (CRITICAL)

From `docs/core/typescript-law/`:

### FORBIDDEN Constructs

| Construct | Why Forbidden |
|-----------|---------------|
| `any` | Runtime bug waiting to happen. No exceptions. |
| `unknown` | Only at system boundaries (JSON parsing, external APIs) |
| `object` (lowercase) | Use specific interfaces or `Record<string, T>` |
| `Function` (uppercase) | Use specific signatures |
| `{}` | Means "any non-nullish value". Use `Record<string, never>` |
| Non-null assertion (`!`) | Use explicit null checks or optional chaining |
| Dead/duplicate code | Design is broken if present |
| ESLint bypasses | Never |
| Section separator comments | See below |

### FORBIDDEN: Section Separator Comments

**NEVER** write comments like:

```typescript
// ==================== PRIVATE METHODS ====================
// ---------------------- HELPERS ----------------------
// ************* CONSTANTS *************
// ####### INITIALIZATION #######
```

These are **lazy, unprofessional, and useless**. They add noise without value.

**INSTEAD**: Use proper TSDoc for EVERY class, method, property, and function:

```typescript
/**
 * Transfers tokens from sender to recipient.
 *
 * @param to - The recipient address
 * @param amount - The amount to transfer in base units
 * @returns True if transfer succeeded
 * @throws {InsufficientBalanceError} If sender has insufficient balance
 * @throws {InvalidAddressError} If recipient address is invalid
 *
 * @example
 * ```typescript
 * const success = await token.transfer(recipientAddress, 1000n);
 * ```
 */
public async transfer(to: Address, amount: bigint): Promise<boolean> {
    // ...
}
```

**TSDoc Requirements:**

- `@param` for every parameter
- `@returns` for non-void returns
- `@throws` for possible exceptions
- `@example` for non-trivial methods
- Description of what the method does, not how

**Code organization comes from proper class design, not ASCII art.**

### Numeric Types

- **`number`**: Array lengths, loop counters, small flags, ports, pixels
- **`bigint`**: Satoshi amounts, block heights, timestamps, database IDs, file sizes, cumulative totals
- **Floats for financial values**: **FORBIDDEN** - Use fixed-point `bigint` with explicit scale

### Required tsconfig.json Settings

```json
{
    "compilerOptions": {
        "strict": true,
        "noImplicitAny": true,
        "strictNullChecks": true,
        "noUnusedLocals": true,
        "noUnusedParameters": true,
        "exactOptionalPropertyTypes": true,
        "noImplicitReturns": true,
        "noFallthroughCasesInSwitch": true,
        "noUncheckedIndexedAccess": true,
        "noImplicitOverride": true,
        "moduleResolution": "bundler",
        "module": "ESNext",
        "target": "ES2025",
        "lib": ["ES2025"],
        "isolatedModules": true,
        "verbatimModuleSyntax": true
    }
}
```

---

## Performance Rules

### THREADING IS MANDATORY

- **Sequential processing = unacceptable performance**
- Use Worker threads for CPU-bound work
- Use async with proper concurrency for I/O
- Batch operations where possible
- Use connection pooling

### Caching (ALWAYS)

- **Reuse contract instances** - Never create new instances for same contract
- **Reuse providers** - Single provider instance per network
- **Cache locally** - Browser localStorage/IndexedDB for user data
- **Cache on API** - Server-side caching for blockchain state
- **Invalidate on block change** - Clear stale data when new block confirmed

### Backend/API Frameworks

**MANDATORY**: Use OPNet's high-performance libraries:

| Package | Purpose |
|---------|---------|
| `@btc-vision/uwebsocket.js` | WebSocket server (fastest) |
| `@btc-vision/hyper-express` | HTTP server (fastest) |

**FORBIDDEN**: Express, Fastify, Koa, Hapi, or any other HTTP framework. They are significantly slower.

```typescript
// CORRECT - Use hyper-express with threading
import HyperExpress from '@btc-vision/hyper-express';
import { Worker } from 'worker_threads';

const app = new HyperExpress.Server();
// Use classes, not functions
// Delegate CPU work to workers
```

### Optimization Principles

1. Profile first, optimize based on data
2. Avoid creating objects in hot loops
3. Reuse buffers when possible
4. Use typed arrays for binary data
5. Keep object shapes consistent (V8 hidden classes)

---

## Contract Gas Optimization (CRITICAL)

### FORBIDDEN Patterns in Contracts

| Pattern | Why Forbidden | Alternative |
|---------|---------------|-------------|
| `while` loops | Unbounded gas consumption | Use bounded `for` loops |
| Infinite loops | Contract halts, wastes gas | Always have exit condition |
| Iterating all map keys | O(n) grows exponentially | Use indexed lookups, pagination |
| Iterating all array elements | O(n) cost explosion | Store aggregates, use pagination |
| Unbounded arrays | Grows forever | Cap size, use cleanup |

### Gas-Efficient Patterns

```typescript
// WRONG - Iterating all holders (O(n) disaster)
let total: u256 = u256.Zero;
for (let i = 0; i < holders.length; i++) {
    total = SafeMath.add(total, balances.get(holders[i]));
}

// CORRECT - Store running total
const totalSupply: StoredU256 = new StoredU256(TOTAL_SUPPLY_POINTER);
// Update on mint/burn, read in O(1)
```

### Optimization Strategies

1. **Store aggregates** - Don't compute, track incrementally
2. **Pagination** - Process in bounded chunks
3. **Indexed lookups** - O(1) instead of O(n) searches
4. **Lazy evaluation** - Compute only when needed
5. **Batch operations** - Amortize overhead across multiple ops

### Security vs Optimization Balance

**CRITICAL**: Optimization must NOT introduce vulnerabilities:

- [ ] Access control still enforced after optimization
- [ ] Bounds checking preserved
- [ ] Integer overflow/underflow handled
- [ ] State consistency maintained
- [ ] No new attack vectors created

When in doubt, **security wins over gas savings**.

---

## Security Audit Checklist

### All Code Must Be Checked For:

#### Cryptographic

- [ ] Key generation entropy
- [ ] Nonce reuse
- [ ] Signature malleability
- [ ] Timing attacks
- [ ] Replay attacks
- [ ] RNG weaknesses
- [ ] EC parameter validation
- [ ] Hash collision potential
- [ ] State commitment integrity
- [ ] Deterministic execution guarantees

#### Smart Contract

- [ ] Reentrancy
- [ ] Integer overflow/underflow
- [ ] Access control bypass
- [ ] Authorization flaws
- [ ] Privilege escalation
- [ ] State manipulation
- [ ] Race conditions
- [ ] Input validation failures
- [ ] Boundary errors
- [ ] Logic flaws
- [ ] Unsafe type conversions
- [ ] Unhandled edge cases
- [ ] Data integrity violations
- [ ] State inconsistency
- [ ] Improper error handling
- [ ] Dangerous dependencies

#### Bitcoin-specific

- [ ] Transaction malleability
- [ ] UTXO selection vulnerabilities
- [ ] Fee sniping
- [ ] Transaction pinning
- [ ] Dust attacks

---

## Quick Start

| Task | Template |
|------|----------|
| New OP20 token | `templates/contracts/op20-token/` |
| New OP721 NFT | `templates/contracts/op721-nft/` |
| Generic contract | `templates/contracts/generic/` |
| Contract tests | `templates/tests/contract-tests/` |
| Frontend dApp | `templates/frontend/opnet-dapp/` |
| Node plugin (indexer) | `templates/plugins/indexer/` |
| Node plugin (generic) | `templates/plugins/generic/` |

---

## Directory Structure

```
/root/opnet-skills/
├── SKILL.md                    # This file - main entry point
├── docs/                       # ALL documentation
│   ├── core/
│   │   ├── typescript-law/     # STRICT rules (NON-NEGOTIABLE)
│   │   ├── opnet/              # Client library (JSON-RPC, WebSocket)
│   │   ├── transaction/        # Transaction builder
│   │   └── OIP/                # Protocol specs (OIP-0003 = plugins)
│   ├── contracts/
│   │   ├── btc-runtime/        # AssemblyScript contract runtime
│   │   ├── opnet-transform/    # Decorators (@method, @returns, @emit)
│   │   ├── as-bignum/          # u256, u128 implementations
│   │   └── example-tokens/     # Contract examples
│   ├── clients/
│   │   ├── bitcoin/            # Bitcoin library (recoded bitcoinjs-lib)
│   │   ├── bip32/              # HD derivation + ML-DSA quantum support
│   │   ├── ecpair/             # EC key pairs
│   │   └── walletconnect/      # Wallet connection
│   ├── testing/
│   │   ├── unit-test-framework/
│   │   └── opnet-unit-test/
│   ├── frontend/
│   │   └── motoswap-ui/        # THE STANDARD for frontend configs
│   └── plugins/
│       ├── plugin-sdk/
│       └── opnet-node/         # opnet-cli docs
├── configs/                    # MANDATORY configuration standards
│   ├── frontend/               # From motoswap-ui (THE STANDARD)
│   ├── contracts/              # From example-tokens
│   ├── node/                   # From opnet-node
│   └── typescript-law/         # TS rules
└── templates/                  # Production-ready starters
    ├── contracts/
    │   ├── op20-token/
    │   ├── op721-nft/
    │   └── generic/
    ├── tests/
    │   └── contract-tests/
    ├── frontend/
    │   └── opnet-dapp/
    └── plugins/
        ├── indexer/
        └── generic/
```

---

## Documentation Index

### Core Documentation

| Path | Description |
|------|-------------|
| `docs/core/typescript-law/` | **STRICT TypeScript rules - READ FIRST** |
| `docs/core/opnet/` | Main client library (JSON-RPC, WebSocket, contracts) |
| `docs/core/opnet/backend-api.md` | **Backend API with hyper-express/uwebsocket.js** |
| `docs/core/transaction/` | Transaction builder, PSBT, quantum signatures |
| `docs/core/transaction/addresses/P2OP.md` | P2OP quantum-resistant address format |
| `docs/core/OIP/` | Protocol specs (OIP-0003 = plugin system) |

### Contract Documentation

| Path | Description |
|------|-------------|
| `docs/contracts/btc-runtime/` | AssemblyScript contract runtime |
| `docs/contracts/btc-runtime/gas-optimization.md` | **Gas optimization patterns (CRITICAL)** |
| `docs/contracts/opnet-transform/` | Decorators: @method, @returns, @emit |
| `docs/contracts/as-bignum/` | u256, u128 for AssemblyScript |
| `docs/contracts/example-tokens/` | Contract examples (OP20, OP721, stablecoins) |

### Client Documentation

| Path | Description |
|------|-------------|
| `docs/clients/bitcoin/` | Bitcoin library (709x faster than bitcoinjs-lib) |
| `docs/clients/bip32/` | HD derivation with ML-DSA quantum resistance |
| `docs/clients/ecpair/` | EC key pair management |
| `docs/clients/walletconnect/` | Web wallet connection |

### Testing Documentation

| Path | Description |
|------|-------------|
| `docs/testing/unit-test-framework/` | Contract testing framework |
| `docs/testing/opnet-unit-test/` | Test examples |

### Frontend Documentation

| Path | Description |
|------|-------------|
| `docs/frontend/motoswap-ui/` | **Frontend integration guide (wallet, caching, transactions)** |

### Plugin Documentation

| Path | Description |
|------|-------------|
| `docs/plugins/plugin-sdk/` | Node plugin development SDK |
| `docs/plugins/opnet-node/` | Node operation, opnet-cli |

---

## Contract Development

### Key Concepts

1. **Contracts use AssemblyScript** - Compiles to WebAssembly
2. **Constructor runs on EVERY interaction** - Use `onDeployment()` for initialization
3. **Contracts CANNOT hold BTC** - They are calculators, not custodians
4. **Verify-don't-custody pattern** - Check `Blockchain.tx.outputs` against internal state

### Decorator Reference

```typescript
// Mark method as callable
@method({ name: 'param1', type: ABIDataTypes.UINT256 })

// Specify return types
@returns({ name: 'result', type: ABIDataTypes.UINT256 })

// Declare emitted events
@emit('Transfer', 'Approval')
```

### Storage Types

| Type | Use Case |
|------|----------|
| `StoredU256` | Single u256 value |
| `StoredBoolean` | Boolean flag |
| `StoredString` | String value |
| `StoredMapU256` | Key-value map (u256 keys/values) |
| `AddressMemoryMap` | In-memory address map |

---

## Testing

### ALL CODE MUST HAVE TESTS

Before any work is considered complete, verify with unit tests.

```typescript
import { opnet, OPNetUnit, Assert, Blockchain } from '@btc-vision/unit-test-framework';

await opnet('My Tests', async (vm: OPNetUnit) => {
    vm.beforeEach(async () => {
        Blockchain.dispose();
        await Blockchain.init();
    });

    await vm.it('should work correctly', async () => {
        const result = await contract.someMethod();
        Assert.expect(result).toEqual(expected);
    });
});
```

---

## Plugin Development

**OPNet nodes are like Minecraft servers - they support plugins!**

### Key Resources

- Read `docs/plugins/plugin-sdk/`
- Read `docs/core/OIP/OIP-0003.md` for plugin specification
- Read `docs/plugins/opnet-node/` for opnet-cli usage
- Use `templates/plugins/indexer/` for indexers (e.g., track all OP20 holders)

### Plugin Lifecycle

| Hook | When Called | Blocking |
|------|-------------|----------|
| `onFirstInstall` | First installation | Yes |
| `onNetworkInit` | Every load | Yes |
| `onBlockChange` | New block confirmed | No |
| `onReorg` | Chain reorganization | Yes (CRITICAL) |

### Critical: Reorg Handling

You **MUST** implement `onReorg()` to revert state for reorged blocks. Failure to do so will cause data inconsistency.

---

## Frontend Development

### Configuration Standard

Frontend configs **MUST** match `configs/frontend/` exactly:

- Vite + React
- Vitest for testing
- ESLint with TypeScript strict mode
- Prettier formatting
- ES2025 target

### Caching (MANDATORY)

- **Reuse provider instances** - Singleton per network
- **Reuse contract instances** - Cache by address
- **Cache API responses** - Invalidate on block change
- **Use localStorage** - For user preferences, token metadata

### Polling Intervals

| Operation | Interval |
|-----------|----------|
| Block height | 15 seconds |
| Transaction confirmation | 15 seconds |
| Fee estimation | 30 seconds |

### Key Hooks

```typescript
// OPNet provider
const { provider, isConnected, network } = useOPNet();

// Contract interaction
const { contract, callMethod, loading } = useContract(address, abi);

// Wallet connection
const { address, connect, disconnect, signPsbt } = useWallet();
```

See `docs/frontend/motoswap-ui/README.md` for complete integration guide.

---

## Backend/API Development

### MANDATORY Frameworks

| Package | Purpose |
|---------|---------|
| `@btc-vision/hyper-express` | HTTP server (fastest) |
| `@btc-vision/uwebsocket.js` | WebSocket server (fastest) |

**FORBIDDEN**: Express, Fastify, Koa, Hapi - they are significantly slower.

### Architecture Requirements

1. **Use classes** - Not function handlers
2. **Use threading** - Worker threads for CPU work
3. **Singleton providers** - One provider instance per network
4. **Cache everything** - Contract instances, API responses
5. **Invalidate on block change** - Keep data fresh

See `docs/core/opnet/backend-api.md` for complete guide.

---

## Client Libraries

| Package | Path | Description |
|---------|------|-------------|
| `@btc-vision/bitcoin` | `docs/clients/bitcoin/` | Bitcoin lib (709x faster PSBT) |
| `@btc-vision/bip32` | `docs/clients/bip32/` | HD derivation + quantum |
| `@btc-vision/ecpair` | `docs/clients/ecpair/` | EC key pairs |
| `@btc-vision/transaction` | `docs/core/transaction/` | OPNet transactions |
| `opnet` | `docs/core/opnet/` | Main client library |
| `@btc-vision/walletconnect` | `docs/clients/walletconnect/` | Wallet connection |

---

## Bitcoin Context

OPNet is built on Bitcoin. Understanding Bitcoin fundamentals is essential:

- **UTXOs** - Unspent Transaction Outputs
- **Taproot (P2TR)** - Primary address type
- **PSBT** - Partially Signed Bitcoin Transactions
- **SegWit** - Segregated Witness
- **Schnorr signatures** - Used for Taproot
- **ML-DSA** - Post-quantum signatures (supported via bip32)

---

## Version Requirements

| Tool | Minimum Version |
|------|-----------------|
| Node.js | >= 24.0.0 |
| TypeScript | >= 5.9.3 |
| AssemblyScript | >= 0.28.9 |

---

## Support & Resources

- **OPNet Documentation**: https://docs.opnet.org
- **GitHub**: https://github.com/btc-vision
- **OIP Specifications**: `docs/core/OIP/`

---

## Critical Reminders

1. **READ typescript-law FIRST** - Non-negotiable rules
2. **Verify project configuration** - Before writing any code
3. **NO `any` type** - Ever
4. **Test everything** - Unit tests required
5. **Handle reorgs** - In plugins, always implement `onReorg()`
6. **Contracts don't hold BTC** - Verify-don't-custody pattern
7. **Threading for performance** - Sequential = unacceptable
8. **Configuration must match standards** - Or refuse to code
