import { Blockchain } from '@btc-vision/btc-runtime/runtime';
import { revertOnError } from '@btc-vision/btc-runtime/runtime/abort/abort';

// Change the import below to match your contract:
// import { OP20Token } from './OP20Token';
// import { MyContract } from './MyContract';
import { OP721NFT } from './OP721NFT';

// Contract factory - change the type and class to match your import above
Blockchain.contract = (): OP721NFT => {
    return new OP721NFT();
};

// Required runtime exports - DO NOT MODIFY
export * from '@btc-vision/btc-runtime/runtime/exports';

// Required abort handler - DO NOT MODIFY
export function abort(message: string, fileName: string, line: u32, column: u32): void {
    revertOnError(message, fileName, line, column);
}
