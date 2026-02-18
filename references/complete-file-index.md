## Complete File Index

### Configuration Files (`docs/`)

| File | Description |
|------|-------------|
| `docs/asconfig.json` | AssemblyScript compiler config |
| `docs/eslint-contract.js` | ESLint flat config for AssemblyScript contracts |
| `docs/eslint-generic.js` | ESLint flat config for TypeScript libraries / backends |
| `docs/eslint-react.js` | ESLint flat config for React frontends |
| `docs/tsconfig-generic.json` | TypeScript config (not contracts) |
| `docs/setup-README.md` | Setup instructions |

### TypeScript Law (`docs/typescript-law/`)

| File | Description |
|------|-------------|
| `docs/typescript-law/README.md` | Overview |
| `docs/typescript-law/CompleteLaw.md` | **COMPLETE RULES - READ FIRST** |

### OPNet Client Library (`docs/opnet/`)

| File | Description |
|------|-------------|
| `docs/opnet/README.md` | Library overview |
| `docs/opnet/getting-started/installation.md` | Installation |
| `docs/opnet/getting-started/overview.md` | Architecture overview |
| `docs/opnet/getting-started/quick-start.md` | Quick start guide |
| `docs/opnet/providers/json-rpc-provider.md` | JSON-RPC provider |
| `docs/opnet/providers/websocket-provider.md` | WebSocket provider |
| `docs/opnet/providers/understanding-providers.md` | Provider concepts |
| `docs/opnet/providers/advanced-configuration.md` | Advanced config |
| `docs/opnet/providers/internal-caching.md` | Caching system |
| `docs/opnet/providers/threaded-http.md` | Threading |
| `docs/opnet/contracts/overview.md` | Contract interaction overview |
| `docs/opnet/contracts/instantiating-contracts.md` | Creating contract instances |
| `docs/opnet/contracts/simulating-calls.md` | Simulating calls |
| `docs/opnet/contracts/sending-transactions.md` | Sending transactions |
| `docs/opnet/contracts/gas-estimation.md` | Gas estimation |
| `docs/opnet/contracts/offline-signing.md` | Offline signing |
| `docs/opnet/contracts/transaction-configuration.md` | TX config |
| `docs/opnet/contracts/contract-code.md` | Contract code retrieval |
| `docs/opnet/abi-reference/abi-overview.md` | ABI overview |
| `docs/opnet/abi-reference/data-types.md` | ABI data types |
| `docs/opnet/abi-reference/op20-abi.md` | OP20 ABI |
| `docs/opnet/abi-reference/op20s-abi.md` | OP20S ABI (signatures) |
| `docs/opnet/abi-reference/op721-abi.md` | OP721 ABI |
| `docs/opnet/abi-reference/motoswap-abis.md` | MotoSwap ABIs |
| `docs/opnet/abi-reference/factory-abis.md` | Factory ABIs |
| `docs/opnet/abi-reference/stablecoin-abis.md` | Stablecoin ABIs |
| `docs/opnet/abi-reference/custom-abis.md` | Custom ABI creation |
| `docs/opnet/api-reference/provider-api.md` | Provider API |
| `docs/opnet/api-reference/contract-api.md` | Contract API |
| `docs/opnet/api-reference/epoch-api.md` | Epoch API |
| `docs/opnet/api-reference/utxo-manager-api.md` | UTXO Manager API |
| `docs/opnet/api-reference/types-interfaces.md` | Types & interfaces |
| `docs/opnet/bitcoin/utxos.md` | UTXO handling |
| `docs/opnet/bitcoin/utxo-optimization.md` | UTXO optimization |
| `docs/opnet/bitcoin/balances.md` | Balance queries |
| `docs/opnet/bitcoin/sending-bitcoin.md` | Sending BTC |
| `docs/opnet/blocks/block-operations.md` | Block operations |
| `docs/opnet/blocks/block-witnesses.md` | Block witnesses |
| `docs/opnet/blocks/gas-parameters.md` | Gas parameters |
| `docs/opnet/blocks/reorg-detection.md` | Reorg detection |
| `docs/opnet/epochs/overview.md` | Epochs overview |
| `docs/opnet/epochs/epoch-operations.md` | Epoch operations |
| `docs/opnet/epochs/mining-template.md` | Mining template |
| `docs/opnet/epochs/submitting-epochs.md` | Submitting epochs |
| `docs/opnet/transactions/broadcasting.md` | Broadcasting TXs |
| `docs/opnet/transactions/fetching-transactions.md` | Fetching TXs |
| `docs/opnet/transactions/transaction-receipts.md` | TX receipts |
| `docs/opnet/transactions/challenges.md` | TX challenges |
| `docs/opnet/storage/storage-operations.md` | Storage operations |
| `docs/opnet/public-keys/public-key-operations.md` | Public key ops |
| `docs/opnet/utils/bitcoin-utils.md` | Bitcoin utilities |
| `docs/opnet/utils/binary-serialization.md` | Binary serialization |
| `docs/opnet/utils/revert-decoder.md` | Revert decoder |
| `docs/opnet/examples/op20-examples.md` | OP20 examples |
| `docs/opnet/examples/op721-examples.md` | OP721 examples |
| `docs/opnet/examples/deployment-examples.md` | Deployment examples |
| `docs/opnet/examples/advanced-swaps.md` | Swap examples |

