import { Blockchain } from '@btc-vision/btc-runtime/runtime';
import { revertOnError } from '@btc-vision/btc-runtime/runtime/abort/abort';
import { OP20Token } from './OP20Token';

// Contract factory - DO NOT MODIFY
Blockchain.contract = (): OP20Token => {
    return new OP20Token();
};

// Required runtime exports - DO NOT MODIFY
export * from '@btc-vision/btc-runtime/runtime/exports';

// Required abort handler - DO NOT MODIFY
export function abort(message: string, fileName: string, line: u32, column: u32): void {
    revertOnError(message, fileName, line, column);
}
