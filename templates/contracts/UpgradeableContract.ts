import { u256 } from '@btc-vision/as-bignum/assembly';
import {
    Address,
    Blockchain,
    BytesWriter,
    Calldata,
    Revert,
    SafeMath,
    StoredString,
    StoredU256,
    U256_BYTE_LENGTH,
    Upgradeable,
} from '@btc-vision/btc-runtime/runtime';

// Storage pointers - each must be unique
const ownerPointer: u16 = Blockchain.nextPointer;
const valuePointer: u16 = Blockchain.nextPointer;
const versionPointer: u16 = Blockchain.nextPointer;

/**
 * UpgradeableContract - An upgradeable OPNet smart contract template
 *
 * This template demonstrates:
 * - Extending the Upgradeable base class (instead of OP_NET)
 * - Implementing the onUpdate() lifecycle hook for safe upgrades
 * - Storage migration patterns between contract versions
 * - Access control for upgrade operations
 *
 * IMPORTANT:
 * - Extend Upgradeable instead of OP_NET for upgrade support
 * - The onUpdate() method is called after the contract bytecode is replaced
 * - Use onUpdate() to migrate storage layouts between versions
 * - Constructor runs on EVERY interaction (NOT just deployment)
 * - Use onDeployment() for one-time initialization
 */
@final
export class UpgradeableContract extends Upgradeable {
    private readonly owner: StoredString;
    private readonly storedValue: StoredU256;
    private readonly contractVersion: StoredU256;

    public constructor() {
        super();
        this.owner = new StoredString(ownerPointer);
        this.storedValue = new StoredU256(valuePointer, u256.Zero);
        this.contractVersion = new StoredU256(versionPointer, u256.Zero);
    }

    /**
     * One-time initialization on first deployment.
     */
    public override onDeployment(_calldata: Calldata): void {
        this.owner.value = Blockchain.tx.origin.p2tr();
        this.storedValue.value = u256.fromU32(100);
        this.contractVersion.value = u256.fromU32(1);
    }

    /**
     * Called after a contract upgrade (bytecode replacement).
     * Use this to migrate storage layouts between versions.
     *
     * @param oldVersion - The version hash of the previous contract code
     * @param calldata - Optional calldata for migration parameters
     */
    public override onUpdate(_oldVersion: u256, calldata: Calldata): void {
        // Ensure only the owner can trigger upgrades
        if (Blockchain.tx.sender.p2tr() !== this.owner.value) {
            throw new Revert('Not owner');
        }

        // Increment version counter
        const currentVersion: u256 = this.contractVersion.value;
        this.contractVersion.value = SafeMath.add(currentVersion, u256.One);

        // Example: Storage migration between versions
        // If upgrading from v1 to v2, you might need to:
        // - Add new storage fields
        // - Transform existing data formats
        // - Set default values for new fields
        //
        // const newFieldPointer: u16 = Blockchain.nextPointer;
        // const newField = new StoredU256(newFieldPointer, u256.Zero);
        // newField.value = calldata.readU256(); // Read migration param
    }

    /**
     * Ensures the caller is the contract owner.
     */
    private ensureOwner(): void {
        if (Blockchain.tx.sender.p2tr() !== this.owner.value) {
            throw new Revert('Not owner');
        }
    }

    /**
     * Get the current contract version.
     */
    @method()
    @returns({ name: 'version', type: ABIDataTypes.UINT256 })
    public getVersion(_: Calldata): BytesWriter {
        const response: BytesWriter = new BytesWriter(U256_BYTE_LENGTH);
        response.writeU256(this.contractVersion.value);
        return response;
    }

    /**
     * Get the current stored value.
     */
    @method()
    @returns({ name: 'value', type: ABIDataTypes.UINT256 })
    public getValue(_: Calldata): BytesWriter {
        const response: BytesWriter = new BytesWriter(U256_BYTE_LENGTH);
        response.writeU256(this.storedValue.value);
        return response;
    }

    /**
     * Set a new value (owner only).
     */
    @method({ name: 'newValue', type: ABIDataTypes.UINT256 })
    public setValue(calldata: Calldata): BytesWriter {
        this.ensureOwner();

        const newValue: u256 = calldata.readU256();
        this.storedValue.value = newValue;

        return new BytesWriter(0);
    }

    /**
     * Transfer ownership (owner only).
     */
    @method({ name: 'newOwner', type: ABIDataTypes.ADDRESS })
    public transferOwnership(calldata: Calldata): BytesWriter {
        this.ensureOwner();

        const newOwner: Address = calldata.readAddress();
        this.owner.value = newOwner.p2tr();

        return new BytesWriter(0);
    }
}
