# OPNet dApp Template

A production-ready React frontend template for OPNet dApps.

## Features

- React 19 with TypeScript
- Vite for fast development and builds
- OPNet provider integration (JSON-RPC + WebSocket)
- Wallet connection (OP Wallet, Unisat)
- Contract interaction hooks
- Responsive design with Bitcoin orange theme

## Quick Start

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```

3. **Build for production:**
   ```bash
   npm run build
   ```

## Project Structure

```
opnet-dapp/
├── src/
│   ├── components/         # React components
│   │   ├── WalletConnect.tsx
│   │   └── ContractInteraction.tsx
│   ├── hooks/              # Custom hooks
│   │   ├── useContract.ts
│   │   └── useWallet.ts
│   ├── providers/          # Context providers
│   │   └── OPNetProvider.tsx
│   ├── App.tsx             # Main app component
│   ├── App.css             # App styles
│   ├── main.tsx            # Entry point
│   └── index.css           # Global styles
├── index.html
├── package.json
├── tsconfig.json
├── tsconfig.app.json
├── tsconfig.node.json
├── vite.config.ts
├── .prettierrc
└── README.md
```

## Using the OPNet Provider

```tsx
import { OPNetProvider, useOPNet } from './providers/OPNetProvider';

// Wrap your app
<OPNetProvider defaultNetwork="regtest">
    <App />
</OPNetProvider>

// Use in components
const { provider, isConnected, network, switchNetwork } = useOPNet();
```

## Using the Contract Hook

```tsx
import { useOP20 } from './hooks/useContract';

const { getName, getSymbol, getBalanceOf, loading, error } = useOP20(contractAddress);

// Call methods
const name = await getName();
const balance = await getBalanceOf(address);
```

## Using the Wallet Hook

```tsx
import { useWallet } from './hooks/useWallet';

const { address, isConnected, connect, disconnect, signMessage, signPsbt } = useWallet();

// Connect wallet
await connect();

// Sign message
const signature = await signMessage('Hello OPNet');
```

## Configuration Standards

This template follows the motoswap-ui configuration standards:
- TypeScript strict mode
- ES2020+ target
- Vite with manual chunk splitting
- Prettier formatting (4 space indent, single quotes)
- Node polyfills for crypto libraries

## Customization

1. **Change network** in `OPNetProvider`:
   ```tsx
   <OPNetProvider defaultNetwork="mainnet">
   ```

2. **Add your contract address** in `App.tsx`:
   ```tsx
   const CONTRACT_ADDRESS = 'bcrt1p...';
   ```

3. **Add custom hooks** in `src/hooks/`

4. **Add components** in `src/components/`

## Testing

```bash
npm run test
```

## Linting & Formatting

```bash
npm run lint
npm run format
```
