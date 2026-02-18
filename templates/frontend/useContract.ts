import { useState, useCallback, useMemo } from 'react';
import { getContract, IOP20Contract, OP_20_ABI, BitcoinInterfaceAbi } from 'opnet';
import { Address } from '@btc-vision/transaction';
import { useOPNet } from '../providers/OPNetProvider';

/**
 * Hook for interacting with OPNet smart contracts.
 *
 * @param contractAddress - The contract address (P2OP format or hex)
 * @param abi - Contract ABI definition
 * @param senderAddress - The sender's Address object (from Address.fromString(hashedMLDSAKey, publicKey))
 * @returns Contract instance and helper methods
 */
export function useContract<T>(
    contractAddress: string,
    abi: BitcoinInterfaceAbi,
    senderAddress?: Address,
) {
    const { provider, network, isConnected } = useOPNet();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<Error | null>(null);

    const contract = useMemo(() => {
        if (!provider || !isConnected) {
            return null;
        }
        try {
            return getContract<T>(contractAddress, abi, provider, network, senderAddress);
        } catch {
            return null;
        }
    }, [provider, isConnected, contractAddress, abi, network, senderAddress]);

    return {
        contract,
        loading,
        setLoading,
        error,
        setError,
        isConnected,
    };
}

/**
 * Token metadata returned from a single .metadata() RPC call.
 */
interface TokenMetadata {
    name: string;
    symbol: string;
    decimals: number;
    totalSupply: bigint;
    owner: string;
}

/**
 * Hook for interacting with OP20 token contracts.
 * Provides type-safe methods for all standard OP20 operations.
 *
 * Uses .metadata() for efficient batch retrieval (1 RPC call instead of 4).
 *
 * @param contractAddress - The token contract address
 * @param senderAddress - The sender's Address object (from Address.fromString(hashedMLDSAKey, publicKey))
 * @returns Token methods and state
 */
export function useOP20(contractAddress: string, senderAddress?: Address) {
    const { provider, network, isConnected } = useOPNet();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<Error | null>(null);

    const contract = useMemo(() => {
        if (!provider || !isConnected) {
            return null;
        }
        try {
            return getContract<IOP20Contract>(
                contractAddress,
                OP_20_ABI,
                provider,
                network,
                senderAddress,
            );
        } catch {
            return null;
        }
    }, [provider, isConnected, contractAddress, network, senderAddress]);

    /**
     * Fetch all token metadata in a single RPC call.
     * Returns name, symbol, decimals, totalSupply, and owner.
     *
     * @returns Token metadata or null if unavailable
     */
    const getMetadata = useCallback(async (): Promise<TokenMetadata | null> => {
        if (!contract) return null;
        setLoading(true);
        setError(null);
        try {
            const result = await contract.metadata();
            return result.decoded as TokenMetadata;
        } catch (err) {
            setError(err instanceof Error ? err : new Error(String(err)));
            return null;
        } finally {
            setLoading(false);
        }
    }, [contract]);

    /**
     * Get the balance of an address.
     *
     * @param address - The address to check
     * @returns The balance in base units or null
     */
    const getBalanceOf = useCallback(
        async (address: Address): Promise<bigint | null> => {
            if (!contract) return null;
            setLoading(true);
            setError(null);
            try {
                const result = await contract.balanceOf(address);
                return result.properties.balance;
            } catch (err) {
                setError(err instanceof Error ? err : new Error(String(err)));
                return null;
            } finally {
                setLoading(false);
            }
        },
        [contract],
    );

    /**
     * Get the allowance for a spender on an owner's tokens.
     *
     * @param owner - The token owner address
     * @param spender - The spender address
     * @returns The remaining allowance or null
     */
    const getAllowance = useCallback(
        async (owner: Address, spender: Address): Promise<bigint | null> => {
            if (!contract) return null;
            setLoading(true);
            setError(null);
            try {
                const result = await contract.allowance(owner, spender);
                return result.properties.remaining;
            } catch (err) {
                setError(err instanceof Error ? err : new Error(String(err)));
                return null;
            } finally {
                setLoading(false);
            }
        },
        [contract],
    );

    return {
        contract,
        loading,
        error,
        isConnected,
        getMetadata,
        getBalanceOf,
        getAllowance,
    };
}
