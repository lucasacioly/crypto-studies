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

// Transaction Creation Models
export interface TransactionCreateRequest {
  recipient: string;
  amount_btc: number;
  fee_rate_sat_vB: number;
  utxo_selection_mode: 'automatic' | 'manual';
  selected_utxo_indices?: number[];
}

export interface TransactionCreateResponse {
  tx_hex: string;
  inputs: Array<{ txid: string; vout: number }>;
  outputs: { [address: string]: number };
  selected_utxos: number;
  change_amount_sat: number;
  estimated_fee_sat: number;
  recipient: string;
  amount_sat: number;
}

export interface TransactionSignRequest {
  tx_hex: string;
}

export interface TransactionSignResponse {
  tx_hex: string;
  complete: boolean;
  errors: string[];
}

export interface TransactionBroadcastRequest {
  tx_hex: string;
}

export interface TransactionBroadcastResponse {
  txid: string;
  wallet: string;
  status: string;
  broadcast_time: string;
}

export interface UTXO {
  index: number;
  txid: string;
  vout: number;
  amount_btc: number;
  amount_sat: number;
  confirmations: number;
}

export interface UTXOListResponse {
  wallet: string;
  utxos: UTXO[];
  total_amount_sat: number;
}

export interface FeeEstimateResponse {
  fee_rate_sat_vB: number;
  source: 'bitcoin_core' | 'manual';
  target_blocks: number;
}

export interface SentTransaction {
  txid: string;
  wallet: string;
  recipient: string;
  amount_btc: number;
  fee_sat: number;
  status: string;
  created_at: string;
  broadcast_at: string;
  confirmations: number;
}