### Transaction Library (`docs/transaction/`)

| File | Description |
|------|-------------|
| `docs/transaction/README.md` | Library overview |
| `docs/transaction/getting-started/installation.md` | Installation |
| `docs/transaction/getting-started/overview.md` | Architecture overview |
| `docs/transaction/getting-started/quick-start.md` | Quick start guide |
| `docs/transaction/transaction-building/transaction-factory.md` | TransactionFactory |
| `docs/transaction/transaction-building/transaction-factory-interfaces.md` | **TransactionFactory interfaces (fees, notes, anchors, send-max)** |
| `docs/transaction/transaction-building/deployment-transactions.md` | Deployment transactions |
| `docs/transaction/transaction-building/interaction-transactions.md` | Interaction transactions |
| `docs/transaction/transaction-building/funding-transactions.md` | Funding transactions |
| `docs/transaction/transaction-building/consolidated-transactions.md` | Consolidated transactions |
| `docs/transaction/transaction-building/cancel-transactions.md` | Cancel transactions |
| `docs/transaction/transaction-building/multisig-transactions.md` | Multisig transactions |
| `docs/transaction/transaction-building/custom-script-transactions.md` | Custom script transactions |
| `docs/transaction/keypair/address.md` | Address class |
| `docs/transaction/keypair/address-verificator.md` | **AddressVerificator - address validation & type detection** |
| `docs/transaction/keypair/ec-keypair.md` | EC key pair utilities |
| `docs/transaction/keypair/message-signer.md` | Message signing |
| `docs/transaction/keypair/mnemonic.md` | Mnemonic / HD wallet |
| `docs/transaction/keypair/wallet.md` | Wallet (classical + quantum keys) |
| `docs/transaction/offline/offline-transaction-signing.md` | Offline signing |
| `docs/transaction/quantum-support/README.md` | Quantum overview |
| `docs/transaction/quantum-support/01-introduction.md` | Quantum intro |
| `docs/transaction/quantum-support/02-mnemonic-and-wallet.md` | Quantum wallet |
| `docs/transaction/quantum-support/03-address-generation.md` | Quantum addresses |
| `docs/transaction/quantum-support/04-message-signing.md` | Quantum signing |
| `docs/transaction/quantum-support/05-address-verification.md` | **Quantum address verification with AddressVerificator** |
| `docs/transaction/addresses/address-types.md` | Address type overview |
| `docs/transaction/addresses/P2OP.md` | P2OP address format |
| `docs/transaction/addresses/P2WDA.md` | P2WDA address format |
| `docs/transaction/signer/tweaked-signer.md` | Tweaked signer |
| `docs/transaction/signer/parallel-signer.md` | Parallel signer |
| `docs/transaction/signer/address-rotation.md` | Address rotation |
| `docs/transaction/abi/abi-coder.md` | ABI coder |
| `docs/transaction/binary/binary-reader.md` | BinaryReader |
| `docs/transaction/binary/binary-writer.md` | BinaryWriter |
| `docs/transaction/browser/wallet-extensions.md` | Wallet extensions |
| `docs/transaction/browser/web3-provider.md` | Web3 provider |
| `docs/transaction/utils/bitcoin-utils.md` | Bitcoin utilities |
| `docs/transaction/utils/buffer-helper.md` | **BufferHelper (Uint8Array↔hex conversions)** |
| `docs/transaction/utils/compressor.md` | Compressor |
| `docs/transaction/utils/types-and-constants.md` | Types & constants |
| `docs/transaction/deterministic/deterministic-collections.md` | Deterministic collections |
| `docs/transaction/epoch/challenge-solution.md` | Challenge solution |
| `docs/transaction/epoch/epoch-validator.md` | Epoch validator |
| `docs/transaction/generators/generators.md` | Generators |
| `docs/transaction/utxo/opnet-limited-provider.md` | OPNet limited provider |
| `docs/transaction/api-reference/interfaces.md` | API interfaces |
| `docs/transaction/api-reference/response-types.md` | Response types |
| `docs/transaction/api-reference/transaction-types.md` | Transaction types |

