# OPNet Development Troubleshooting

Common errors, causes, and fixes for OPNet development.

---

## Build & Compilation Errors

### Error: `Cannot find module 'opnet'`
**Cause:** Wrong package version or missing install.
**Fix:** Check `guidelines/setup-guidelines.md` for exact versions. Run `npm install`.

### Error: `Top-level await is currently not supported with the "cjs" output format`
**Cause:** Using `npx tsx` with top-level await outside an async function.
**Fix:** Wrap code in `async function main() { ... } main();` or set `"type": "module"` in package.json.

### Error: `Transform failed` / `TS2564: Property has no initializer`
**Cause:** AssemblyScript requires field initialization at declaration.
**Fix:** Initialize `StoredU256` and other fields at declaration, not in the constructor body.

### Error: `Cannot use namespace as a type`
**Cause:** Importing `ABIDataTypes` incorrectly.
**Fix:** `ABIDataTypes` is globally available via decorators in contracts. For TypeScript, import from `@btc-vision/transaction` or `opnet`.

### Error: `Module not found: @btc-vision/bitcoin`
**Cause:** Using `bitcoinjs-lib` instead of the OPNet fork.
**Fix:** Replace `bitcoinjs-lib` with `@btc-vision/bitcoin`. Replace `ecpair` with `@btc-vision/ecpair`.

### Error: WASM compilation produces 0 bytes
**Cause:** Missing or incorrect `asconfig.json`, or contract has no exported methods.
**Fix:** Verify `asconfig.json` matches `docs/asconfig.json`. Ensure contract uses `@method` decorators.

---

## Runtime & RPC Errors

### Error: `Error fetching block: Something went wrong`
**Cause:** Using `'latest'` as block parameter (unsupported on some RPC versions).
**Fix:** Fetch the block by specific height number instead.

### Error: `provider.getBlockCount is not a function`
**Cause:** `getBlockCount()` doesn't exist on the provider.
**Fix:** Use `provider.getBlock(Number(height))` to probe for latest block.

### Error: `JSON.stringify cannot serialize a BigInt`
**Cause:** `provider.getBlock()` passed a `BigInt` block height internally.
**Fix:** Convert to `Number()` before passing: `provider.getBlock(Number(blockHeight))`.

### Error: `Could not decode transaction`
**Cause:** Transaction calldata malformed, wrong ABI encoding, or contract doesn't exist at address.
**Fix:** Verify contract is deployed, ABI matches contract, and all parameters are correctly typed.

### Error: `Output value is less than minimum dust (275 < 330)`
**Cause:** NativeSwap execute has an LP recipient allocated below SDK's MINIMUM_DUST threshold.
**Fix:** Known SDK issue. Pad extraOutputs to at least 546 sats. May need SDK update.

---

## Frontend Errors

### Error: `Address.fromString() crashes` / `Invalid address`
**Cause:** Passing a bech32 address (`bc1q...`) or only one parameter.
**Fix:** `Address.fromString()` requires TWO params: `(hashedMLDSAKey, publicKey)`. Get both from `useWalletConnect()`. Never pass raw Bitcoin addresses.

### Error: `Wallet not connected` even when wallet is connected
**Cause:** Gating on `signer` object which is `null` on frontend.
**Fix:** Check `isConnected` and `address` from `useWalletConnect()`, not `signer`.

### Error: WalletConnect modal renders at bottom of page / broken layout
**Cause:** Default `@btc-vision/walletconnect` modal CSS positioning.
**Fix:** Add the WalletConnect CSS fix (position: fixed, centered overlay). See AGENTS.md WalletConnect Popup Fix section.

### Error: `import { Address } from '@btc-vision/bitcoin'` fails in browser
**Cause:** `@btc-vision/bitcoin` browser bundle doesn't export `Address`.
**Fix:** Import from `opnet` instead: `import { Address } from 'opnet';`

---

## Contract Interaction Errors

### Error: `getContract` returns undefined / wrong contract
**Cause:** Missing parameters. `getContract` requires 5 params.
**Fix:** `getContract<T>(address, abi, provider, network, senderAddress)` -- all 5 are required.

### Error: Simulation succeeds but `sendTransaction` fails
**Cause:** Simulation doesn't check BTC availability. Actual send needs funded UTXOs.
**Fix:** Ensure the sender has sufficient BTC UTXOs. Check `provider.utxoManager.getUTXOs()`.

### Error: `increaseAllowance` not found / `approve` doesn't work
**Cause:** OP20 uses `increaseAllowance()`, not `approve()`.
**Fix:** Replace `approve()` calls with `increaseAllowance()`.

