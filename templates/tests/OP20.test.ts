import { opnet, OPNetUnit, Assert, Blockchain } from '@btc-vision/unit-test-framework';
import { OP20 } from '@btc-vision/unit-test-framework';
import { Address } from '@btc-vision/transaction';

/**
 * OP20 Token Unit Tests
 *
 * This test suite demonstrates how to test OP20 token contracts.
 * Use this as a template for your own contract tests.
 *
 * KEY API NOTES:
 * - OP20 constructor takes an object: { address, deployer, file, decimals }
 * - mint(to, amount: number) uses whole units; mintRaw(to, amount: bigint) uses raw units
 * - Use safeTransfer(from, to, amount) instead of transfer(to, amount)
 * - Use increaseAllowance(owner, spender, amount) instead of approve(spender, amount)
 * - Use safeTransferFrom(from, to, amount) instead of transferFrom(from, to, amount)
 * - OP20 has NO name() or symbol() methods -- use metadata() instead
 * - decimals is a readonly property (token.decimals), NOT an async method
 * - Built-in methods set sender/txOrigin internally -- no need for Blockchain.msgSender
 * - Events are on CallResponse.events, not on the contract instance
 * - Gas is on CallResponse.usedGas, not on Blockchain
 */
await opnet('OP20 Token Tests', async (vm: OPNetUnit) => {
    // Test addresses
    const deployerAddress: Address = Blockchain.generateRandomAddress();
    const userAddress: Address = Blockchain.generateRandomAddress();
    const recipientAddress: Address = Blockchain.generateRandomAddress();

    // Contract instance
    let token: OP20;

    // Contract address
    const contractAddress: Address = Blockchain.generateRandomAddress();

    /**
     * Setup before each test
     */
    vm.beforeEach(async () => {
        // Clean up previous state
        Blockchain.dispose();
        Blockchain.clearContracts();

        // Initialize blockchain
        await Blockchain.init();

        // Create and register contract (object constructor with file path and decimals)
        token = new OP20({
            address: contractAddress,
            deployer: deployerAddress,
            file: './bytecodes/OP20Token.wasm',
            decimals: 18,
        });
        Blockchain.register(token);

        // Initialize the contract (runs onDeployment)
        await token.init();
    });

    /**
     * Cleanup after each test
     */
    vm.afterEach(() => {
        token.dispose();
        Blockchain.dispose();
    });

    await vm.it('should return correct token metadata', async () => {
        // OP20 has no name() or symbol() methods -- use metadata() instead
        const { metadata } = await token.metadata();

        Assert.expect(metadata.name).toBeDefined();
        Assert.expect(typeof metadata.name).toEqual('string');

        Assert.expect(metadata.symbol).toBeDefined();
        Assert.expect(typeof metadata.symbol).toEqual('string');

        Assert.expect(metadata.decimals).toBeGreaterThanOrEqual(0);
        Assert.expect(metadata.decimals).toBeLessThanOrEqual(18);
    });

    await vm.it('should have correct decimals property', async () => {
        // decimals is a readonly property on the OP20 instance, NOT an async method
        const decimals = token.decimals;
        Assert.expect(decimals).toEqual(18);
    });

    await vm.it('should return zero balance for new address', async () => {
        const balance = await token.balanceOf(userAddress);
        Assert.expect(balance.toString()).toEqual('0');
    });

    await vm.it('should return correct balance after mint', async () => {
        // mint(to, amount: number) uses whole units -- sender is automatically set to deployer
        await token.mint(userAddress, 1000);

        // Check balance (returns bigint in raw units)
        const balance = await token.balanceOf(userAddress);
        Assert.expect(balance).toBeGreaterThan(0n);
    });

    await vm.it('should mint raw amount correctly', async () => {
        const rawAmount = 1_000_000_000_000_000_000_000n; // 1000 * 10^18

        // mintRaw(to, amount: bigint) uses raw units -- sender is automatically set to deployer
        await token.mintRaw(userAddress, rawAmount);

        const balance = await token.balanceOf(userAddress);
        Assert.expect(balance.toString()).toEqual(rawAmount.toString());
    });

    await vm.it('should transfer tokens successfully', async () => {
        const transferAmount = 100_000_000_000_000_000_000n; // 100 * 10^18

        // Mint to user first
        await token.mint(userAddress, 1000);

        // safeTransfer(from, to, amount) -- sender is automatically set to `from`
        await token.safeTransfer(userAddress, recipientAddress, transferAmount);

        // Check balances
        const recipientBalance = await token.balanceOf(recipientAddress);
        Assert.expect(recipientBalance.toString()).toEqual(transferAmount.toString());
    });

    await vm.it('should revert transfer with insufficient balance', async () => {
        const transferAmount = 100_000_000_000_000_000_000n;

        await Assert.expect(async () => {
            await token.safeTransfer(userAddress, recipientAddress, transferAmount);
        }).toThrow();
    });

    await vm.it('should increase allowance correctly', async () => {
        const allowanceAmount = 500_000_000_000_000_000_000n; // 500 * 10^18

        // increaseAllowance(owner, spender, amount) -- sender is automatically set to `owner`
        await token.increaseAllowance(userAddress, recipientAddress, allowanceAmount);

        const allowance = await token.allowance(userAddress, recipientAddress);
        Assert.expect(allowance.toString()).toEqual(allowanceAmount.toString());
    });

    await vm.it('should execute safeTransferFrom with allowance', async () => {
        const allowanceAmount = 500_000_000_000_000_000_000n;
        const transferAmount = 200_000_000_000_000_000_000n;

        // Mint to user
        await token.mint(userAddress, 1000);

        // Increase allowance for recipient
        await token.increaseAllowance(userAddress, recipientAddress, allowanceAmount);

        // safeTransferFrom(from, to, amount) -- sender is automatically set to `from`
        await token.safeTransferFrom(userAddress, recipientAddress, transferAmount);

        // Check balances
        const recipientBalance = await token.balanceOf(recipientAddress);
        Assert.expect(recipientBalance.toString()).toEqual(transferAmount.toString());

        // Check remaining allowance
        const remainingAllowance = await token.allowance(userAddress, recipientAddress);
        Assert.expect(remainingAllowance.toString()).toEqual(
            (allowanceAmount - transferAmount).toString(),
        );
    });

    await vm.it('should emit events on transfer', async () => {
        // Mint to user
        await token.mint(userAddress, 1000);

        const transferAmount = 100_000_000_000_000_000_000n;

        // safeTransfer returns CallResponse which contains events
        const result = await token.safeTransfer(userAddress, recipientAddress, transferAmount);

        // Events are on the CallResponse
        Assert.expect(result.events.length).toBeGreaterThan(0);
    });

    await vm.it('should track gas consumption', async () => {
        Blockchain.enableGasTracking();

        await token.mint(userAddress, 1000);

        // Gas is tracked per-call on CallResponse.usedGas
        const transferAmount = 100_000_000_000_000_000_000n;
        const result = await token.safeTransfer(userAddress, recipientAddress, transferAmount);
        Assert.expect(result.usedGas).toBeGreaterThan(0n);

        Blockchain.disableGasTracking();
    });
});