### OIP Specifications (`docs/OIP/`)

| File | Description |
|------|-------------|
| `docs/OIP/README.md` | OIP overview |
| `docs/OIP/OIP/OIP-0001.md` | OIP process |
| `docs/OIP/OIP/OIP-0002.md` | Contract standards |
| `docs/OIP/OIP/OIP-0003.md` | **Plugin system spec** |
| `docs/OIP/OIP/OIP-0004.md` | Epoch system |
| `docs/OIP/standard/OIP-0020.md` | OP20 token standard |
| `docs/OIP/standard/OIP-0721.md` | OP721 NFT standard |

### Contract Runtime (`docs/btc-runtime/`)

| File | Description |
|------|-------------|
| `docs/btc-runtime/README.md` | Runtime overview & gas optimization |
| `docs/btc-runtime/getting-started/installation.md` | Installation |
| `docs/btc-runtime/getting-started/first-contract.md` | First contract |
| `docs/btc-runtime/getting-started/project-structure.md` | Project structure |
| `docs/btc-runtime/core-concepts/blockchain-environment.md` | Blockchain env |
| `docs/btc-runtime/core-concepts/storage-system.md` | Storage system |
| `docs/btc-runtime/core-concepts/pointers.md` | Storage pointers |
| `docs/btc-runtime/core-concepts/events.md` | Events |
| `docs/btc-runtime/core-concepts/decorators.md` | Decorators |
| `docs/btc-runtime/core-concepts/security.md` | Security |
| `docs/btc-runtime/api-reference/blockchain.md` | Blockchain API |
| `docs/btc-runtime/api-reference/storage.md` | Storage API |
| `docs/btc-runtime/api-reference/events.md` | Events API |
| `docs/btc-runtime/api-reference/op20.md` | OP20 API |
| `docs/btc-runtime/api-reference/op721.md` | OP721 API |
| `docs/btc-runtime/api-reference/safe-math.md` | SafeMath API |
| `docs/btc-runtime/contracts/op-net-base.md` | OP_NET base class |
| `docs/btc-runtime/contracts/op20-token.md` | OP20 implementation |
| `docs/btc-runtime/contracts/op20s-stablecoin.md` | OP20S stablecoin/pegged-token base |
| `docs/btc-runtime/contracts/op721-nft.md` | OP721 implementation |
| `docs/btc-runtime/contracts/reentrancy-guard.md` | Reentrancy guard |
| `docs/btc-runtime/contracts/upgradeable.md` | Upgradeable contracts |
| `docs/btc-runtime/storage/stored-primitives.md` | Stored primitives |
| `docs/btc-runtime/storage/stored-maps.md` | Stored maps |
| `docs/btc-runtime/storage/stored-arrays.md` | Stored arrays |
| `docs/btc-runtime/storage/memory-maps.md` | Memory maps |
| `docs/btc-runtime/types/address.md` | Address type |
| `docs/btc-runtime/types/calldata.md` | Calldata type |
| `docs/btc-runtime/types/bytes-writer-reader.md` | BytesWriter/Reader |
| `docs/btc-runtime/types/safe-math.md` | SafeMath type |
| `docs/btc-runtime/advanced/cross-contract-calls.md` | Cross-contract calls |
| `docs/btc-runtime/advanced/signature-verification.md` | Signature verification |
| `docs/btc-runtime/advanced/quantum-resistance.md` | Quantum resistance |
| `docs/btc-runtime/advanced/bitcoin-scripts.md` | Bitcoin scripts |
| `docs/btc-runtime/advanced/contract-upgrades.md` | Contract upgrades |
| `docs/btc-runtime/advanced/plugins.md` | Contract plugins |
| `docs/btc-runtime/examples/basic-token.md` | Basic token example |
| `docs/btc-runtime/examples/stablecoin.md` | Stablecoin example |
| `docs/btc-runtime/examples/nft-with-reservations.md` | NFT example |
| `docs/btc-runtime/examples/oracle-integration.md` | Oracle example |

