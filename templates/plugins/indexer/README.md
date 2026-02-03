# OP20 Indexer Plugin

An OPNet node plugin that indexes OP20 token transfers and maintains holder balances.

## Overview

OPNet nodes are like Minecraft servers - they support plugins! This plugin demonstrates how to:
- Process blocks and transactions
- Store data in the plugin database (MongoDB)
- Handle chain reorganizations
- Expose custom API endpoints

## Features

- Tracks all OP20 token transfers
- Maintains holder balances per token
- Exposes REST API for querying token data
- Handles chain reorganizations correctly

## Installation

1. **Build the plugin:**
   ```bash
   npm install
   npm run build
   ```

2. **Install to OPNet node:**
   ```bash
   opnet-cli plugin install ./dist/op20-indexer.opnet
   ```

3. **Enable the plugin:**
   ```bash
   opnet-cli plugin enable op20-indexer
   ```

## API Endpoints

Once installed, the plugin exposes these endpoints:

### List Tokens
```
GET /api/plugins/op20-indexer/tokens
```

### Get Token Holders
```
GET /api/plugins/op20-indexer/holders/:tokenAddress
```

### Get Balance
```
GET /api/plugins/op20-indexer/balance/:tokenAddress/:holderAddress
```

### Get Transfers
```
GET /api/plugins/op20-indexer/transfers/:tokenAddress?limit=50
```

## Plugin Lifecycle

### Hooks Called on Every Load
- `onLoad()` - Plugin loaded
- `onNetworkInit()` - Network initialized

### Hooks Called Once
- `onFirstInstall()` - First time installation (create indexes)

### Sync Hooks (Blocking)
- `onSyncRequired()` - Check if sync is needed
- `onSyncBlock()` - Process historical block
- `onSyncComplete()` - Sync finished

### Block Processing Hooks
- `onBlockChange()` - New block confirmed (live mode)

### Critical Hooks (MUST Implement)
- `onReorg()` - Chain reorganization - **MUST revert state**
- `onPurgeBlocks()` - Delete data for block range

## Permissions

This plugin requires the following permissions in `plugin.json`:

```json
{
    "database": { "enabled": true, "collections": [...] },
    "blocks": { "postProcess": true, "onChange": true },
    "api": { "addEndpoints": true },
    "blockchain": { "blocks": true, "transactions": true }
}
```

## Development

### Directory Structure

```
indexer/
├── src/
│   ├── index.ts        # Plugin entry point
│   ├── OP20Indexer.ts  # Main plugin class
│   └── types.ts        # Type definitions
├── plugin.json         # Plugin manifest
├── package.json
├── tsconfig.json
└── README.md
```

### Key Concepts

1. **Extend PluginBase**: Your plugin class must extend `PluginBase`
2. **Handle Reorgs**: Always implement `onReorg()` to maintain data consistency
3. **Track Sync State**: Use `context.updateLastSyncedBlock()` to track progress
4. **Use Permissions**: Only request permissions you actually need

## Building for Production

1. Compile TypeScript: `npm run build`
2. Compile to Bytenode: `npm run compile`
3. Package as `.opnet` file using opnet-cli

## References

- [OIP-0003: Plugin System](../../docs/core/OIP/OIP-0003.md)
- [Plugin SDK Documentation](../../docs/plugins/plugin-sdk/)
- [OPNet Node Documentation](../../docs/plugins/opnet-node/)
