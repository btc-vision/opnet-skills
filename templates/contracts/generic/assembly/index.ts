import { Blockchain } from '@btc-vision/btc-runtime/runtime';
import { revertOnError } from '@btc-vision/btc-runtime/runtime/abort/abort';
import { MyContract } from './MyContract';

// Contract factory - DO NOT MODIFY
Blockchain.contract = (): MyContract => {
    return new MyContract();
};

// Required runtime exports - DO NOT MODIFY
export * from '@btc-vision/btc-runtime/runtime/exports';

// Required abort handler - DO NOT MODIFY
export function abort(message: string, fileName: string, line: u32, column: u32): void {
    revertOnError(message, fileName, line, column);
}
