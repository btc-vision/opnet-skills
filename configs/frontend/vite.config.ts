import { resolve } from 'path';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { nodePolyfills } from 'vite-plugin-node-polyfills';
import eslint from 'vite-plugin-eslint2';

export default defineConfig({
    base: '/',
    plugins: [
        nodePolyfills({
            globals: {
                Buffer: true,
                global: true,
                process: true
            },
            overrides: {
                crypto: 'crypto-browserify'
            }
        }),
        react(),
        eslint({
            cache: false
        })
    ],
    resolve: {
        alias: {
            global: 'global',
            // Browser shims for Node.js-specific modules
            undici: resolve(__dirname, 'node_modules/opnet/src/fetch/fetch-browser.js')
        },
        mainFields: ['module', 'main', 'browser'],
        dedupe: ['@noble/curves', '@noble/hashes', '@scure/base', 'buffer', 'react', 'react-dom']
    },
    build: {
        commonjsOptions: {
            strictRequires: true,
            transformMixedEsModules: true
        },
        rollupOptions: {
            output: {
                entryFileNames: '[name].js',
                chunkFileNames: 'js/[name]-[hash].js',
                assetFileNames: (assetInfo) => {
                    const name = assetInfo.names?.[0] ?? '';
                    const info = name.split('.');
                    const ext = info[info.length - 1];
                    if (/png|jpe?g|svg|gif|tiff|bmp|ico/i.test(ext || '')) {
                        return `images/[name][extname]`;
                    }
                    if (/woff|woff2|eot|ttf|otf/i.test(ext || '')) {
                        return `fonts/[name][extname]`;
                    }
                    if (/css/i.test(ext || '')) {
                        return `css/[name][extname]`;
                    }
                    return `assets/[name][extname]`;
                },
                manualChunks(id) {
                    // crypto-browserify has internal circular deps - don't split it
                    // Let it bundle with the main code
                    if (id.includes('crypto-browserify') || id.includes('randombytes')) {
                        return undefined; // Don't put in separate chunk
                    }
                    if (id.includes('node_modules')) {
                        // Noble crypto libraries - shared across packages
                        if (id.includes('@noble/curves')) return 'noble-curves';
                        if (id.includes('@noble/hashes')) return 'noble-hashes';
                        if (id.includes('@scure/')) return 'scure';

                        // @btc-vision packages - split individually
                        if (id.includes('@btc-vision/transaction')) return 'btc-transaction';
                        if (id.includes('@btc-vision/bitcoin')) return 'btc-bitcoin';
                        if (id.includes('@btc-vision/bip32')) return 'btc-bip32';
                        if (id.includes('@btc-vision/post-quantum')) return 'btc-post-quantum';
                        if (id.includes('@btc-vision/wallet-sdk')) return 'btc-wallet-sdk';
                        if (id.includes('@btc-vision/logger')) return 'btc-logger';
                        if (id.includes('@btc-vision/passworder')) return 'btc-passworder';

                        // opnet library
                        if (id.includes('node_modules/opnet')) return 'opnet';

                        // Bitcoin utilities
                        if (id.includes('bip39')) return 'bip39';
                        if (id.includes('ecpair') || id.includes('tiny-secp256k1')) return 'bitcoin-utils';
                        if (id.includes('bitcore-lib')) return 'bitcore';

                        // UI libraries - react, react-dom, scheduler, and antd MUST be in same chunk
                        // to ensure proper initialization order
                        if (
                            id.includes('node_modules/react-dom') ||
                            id.includes('node_modules/react/') ||
                            id.includes('node_modules/scheduler') ||
                            id.includes('antd') ||
                            id.includes('@ant-design') ||
                            id.includes('rc-') ||
                            id.includes('@rc-component')
                        )
                            return 'react-ui';

                        // Other large deps
                        if (id.includes('ethers')) return 'ethers';
                        if (id.includes('protobufjs') || id.includes('@protobufjs')) return 'protobuf';
                        if (id.includes('lodash')) return 'lodash';
                    }
                }
            },
            external: [
                'worker_threads',
                'node:sqlite',
                'node:diagnostics_channel',
                'node:async_hooks',
                'node:perf_hooks',
                'node:worker_threads'
            ]
        },
        target: 'esnext',
        modulePreload: false,
        cssCodeSplit: false,
        assetsInlineLimit: 10000,
        chunkSizeWarningLimit: 3000
    },
    optimizeDeps: {
        include: ['react', 'react-dom', 'buffer', 'process', 'stream-browserify'],
        exclude: ['@btc-vision/transaction', 'crypto-browserify']
    }
});