### Error: Contract deploy calldata is 0 bytes
**Cause:** Known regtest node bug -- node passes 0 bytes to `onDeploy()`.
**Fix:** Confirmed bug. Workaround: don't rely on constructor calldata in `onDeployment()`.

---

## NativeSwap Errors

### Error: Approve and pool creation in same block fails
**Cause:** Token approval needs confirmation before pool creation can reference it.
**Fix:** Submit approve TX, wait for block confirmation, THEN submit pool creation.

### Error: CSV address generation fails
**Cause:** Wrong pubkey format or missing CSV delay.
**Fix:** Use `Address.fromString(hashedMLDSAKey, publicKey).toCSV(1n)` with the hashed ML-DSA key and tweaked public key.

### Error: `setTransactionDetails()` required before simulation
**Cause:** NativeSwap simulation needs transaction context.
**Fix:** Call `setTransactionDetails()` on the contract before running any simulation. Do NOT use `maximumAllowedSatToSpend` as a substitute.

---

## Deployment Errors

### Error: `sendRawTransaction` returns `{ success: false }`
**Cause:** Transaction rejected by node. Could be dust, invalid script, or mempool policy.
**Fix:** Check the `result` field for error message. Common: dust threshold, max ancestors exceeded.

### Error: `opr1s` addresses can't be passed to `Address.fromString()`
**Cause:** `opr1s` is an OPNet-specific format not directly parseable.
**Fix:** Use `getPublicKeysInfoRaw()` to resolve the tweaked public key, then pass that to `Address.fromString()`.

### Error: Mempool 25-descendant chain limit
**Cause:** Too many unconfirmed transactions chained from same UTXOs.
**Fix:** Split UTXOs into multiple independent ones. Wait for confirmations between batches.

---

## Buffer→Uint8Array Migration Issues

### Error: `Buffer is not defined` / `Cannot find name 'Buffer'`
**Cause:** Buffer has been removed from the entire OPNet stack. All packages now use Uint8Array.
**Fix:** Replace all Buffer usage with Uint8Array. Use `BufferHelper` from `@btc-vision/transaction` for hex conversions. Use `TextEncoder`/`TextDecoder` for string encoding.

### Error: `Buffer.from is not a function`
**Cause:** Same as above - Buffer is gone from OPNet packages.
**Fix:** Replace `Buffer.from(hex, 'hex')` with `BufferHelper.hexToUint8Array(hex)` from `@btc-vision/transaction`. Replace `Buffer.from(str)` with `new TextEncoder().encode(str)`.

---

## AssemblyScript Fork Issues

### Error: `Duplicate asc binary` / `Cannot find module 'assemblyscript'`
**Cause:** Both `assemblyscript` and `@btc-vision/assemblyscript` are installed, or wrong one is installed.
**Fix:** Run `npm uninstall assemblyscript` first, then `npm i @btc-vision/assemblyscript@^0.29.2`. The fork is required for closure support.

### Error: `Closures are not supported`
**Cause:** Using upstream `assemblyscript` instead of the custom fork.
**Fix:** `npm uninstall assemblyscript && npm i @btc-vision/assemblyscript@^0.29.2`

---

## WalletConnect v2 Issues

### Error: `openConnectModal is not a function` / `connectToWallet undefined`
**Cause:** Using old WalletConnect v1 API. The v2 API has different method names.
**Fix:** Update to `@btc-vision/walletconnect` latest and use the new API. See `docs/walletconnect/README.md`.

---

## P2MR Address Issues

### Error: `Unknown address type` when handling P2MR addresses
**Cause:** Code doesn't handle the new P2MR (BIP-360) address format.
**Fix:** Update address handling to support P2MR alongside P2TR/P2WPKH. See `docs/bitcoin/p2mr.md`.

---

## General Tips

- **Always use `optimize: false`** when calling `getUTXOs()` -- `optimize: true` filters out UTXOs
- **Never use `number` for satoshi amounts** -- always `bigint`
- **Never use `while` loops in contracts** -- bounded `for` only
- **Always simulate before sending** -- never skip simulation step
- **Check `guidelines/setup-guidelines.md` for package versions** -- never guess
- **Never use Buffer** -- always Uint8Array (Buffer is removed from the stack)
- **Always `npm uninstall assemblyscript`** before installing `@btc-vision/assemblyscript`
- **Use MongoDB** for backend persistence, not file-based storage
- **Use `@btc-vision/hyper-express`** for backends, never Express/Fastify/Koa
