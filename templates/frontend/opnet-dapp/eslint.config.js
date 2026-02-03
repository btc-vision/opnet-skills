import eslint from '@eslint/js';
import tseslint from 'typescript-eslint';
import reactHooks from 'eslint-plugin-react-hooks';
import reactRefresh from 'eslint-plugin-react-refresh';

export default tseslint.config(
    eslint.configs.recommended,
    ...tseslint.configs.strictTypeChecked,
    {
        languageOptions: {
            parserOptions: {
                projectService: true,
                tsconfigRootDir: import.meta.dirname,
            },
        },
        plugins: {
            'react-hooks': reactHooks,
            'react-refresh': reactRefresh,
        },
        rules: {
            // React hooks rules
            'react-hooks/rules-of-hooks': 'error',
            'react-hooks/exhaustive-deps': 'warn',
            'react-refresh/only-export-components': ['warn', { allowConstantExport: true }],

            // TypeScript strict rules
            '@typescript-eslint/no-explicit-any': 'error',
            '@typescript-eslint/explicit-function-return-type': 'warn',
            '@typescript-eslint/strict-boolean-expressions': 'warn',
            '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
        },
    },
    {
        files: ['**/*.js'],
        ...tseslint.configs.disableTypeChecked,
    }
);
