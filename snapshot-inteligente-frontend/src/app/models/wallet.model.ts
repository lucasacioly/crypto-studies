/**
 * Wallet data models for Task 3 - Multiple Wallets Support
 */

export interface WalletInfo {
  walletname: string;
  balance: number;
  txcount: number;
}

export interface WalletStatus {
  wallet: string;
  balance: number;
  utxos: number;
}

export interface WalletListResponse {
  available_wallets: string[];
  loaded_wallets: string[];
  selected_wallet?: string;
}

export interface WalletSelectResponse {
  selected_wallet: string;
  wallet_info: WalletInfo;
}

export enum TransactionStatusEnum {
  BROADCAST = 'broadcast',
  MEMPOOL = 'mempool',
  CONFIRMED = 'confirmed',
  UNKNOWN = 'unknown'
}

export interface TransactionInterpretation {
  status: TransactionStatusEnum;
  message: string;
  warning?: string;
}

export interface TransactionDetail {
  txid: string;
  wallet: string;
  status: TransactionStatusEnum;
  confirmed: boolean;
  confirmations: number;
  block_hash?: string;
  age_seconds: number;
  message: string;
  warning?: string;
}
