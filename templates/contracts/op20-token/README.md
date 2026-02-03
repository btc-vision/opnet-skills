# OP20 Token Template

A production-ready OP20 fungible token for OPNet.

## Features

- Standard OP20 interface (ERC20-like)
- Minting with deployer-only access control
- Batch airdrop functionality
- Max supply enforcement
- Burn functionality

## Quick Start

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Customize your token** in `assembly/OP20Token.ts`:
   ```typescript
   const maxSupply: u256 = u256.fromString('1000000000000000000000000000');
   const decimals: u8 = 18;
   const name: string = 'My Token';
   const symbol: string = 'MTK';
   ```

3. **Build the contract:**
   ```bash
   npm run build
   ```

4. **Deploy** using OPNet transaction builder.

## Contract Methods

### Standard OP20 (inherited)
- `name()` - Token name
- `symbol()` - Token symbol
- `decimals()` - Number of decimals
- `totalSupply()` - Total supply
- `balanceOf(address)` - Balance of address
- `transfer(to, amount)` - Transfer tokens
- `approve(spender, amount)` - Approve spender
- `allowance(owner, spender)` - Check allowance
- `transferFrom(from, to, amount)` - Transfer from approved

### Custom Methods
- `mint(to, amount)` - Mint tokens (deployer only)
- `airdrop(recipients)` - Batch mint (deployer only)
- `burn(amount)` - Burn tokens from caller

## Security Notes

- Only the contract deployer can mint tokens
- Max supply is enforced - minting beyond max will revert
- All math operations use SafeMath to prevent overflow

## Directory Structure

```
op20-token/
├── assembly/
│   ├── index.ts        # Entry point (DO NOT MODIFY)
│   ├── OP20Token.ts    # Your token implementation
│   └── tsconfig.json   # TypeScript config
├── asconfig.json       # AssemblyScript build config
├── package.json        # Dependencies
└── README.md           # This file
```

## Testing

Use the unit-test-framework to test your contract before deployment.
See `/templates/tests/contract-tests/` for examples.
