import { opnet, OPNetUnit, Assert, Blockchain } from '@btc-vision/unit-test-framework';
import { OP721, BytecodeManager, ContractRuntime } from '@btc-vision/unit-test-framework';
import { Address, BinaryWriter, BinaryReader } from '@btc-vision/transaction';
import type { OP721Interface } from '@btc-vision/unit-test-framework';

/**
 * Custom OP721 test wrapper that adds a mint method.
 *
 * The base OP721 class does NOT include a mint() method because minting
 * logic varies per contract. You must extend OP721 and add your contract's
 * custom methods, similar to how you extend ContractRuntime for custom contracts.
 */
class TestOP721 extends OP721 {
    private readonly mintSelector: number = Number(
        `0x${this.abiCoder.encodeSelector('mint(address)')}`,
    );

    constructor(details: OP721Interface) {
        super(details);
    }

    /**
     * Mint a single NFT to the specified address.
     * Calls the contract's mint(address) method as the deployer.
     * Returns the minted token ID.
     */
    public async mint(to: Address): Promise<bigint> {
        const calldata = new BinaryWriter();
        calldata.writeSelector(this.mintSelector);
        calldata.writeAddress(to);

        const result = await this.executeThrowOnError({
            calldata: calldata.getBuffer(),
            sender: this.deployer,
            txOrigin: this.deployer,
        });

        const reader = new BinaryReader(result.response);
        return reader.readU256();
    }
}

/**
 * OP721 NFT Unit Tests
 *
 * This test suite demonstrates how to test OP721 NFT contracts.
 *
 * KEY API NOTES:
 * - OP721 constructor takes an object: { address, deployer, file }
 * - OP721 has NO built-in mint() -- extend the class and add it yourself
 * - transferFrom(from, to, tokenId: bigint, sender?: Address) -- sender defaults to from
 * - approve(spender, tokenId: bigint, sender: Address) -- 3 required args
 * - Built-in methods set sender/txOrigin internally -- no need for Blockchain.msgSender
 * - All token IDs and amounts use native bigint, NOT u256
 */
await opnet('OP721 NFT Tests', async (vm: OPNetUnit) => {
    const deployerAddress: Address = Blockchain.generateRandomAddress();
    const ownerAddress: Address = Blockchain.generateRandomAddress();
    const recipientAddress: Address = Blockchain.generateRandomAddress();
    const operatorAddress: Address = Blockchain.generateRandomAddress();

    let nft: TestOP721;
    const contractAddress: Address = Blockchain.generateRandomAddress();

    vm.beforeEach(async () => {
        Blockchain.dispose();
        Blockchain.clearContracts();
        await Blockchain.init();

        nft = new TestOP721({
            address: contractAddress,
            deployer: deployerAddress,
            file: './bytecodes/OP721NFT.wasm',
        });
        Blockchain.register(nft);
        await nft.init();
    });

    vm.afterEach(() => {
        nft.dispose();
        Blockchain.dispose();
    });

    await vm.it('should return correct collection name', async () => {
        const name = await nft.name();
        Assert.expect(name).toBeDefined();
        Assert.expect(typeof name).toEqual('string');
    });

    await vm.it('should return correct collection symbol', async () => {
        const symbol = await nft.symbol();
        Assert.expect(symbol).toBeDefined();
        Assert.expect(typeof symbol).toEqual('string');
    });

    await vm.it('should mint an NFT to an address', async () => {
        // mint() is our custom method -- returns the minted tokenId
        const tokenId = await nft.mint(ownerAddress);

        const owner = await nft.ownerOf(tokenId);
        Assert.expect(owner.equals(ownerAddress)).toEqual(true);
    });

    await vm.it('should return correct balance after minting', async () => {
        await nft.mint(ownerAddress);
        await nft.mint(ownerAddress);

        const balance = await nft.balanceOf(ownerAddress);
        Assert.expect(balance.toString()).toEqual('2');
    });

    await vm.it('should transfer NFT between addresses', async () => {
        const tokenId = await nft.mint(ownerAddress);

        // transferFrom(from, to, tokenId, sender?) -- sender defaults to from
        await nft.transferFrom(ownerAddress, recipientAddress, tokenId);

        const newOwner = await nft.ownerOf(tokenId);
        Assert.expect(newOwner.equals(recipientAddress)).toEqual(true);
    });

    await vm.it('should approve operator for a specific token', async () => {
        const tokenId = await nft.mint(ownerAddress);

        // approve(spender, tokenId, sender) -- 3 required args
        await nft.approve(operatorAddress, tokenId, ownerAddress);

        const approved = await nft.getApproved(tokenId);
        Assert.expect(approved.equals(operatorAddress)).toEqual(true);
    });

    await vm.it('should allow approved operator to transfer', async () => {
        const tokenId = await nft.mint(ownerAddress);

        await nft.approve(operatorAddress, tokenId, ownerAddress);

        // transferFrom with explicit sender (the approved operator)
        await nft.transferFrom(ownerAddress, recipientAddress, tokenId, operatorAddress);

        const newOwner = await nft.ownerOf(tokenId);
        Assert.expect(newOwner.equals(recipientAddress)).toEqual(true);
    });

    await vm.it('should revert transfer from non-owner/non-approved', async () => {
        const tokenId = await nft.mint(ownerAddress);

        await Assert.expect(async () => {
            // recipientAddress is neither owner nor approved
            await nft.transferFrom(ownerAddress, recipientAddress, tokenId, recipientAddress);
        }).toThrow();
    });

    await vm.it('should track gas consumption', async () => {
        Blockchain.enableGasTracking();

        const tokenId = await nft.mint(ownerAddress);

        // Gas is tracked per-call on CallResponse.usedGas
        const result = await nft.transferFrom(ownerAddress, recipientAddress, tokenId);
        Assert.expect(result.usedGas).toBeGreaterThan(0n);

        Blockchain.disableGasTracking();
    });
});