### Unit Test Framework (`docs/unit-test-framework/`)

| File | Description |
|------|-------------|
| `docs/unit-test-framework/README.md` | Framework overview |
| `docs/unit-test-framework/getting-started/installation.md` | Installation |
| `docs/unit-test-framework/getting-started/quick-start.md` | Quick start |
| `docs/unit-test-framework/writing-tests/basic-tests.md` | Basic test patterns |
| `docs/unit-test-framework/writing-tests/custom-contracts.md` | Custom contract tests |
| `docs/unit-test-framework/writing-tests/op20-tokens.md` | OP20 token tests |
| `docs/unit-test-framework/writing-tests/op721-nfts.md` | OP721 NFT tests |
| `docs/unit-test-framework/built-in-contracts/op20.md` | Built-in OP20 |
| `docs/unit-test-framework/built-in-contracts/op721.md` | Built-in OP721 |
| `docs/unit-test-framework/built-in-contracts/op721-extended.md` | Extended OP721 |
| `docs/unit-test-framework/api-reference/assertions.md` | Assertions API |
| `docs/unit-test-framework/api-reference/blockchain.md` | Blockchain API |
| `docs/unit-test-framework/api-reference/contract-runtime.md` | ContractRuntime API |
| `docs/unit-test-framework/api-reference/types-interfaces.md` | Types & interfaces |
| `docs/unit-test-framework/api-reference/utilities.md` | Utilities API |
| `docs/unit-test-framework/advanced/consensus-rules.md` | Consensus rules testing |
| `docs/unit-test-framework/advanced/cross-contract-calls.md` | Cross-contract tests |
| `docs/unit-test-framework/advanced/gas-profiling.md` | Gas profiling |
| `docs/unit-test-framework/advanced/signature-verification.md` | Signature tests |
| `docs/unit-test-framework/advanced/state-management.md` | State management |
| `docs/unit-test-framework/advanced/transaction-simulation.md` | TX simulation |
| `docs/unit-test-framework/advanced/upgradeable-contracts.md` | Upgrade tests |
| `docs/unit-test-framework/examples/block-replay.md` | Block replay example |
| `docs/unit-test-framework/examples/nativeswap-testing.md` | NativeSwap testing |

### Legacy Unit Test (`docs/opnet-unit-test/`)

| File | Description |
|------|-------------|
| `docs/opnet-unit-test/README.md` | Legacy test overview |
| `docs/opnet-unit-test/Blockchain.md` | Blockchain mocking |
| `docs/opnet-unit-test/ContractRuntime.md` | Contract runtime |

### Bitcoin Library (`docs/bitcoin/`)

