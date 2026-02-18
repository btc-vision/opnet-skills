import { opnet, OPNetUnit, Assert, Blockchain } from '@btc-vision/unit-test-framework';
import { ContractRuntime, BytecodeManager } from '@btc-vision/unit-test-framework';
import { Address, BinaryWriter, BinaryReader } from '@btc-vision/transaction';

/**
 * Custom Contract Unit Tests
 *
 * This test suite demonstrates how to test custom OPNet contracts
 * that are NOT OP20 or OP721 (those have built-in test classes).
 *
 * For custom contracts, you extend ContractRuntime and define
 * your contract's methods using the selector + execute pattern.
 *
 * KEY API NOTES:
 * - Constructor must call super({ address, deployer, gasLimit? })
 * - Override defineRequiredBytecodes() to load your .wasm file
 * - Encode selectors: Number(`0x${this.abiCoder.encodeSelector('method(types)')}`)
 * - Execute: this.execute({ calldata: writer.getBuffer(), sender?, txOrigin? })
 * - Decode response: new BinaryReader(result.response).readU256()
 * - Use this.executeThrowOnError() for methods that should revert on failure
 * - All numeric values use native bigint, NOT u256
 */

/**
 * Custom contract test wrapper.
 * Extend ContractRuntime to interact with your compiled .wasm contract.
 */
class MyContractRuntime extends ContractRuntime {
    // Encode selectors from ABI signatures (done once, reused for each call)
    private readonly getValueSelector: number = Number(
        `0x${this.abiCoder.encodeSelector('getValue()')}`,
    );
    private readonly setValueSelector: number = Number(
        `0x${this.abiCoder.encodeSelector('setValue(uint256)')}`,
    );
    private readonly incrementSelector: number = Number(
        `0x${this.abiCoder.encodeSelector('increment(uint256)')}`,
    );
    private readonly getOwnerSelector: number = Number(
        `0x${this.abiCoder.encodeSelector('getOwner()')}`,
    );
    private readonly isPausedSelector: number = Number(
        `0x${this.abiCoder.encodeSelector('isPaused()')}`,
    );
    private readonly pauseSelector: number = Number(
        `0x${this.abiCoder.encodeSelector('pause()')}`,
    );
    private readonly unpauseSelector: number = Number(
        `0x${this.abiCoder.encodeSelector('unpause()')}`,
    );

    constructor(deployer: Address, contractAddress: Address, gasLimit: bigint = 100_000_000_000_000n) {
        super({
            address: contractAddress,
            deployer: deployer,
            gasLimit,
        });
    }

    /**
     * Load the compiled .wasm bytecode for this contract.
     * Called automatically during init().
     */
    protected defineRequiredBytecodes(): void {
        BytecodeManager.loadBytecode('./bytecodes/MyContract.wasm', this.address);
    }

    /**
     * Get the stored value from the contract.
     */
    public async getValue(): Promise<bigint> {
        const calldata = new BinaryWriter();
        calldata.writeSelector(this.getValueSelector);

        const result = await this.executeThrowOnError({
            calldata: calldata.getBuffer(),
            saveStates: false,
        });

        const reader = new BinaryReader(result.response);
        return reader.readU256();
    }

    /**
     * Set a new value in the contract.
     * Pass sender explicitly in the execute params.
     */
    public async setValue(newValue: bigint, sender: Address): Promise<void> {
        const calldata = new BinaryWriter();
        calldata.writeSelector(this.setValueSelector);
        calldata.writeU256(newValue);

        await this.executeThrowOnError({
            calldata: calldata.getBuffer(),
            sender: sender,
            txOrigin: sender,
        });
    }

    /**
     * Increment the stored value.
     */
    public async increment(amount: bigint, sender: Address): Promise<bigint> {
        const calldata = new BinaryWriter();
        calldata.writeSelector(this.incrementSelector);
        calldata.writeU256(amount);

        const result = await this.executeThrowOnError({
            calldata: calldata.getBuffer(),
            sender: sender,
            txOrigin: sender,
        });

        const reader = new BinaryReader(result.response);
        return reader.readU256();
    }

