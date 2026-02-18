import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { nodePolyfills } from 'vite-plugin-node-polyfills';
import { resolve } from 'path';

export default defineConfig({
    plugins: [
        // nodePolyfills MUST come before react()
        nodePolyfills({
            globals: {
                // Buffer polyfill is needed for third-party dependencies that still use it.
                // OPNet's own code uses Uint8Array, but transitive deps may require Buffer.
                Buffer: true,
                global: true,
                process: true,
            },
            overrides: {
                crypto: 'crypto-browserify', // REQUIRED for signing operations
            },
        }),
        react(),
    ],
    resolve: {
        alias: {
            global: 'global',
            // opnet uses undici for fetch - needs browser shim
            undici: resolve(__dirname, 'node_modules/opnet/src/fetch/fetch-browser.js'),
            '@noble/hashes/sha256': '@noble/hashes/sha2.js',
            '@noble/hashes/sha512': '@noble/hashes/sha2.js',
            '@noble/hashes/ripemd160': '@noble/hashes/legacy.js',
        },
        dedupe: [
            '@noble/curves',
            '@noble/hashes',
            '@scure/base',
            'buffer',
            'react',
            'react-dom',
        ],
    },
    build: {
        target: 'esnext',
        rollupOptions: {
            output: {
                manualChunks: {
                    crypto: ['@noble/curves', '@noble/hashes'],
                    btcvision: [
                        '@btc-vision/transaction',
                        '@btc-vision/bitcoin',
                        '@btc-vision/bip32',
                        '@btc-vision/ecpair',
                    ],
                    opnet: ['opnet'],
                    react: ['react', 'react-dom', 'react-router-dom'],
                },
            },
        },
    },
    optimizeDeps: {
        include: ['react', 'react-dom', 'buffer', 'process'],
        exclude: ['crypto-browserify'],
    },
});