| File | Description |
|------|-------------|
| `docs/bitcoin/README.md` | Library overview |
| `docs/bitcoin/address.md` | Address encoding/decoding |
| `docs/bitcoin/block.md` | Block class |
| `docs/bitcoin/crypto.md` | Cryptographic functions |
| `docs/bitcoin/ecc.md` | Elliptic curve |
| `docs/bitcoin/errors.md` | Error types |
| `docs/bitcoin/io.md` | I/O utilities |
| `docs/bitcoin/networks.md` | Network configurations |
| `docs/bitcoin/p2mr.md` | **P2MR (BIP-360) quantum-resistant addresses** |
| `docs/bitcoin/payments.md` | Payment types (P2TR, P2WPKH, P2WSH, P2SH, P2OP) |
| `docs/bitcoin/psbt.md` | PSBT class, signing, finalization |
| `docs/bitcoin/script.md` | Script building, opcodes |
| `docs/bitcoin/taproot.md` | Taproot support |
| `docs/bitcoin/transaction.md` | Transaction class |
| `docs/bitcoin/types.md` | Type definitions |
| `docs/bitcoin/workers.md` | Worker threads |

### BIP32 HD Derivation (`docs/bip32/`)

| File | Description |
|------|-------------|
| `docs/bip32/README.md` | Overview |
| `docs/bip32/getting-started/installation.md` | Installation |
| `docs/bip32/getting-started/overview.md` | Architecture overview |
| `docs/bip32/getting-started/quick-start.md` | Quick start |
| `docs/bip32/bip32/factory.md` | BIP32 factory |
| `docs/bip32/bip32/key-derivation.md` | Key derivation |
| `docs/bip32/bip32/serialization.md` | Serialization |
| `docs/bip32/bip32/signing.md` | Signing |
| `docs/bip32/bip32/tweaking.md` | Key tweaking |
| `docs/bip32/derivation-paths/derivation-paths.md` | Derivation paths |
| `docs/bip32/networks/network-configuration.md` | Network config |
| `docs/bip32/quantum/overview.md` | Quantum BIP32 overview |
| `docs/bip32/quantum/factory.md` | Quantum BIP32 factory |
| `docs/bip32/quantum/key-derivation.md` | Quantum key derivation |
| `docs/bip32/quantum/security-levels.md` | ML-DSA security levels |
| `docs/bip32/api-reference/bip32-api.md` | BIP32 API reference |
| `docs/bip32/api-reference/quantum-api.md` | Quantum API reference |
| `docs/bip32/api-reference/types-interfaces.md` | Types & interfaces |

### Other Libraries

| File | Description |
|------|-------------|
| `docs/ecpair/README.md` | EC key pairs |
| `docs/as-bignum/README.md` | BigNum library (u256, u128) |
| `docs/assemblyscript/README.md` | AssemblyScript fork (closures) |
| `docs/opnet-transform/README.md` | Transform decorators |
| `docs/bs58check/README.md` | Base58Check encoding |
| `docs/bitcoin-rpc/README.md` | Bitcoin RPC client |
| `docs/noble-post-quantum/distributed-dkg-plan.md` | DKG plan |
| `docs/noble-post-quantum/threshold-ml-dsa-whitepaper.md` | Threshold ML-DSA |

### WalletConnect (`docs/walletconnect/`)

| File | Description |
|------|-------------|
| `docs/walletconnect/README.md` | WalletConnect v2 integration |
| `docs/walletconnect/wallet-integration.md` | Wallet integration guide |

### Example Tokens (`docs/example-tokens/`)

| File | Description |
|------|-------------|
| `docs/example-tokens/README.md` | Example tokens overview |
| `docs/example-tokens/OP_20.md` | OP20 example |

### Infrastructure

| File | Description |
|------|-------------|
| `docs/opnet-node/README.md` | OPNet node |
| `docs/opnet-node/docker-README.md` | Docker setup |
| `docs/opnet-cli/README.md` | OPNet CLI |
| `docs/op-vm/README.md` | OPNet VM |
| `docs/plugin-sdk/README.md` | Plugin SDK |
| `docs/opwallet/README.md` | OP_WALLET overview |
| `docs/opwallet/Functions.md` | OP_WALLET content script functions |

### Cryptography (`docs/cryptography/`)

| File | Description |
|------|-------------|
| `docs/cryptography/threshold-ml-dsa-whitepaper-v1.1.md` | Threshold ML-DSA whitepaper |
| `docs/cryptography/threshold-mldsa-research.md` | ML-DSA research |
| `docs/cryptography/dealerless-dkg-threshold-mldsa.md` | Dealerless DKG |

