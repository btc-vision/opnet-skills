# Generic OPNet Plugin Template

A minimal OPNet node plugin template.

## Quick Start

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Build:**
   ```bash
   npm run build
   ```

3. **Install to node:**
   ```bash
   opnet-cli plugin install ./dist/my-plugin.opnet
   ```

## Plugin Hooks

| Hook | When Called | Blocking |
|------|-------------|----------|
| `onLoad` | Plugin loaded | No |
| `onUnload` | Plugin unloading | No |
| `onFirstInstall` | First installation | Yes |
| `onNetworkInit` | Network initialized | Yes |
| `onBlockChange` | New block confirmed | No |
| `onReorg` | Chain reorganization | Yes |

## Permissions

Edit `plugin.json` to request only the permissions you need.

## References

- [OIP-0003: Plugin System](../../docs/core/OIP/OIP-0003.md)
- [Plugin SDK](../../docs/plugins/plugin-sdk/)
