import { useState, useEffect, useMemo } from 'react';
import { Address } from 'opnet';
import { useOP20 } from '../hooks/useContract';
import { useWallet } from '../hooks/useWallet';
import { formatUnits } from 'opnet';

interface ContractInteractionProps {
    contractAddress: string;
}

/**
 * ContractInteraction Component
 *
 * Example component for interacting with an OP20 token contract.
 * Demonstrates:
 * - Using .metadata() for efficient batch retrieval (1 RPC call)
 * - Proper Address.fromString(hashedMLDSAKey, publicKey) usage
 * - Correct wallet data access patterns
 */
export function ContractInteraction({ contractAddress }: ContractInteractionProps) {
    const { hashedMLDSAKey, publicKey, isConnected } = useWallet();

    /** Construct sender Address from wallet keys for contract interaction */
    const senderAddress = useMemo(() => {
        if (!hashedMLDSAKey || !publicKey) return undefined;
        return Address.fromString(hashedMLDSAKey, publicKey);
    }, [hashedMLDSAKey, publicKey]);

    const { getMetadata, getBalanceOf, loading, error } = useOP20(contractAddress, senderAddress);

    const [tokenInfo, setTokenInfo] = useState<{
        name: string | null;
        symbol: string | null;
        decimals: number | null;
        totalSupply: bigint | null;
    }>({
        name: null,
        symbol: null,
        decimals: null,
        totalSupply: null,
    });

    const [balance, setBalance] = useState<bigint | null>(null);

    /** Load all token metadata in a single RPC call */
    useEffect(() => {
        const loadTokenInfo = async () => {
            const metadata = await getMetadata();
            if (metadata) {
                setTokenInfo({
                    name: metadata.name,
                    symbol: metadata.symbol,
                    decimals: metadata.decimals,
                    totalSupply: metadata.totalSupply,
                });
            }
        };

        loadTokenInfo();
    }, [getMetadata]);

    /** Load user balance when connected */
    useEffect(() => {
        const loadBalance = async () => {
            if (isConnected && senderAddress) {
                const bal = await getBalanceOf(senderAddress);
                setBalance(bal);
            } else {
                setBalance(null);
            }
        };

        loadBalance();
    }, [isConnected, senderAddress, getBalanceOf]);

    const formatBalance = (bal: bigint | null, decimals: number | null): string => {
        if (bal === null || decimals === null) return '0';
        return formatUnits(bal, decimals);
    };

    return (
        <div className="contract-interaction">
            <h2>Token Information</h2>

            {loading && <p className="loading">Loading...</p>}
            {error && <p className="error">{error.message}</p>}

            <div className="token-info">
                <div className="info-row">
                    <span className="label">Name:</span>
                    <span className="value">{tokenInfo.name ?? '-'}</span>
                </div>
                <div className="info-row">
                    <span className="label">Symbol:</span>
                    <span className="value">{tokenInfo.symbol ?? '-'}</span>
                </div>
                <div className="info-row">
                    <span className="label">Decimals:</span>
                    <span className="value">{tokenInfo.decimals ?? '-'}</span>
                </div>
                <div className="info-row">
                    <span className="label">Total Supply:</span>
                    <span className="value">
                        {formatBalance(tokenInfo.totalSupply, tokenInfo.decimals)}{' '}
                        {tokenInfo.symbol}
                    </span>
                </div>
            </div>

            {isConnected && (
                <div className="user-info">
                    <h3>Your Balance</h3>
                    <p className="balance">
                        {formatBalance(balance, tokenInfo.decimals)} {tokenInfo.symbol}
                    </p>
                </div>
            )}
        </div>
    );
}
