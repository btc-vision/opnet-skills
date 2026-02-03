import { useState, useCallback } from 'react';
import { useWalletConnect } from '@btc-vision/walletconnect';
import { Address } from '@btc-vision/transaction';

/**
 * Hook for wallet connection and management.
 * Provides methods for connecting, disconnecting, and signing with OPNet-compatible wallets.
 *
 * @returns Wallet state and action methods
 */
export function useWallet() {
    const walletConnect = useWalletConnect();
    const [isConnecting, setIsConnecting] = useState(false);
    const [error, setError] = useState<Error | null>(null);

    /**
     * Connect to an available wallet.
     */
    const connect = useCallback(async () => {
        setIsConnecting(true);
        setError(null);

        try {
            await walletConnect.requestConnection();
        } catch (err) {
            const connectError = err instanceof Error ? err : new Error(String(err));
            setError(connectError);
        } finally {
            setIsConnecting(false);
        }
    }, [walletConnect]);

    /**
     * Disconnect the current wallet.
     */
    const disconnect = useCallback(async () => {
        setError(null);
        try {
            await walletConnect.disconnect();
        } catch (err) {
            const disconnectError = err instanceof Error ? err : new Error(String(err));
            setError(disconnectError);
        }
    }, [walletConnect]);

    /**
     * Sign a message with the connected wallet.
     *
     * @param message - The message to sign
     * @returns The signature or null if signing failed
     */
    const signMessage = useCallback(
        async (message: string): Promise<string | null> => {
            setError(null);
            try {
                const signature = await walletConnect.signMessage(message);
                return signature;
            } catch (err) {
                const signError = err instanceof Error ? err : new Error(String(err));
                setError(signError);
                return null;
            }
        },
        [walletConnect]
    );

    /**
     * Sign a PSBT with the connected wallet.
     *
     * @param psbt - The PSBT to sign (base64 or hex)
     * @returns The signed PSBT or null if signing failed
     */
    const signPsbt = useCallback(
        async (psbt: string): Promise<string | null> => {
            setError(null);
            try {
                const signedPsbt = await walletConnect.signPsbt(psbt);
                return signedPsbt;
            } catch (err) {
                const signError = err instanceof Error ? err : new Error(String(err));
                setError(signError);
                return null;
            }
        },
        [walletConnect]
    );

    /**
     * Get the wallet address as an Address object for contract interactions.
     *
     * @returns Address object or null if not connected
     */
    const getAddress = useCallback((): Address | null => {
        const addr = walletConnect.address;
        if (!addr) return null;
        try {
            return Address.fromString(addr.toString());
        } catch {
            return null;
        }
    }, [walletConnect.address]);

    return {
        address: walletConnect.address,
        publicKey: walletConnect.publicKey,
        isConnected: walletConnect.connected,
        isConnecting,
        error,
        walletName: walletConnect.walletName,
        connect,
        disconnect,
        signMessage,
        signPsbt,
        getAddress,
    };
}