### Frontend

| File | Description |
|------|-------------|
| `docs/frontend-motoswap-ui-README.md` | **Frontend guide (THE STANDARD)** |

---

### Guidelines (`guidelines/`)

| File | Description |
|------|-------------|
| `guidelines/audit-guidelines.md` | Security audit guide |
| `guidelines/backend-guidelines.md` | Backend development patterns |
| `guidelines/contracts-guidelines.md` | Smart contract patterns |
| `guidelines/ethereum-migration-guidelines.md` | **Ethereum to OPNet concept mapping guide** |
| `guidelines/frontend-guidelines.md` | Frontend development patterns |
| `guidelines/generic-questions-guidelines.md` | Topic routing for conceptual questions |
| `guidelines/plugin-guidelines.md` | Plugin development patterns |
| `guidelines/setup-guidelines.md` | Project setup and configuration |
| `guidelines/unit-testing-guidelines.md` | Unit testing patterns |

### How-To Guides (`how-to/`)

| File | Description |
|------|-------------|
| `how-to/airdrops.md` | Claim-based airdrop pattern (two-address system) |
| `how-to/contract-upgrades.md` | Upgradeable contract pattern with onUpdate |
| `how-to/dex-building.md` | NativeSwap DEX pattern |
| `how-to/eth-equivalents.md` | **ETH→OPNet feature mapping table** |
| `how-to/message-signing.md` | ML-DSA, Schnorr, ECDSA signing |
| `how-to/multisig.md` | Multisig transaction workflow |
| `how-to/offline-signing.md` | Air-gapped signing workflow |
| `how-to/oracle-integration.md` | Oracle integration pattern |
| `how-to/stablecoin.md` | Stablecoin contract pattern |

### References (`references/`)

| File | Description |
|------|-------------|
| `references/audit-checklists.md` | Audit checklists & vulnerability patterns |
| `references/complete-file-index.md` | This file |
| `references/known-frontend-mistakes.md` | Common frontend mistakes |
| `references/opnet-core-concepts.md` | Core concepts (CSV, NativeSwap, upgrades, P2MR, quantum) |
| `references/troubleshooting.md` | Common errors and fixes |

### Templates

#### Contract Templates (`templates/contracts/`)

| File | Description |
|------|-------------|
| `templates/contracts/OP20Token.ts` | OP20 token implementation |
| `templates/contracts/OP721NFT.ts` | OP721 NFT implementation |
| `templates/contracts/MyContract.ts` | Generic contract template |
| `templates/contracts/UpgradeableContract.ts` | Upgradeable contract template |
| `templates/contracts/index.ts` | Entry point / exports |

#### Frontend Templates (`templates/frontend/`)

| File | Description |
|------|-------------|
| `templates/frontend/App.tsx` | Main app component |
| `templates/frontend/OPNetProvider.tsx` | OPNet context provider |
| `templates/frontend/WalletConnect.tsx` | Wallet connection component |
| `templates/frontend/ContractInteraction.tsx` | Contract interaction component |
| `templates/frontend/useWallet.ts` | Wallet hook |
| `templates/frontend/useContract.ts` | Contract hook |
| `templates/frontend/vite.config.ts` | Vite configuration |
| `templates/frontend/package.json` | Package dependencies |

#### Plugin Templates (`templates/plugins/`)

| File | Description |
|------|-------------|
| `templates/plugins/MyPlugin.ts` | Generic plugin template |
| `templates/plugins/OP20Indexer.ts` | OP20 indexer plugin |
| `templates/plugins/types.ts` | Type definitions |
| `templates/plugins/index.ts` | Entry point |
| `templates/plugins/plugin.json` | Plugin manifest |

#### Test Templates (`templates/tests/`)

| File | Description |
|------|-------------|
| `templates/tests/OP20.test.ts` | OP20 test example |
| `templates/tests/OP721.test.ts` | OP721 NFT test example |
| `templates/tests/CustomContract.test.ts` | Custom contract test example |
| `templates/tests/setup.ts` | Test setup |

---
