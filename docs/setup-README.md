# OPNet Project Setup Templates

This folder contains shared configuration templates for OPNet projects. Copy the relevant files to your project root.

## Configuration Files

| File | Use For | Copy To |
|------|---------|---------|
| `.prettierrc` | All OPNet projects | Project root |
| `eslint-contract.js` | Smart contracts (btc-runtime) | `eslint.config.js` |
| `eslint-generic.js` | TypeScript libs / backends / plugins | `eslint.config.js` |
| `eslint-react.js` | React/Next.js frontends | `eslint.config.js` |
| `tsconfig-generic.json` | TypeScript projects (NOT contracts) | `tsconfig.json` |
| `asconfig.json` | AssemblyScript contracts | Project root |

## Quick Setup

### Smart Contract Project (btc-runtime)

```bash
cp setup/.prettierrc .prettierrc
cp setup/eslint-contract.js eslint.config.js
cp setup/asconfig.json asconfig.json
```

### TypeScript Library / Backend / Plugin

```bash
cp setup/.prettierrc .prettierrc
cp setup/eslint-generic.js eslint.config.js
cp setup/tsconfig-generic.json tsconfig.json
```

### React/Next.js Frontend

```bash
cp setup/.prettierrc .prettierrc
cp setup/eslint-react.js eslint.config.js
```

## Notes

- **Contracts**: Use `asconfig.json` for AssemblyScript. Do NOT use `tsconfig-generic.json` for contracts.
- **ESLint**: Uses ESLint 10 flat config format. Copy as `eslint.config.js` (NOT `.eslintrc.json`).
- **All configs**: Use ESNext target and strict TypeScript settings.
- **Dependencies**: Install `eslint @eslint/js typescript-eslint` as devDependencies. For React, also install `eslint-plugin-react-hooks eslint-plugin-react-refresh`.
