# OP721 NFT Template

A production-ready OP721 non-fungible token for OPNet.

## Features

- Standard OP721 interface (ERC721-like)
- Minting with deployer-only access control
- Batch airdrop functionality
- Max supply enforcement
- Token URI support
- Burn functionality

## Quick Start

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Customize your NFT** in `assembly/OP721NFT.ts`:
   ```typescript
   const maxSupply: u256 = u256.fromU32(10000);
   const name: string = 'My NFT Collection';
   const symbol: string = 'MNFT';
   const baseURI: string = 'https://api.example.com/metadata/';
   ```

3. **Build the contract:**
   ```bash
   npm run build
   ```

4. **Deploy** using OPNet transaction builder.

## Contract Methods

### Standard OP721 (inherited)
- `name()` - Collection name
- `symbol()` - Collection symbol
- `totalSupply()` - Total minted
- `ownerOf(tokenId)` - Owner of token
- `balanceOf(owner)` - Number of tokens owned
- `tokenURI(tokenId)` - Metadata URI
- `approve(to, tokenId)` - Approve transfer
- `getApproved(tokenId)` - Get approved address
- `setApprovalForAll(operator, approved)` - Set operator
- `isApprovedForAll(owner, operator)` - Check operator
- `transferFrom(from, to, tokenId)` - Transfer token
- `safeTransferFrom(from, to, tokenId)` - Safe transfer

### Custom Methods
- `setMintEnabled(enabled)` - Enable/disable minting
- `isMintEnabled()` - Check mint status
- `mint(to)` - Mint single NFT (deployer only)
- `airdrop(addresses, amounts)` - Batch mint (deployer only)
- `setTokenURI(tokenId, uri)` - Set token URI (deployer only)
- `burn(tokenId)` - Burn token (owner only)
- `getStatus()` - Get minted/available/max supply

## Security Notes

- Only the contract deployer can mint NFTs
- Max supply is enforced
- Only token owner can burn their token
- All math uses SafeMath to prevent overflow

## Directory Structure

```
op721-nft/
├── assembly/
│   ├── index.ts        # Entry point (DO NOT MODIFY)
│   ├── OP721NFT.ts     # Your NFT implementation
│   └── tsconfig.json   # TypeScript config
├── asconfig.json       # AssemblyScript build config
├── package.json        # Dependencies
└── README.md           # This file
```