    /**
     * Get the contract owner.
     */
    public async getOwner(): Promise<string> {
        const calldata = new BinaryWriter();
        calldata.writeSelector(this.getOwnerSelector);

        const result = await this.executeThrowOnError({
            calldata: calldata.getBuffer(),
            saveStates: false,
        });

        const reader = new BinaryReader(result.response);
        return reader.readStringWithLength();
    }

    /**
     * Check if contract is paused.
     */
    public async isPaused(): Promise<boolean> {
        const calldata = new BinaryWriter();
        calldata.writeSelector(this.isPausedSelector);

        const result = await this.executeThrowOnError({
            calldata: calldata.getBuffer(),
            saveStates: false,
        });

        const reader = new BinaryReader(result.response);
        return reader.readBoolean();
    }

    /**
     * Pause the contract (owner only).
     */
    public async pause(sender: Address): Promise<void> {
        const calldata = new BinaryWriter();
        calldata.writeSelector(this.pauseSelector);

        await this.executeThrowOnError({
            calldata: calldata.getBuffer(),
            sender: sender,
            txOrigin: sender,
        });
    }

    /**
     * Unpause the contract (owner only).
     */
    public async unpause(sender: Address): Promise<void> {
        const calldata = new BinaryWriter();
        calldata.writeSelector(this.unpauseSelector);

        await this.executeThrowOnError({
            calldata: calldata.getBuffer(),
            sender: sender,
            txOrigin: sender,
        });
    }
}

await opnet('Custom Contract Tests', async (vm: OPNetUnit) => {
    const deployerAddress: Address = Blockchain.generateRandomAddress();
    const userAddress: Address = Blockchain.generateRandomAddress();

    let contract: MyContractRuntime;
    const contractAddress: Address = Blockchain.generateRandomAddress();

    vm.beforeEach(async () => {
        Blockchain.dispose();
        Blockchain.clearContracts();
        await Blockchain.init();

        contract = new MyContractRuntime(deployerAddress, contractAddress);
        Blockchain.register(contract);
        await contract.init();
    });

    vm.afterEach(() => {
        contract.dispose();
        Blockchain.dispose();
    });

    await vm.it('should initialize with default value', async () => {
        const value = await contract.getValue();
        Assert.expect(value.toString()).toEqual('100');
    });

    await vm.it('should set deployer as owner', async () => {
        const owner = await contract.getOwner();
        Assert.expect(owner).toBeDefined();
        Assert.expect(owner.length).toBeGreaterThan(0);
    });

    await vm.it('should set new value as deployer', async () => {
        await contract.setValue(500n, deployerAddress);

        const stored = await contract.getValue();
        Assert.expect(stored.toString()).toEqual('500');
    });

    await vm.it('should increment value correctly', async () => {
        const newValue = await contract.increment(50n, deployerAddress);
        Assert.expect(newValue.toString()).toEqual('150');
    });

    await vm.it('should start unpaused', async () => {
        const paused = await contract.isPaused();
        Assert.expect(paused).toEqual(false);
    });

    await vm.it('should allow owner to pause and unpause', async () => {
        await contract.pause(deployerAddress);
        let paused = await contract.isPaused();
        Assert.expect(paused).toEqual(true);

        await contract.unpause(deployerAddress);
        paused = await contract.isPaused();
        Assert.expect(paused).toEqual(false);
    });

    await vm.it('should prevent non-owner from pausing', async () => {
        await Assert.expect(async () => {
            await contract.pause(userAddress);
        }).toThrow();
    });

    await vm.it('should prevent operations when paused', async () => {
        await contract.pause(deployerAddress);

        await Assert.expect(async () => {
            await contract.setValue(999n, deployerAddress);
        }).toThrow();
    });

    await vm.it('should track gas consumption', async () => {
        Blockchain.enableGasTracking();

        await contract.setValue(42n, deployerAddress);

        // Gas is tracked per-call; read the value to get a CallResponse with usedGas
        const value = await contract.getValue();
        Assert.expect(value.toString()).toEqual('42');

        Blockchain.disableGasTracking();
    });
});
