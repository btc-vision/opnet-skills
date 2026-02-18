// @ts-check
// ESLint flat config for OPNet TypeScript projects (backends, libraries, plugins)
// Matches the conventions used by @btc-vision/transaction, opnet, @btc-vision/bitcoin
//
// Required devDependencies:
//   eslint @eslint/js typescript-eslint

import eslint from '@eslint/js';
import tseslint from 'typescript-eslint';

export default tseslint.config(
    eslint.configs.recommended,
    ...tseslint.configs.strictTypeChecked,
    {
        languageOptions: {
            parserOptions: {
                projectService: true,
                tsconfigDirName: import.meta.dirname,
            },
        },
        rules: {
            // --- Core TypeScript rules (matching OPNet repos) ---
            'no-undef': 'off',
            '@typescript-eslint/no-unused-vars': 'off',
            'no-empty': 'off',
            '@typescript-eslint/restrict-template-expressions': 'off',
            '@typescript-eslint/only-throw-error': 'off',
            '@typescript-eslint/no-unnecessary-condition': 'off',
            '@typescript-eslint/unbound-method': 'warn',
            '@typescript-eslint/no-confusing-void-expression': 'off',
            '@typescript-eslint/no-extraneous-class': 'off',
            'no-async-promise-executor': 'off',
            '@typescript-eslint/no-misused-promises': 'off',
            '@typescript-eslint/no-unnecessary-type-parameters': 'off',
            '@typescript-eslint/no-duplicate-enum-values': 'off',
            'prefer-spread': 'off',
            '@typescript-eslint/no-empty-object-type': 'off',
            '@typescript-eslint/no-base-to-string': 'off',
            '@typescript-eslint/no-dynamic-delete': 'off',
            '@typescript-eslint/no-redundant-type-constituents': 'off',
            'no-useless-assignment': 'off',

            // --- OPNet-specific safety rules ---
            'no-restricted-globals': [
                'error',
                { name: 'Buffer', message: 'Buffer is REMOVED from OPNet. Use Uint8Array with toHex/fromHex/fromBase64/toBase64 from @btc-vision/bitcoin.' },
            ],
            'no-restricted-properties': [
                'error',
                { object: 'Buffer', property: 'from', message: 'Buffer is REMOVED. Use fromHex()/fromBase64() from @btc-vision/bitcoin or new TextEncoder().encode().' },
                { object: 'Buffer', property: 'alloc', message: 'Buffer is REMOVED. Use new Uint8Array(size).' },
                { object: 'Buffer', property: 'concat', message: 'Buffer is REMOVED. Use Uint8Array concatenation.' },
            ],
        },
    },
    {
        files: ['**/*.js'],
        ...tseslint.configs.disableTypeChecked,
    },
);
