/**
 * Event data models for Task 2 - Real-time Event Streaming
 */

export interface BlockEvent {
  block_hash: string;
  block_height?: number;
  timestamp: string;
  received_at: number;
}

export interface TransactionEvent {
  txid: string;
  timestamp: string;
  received_at: number;
  size_vbytes?: number;
  fee_rate_sat_vb?: number;
}

export interface BlockState {
  hash: string;
  height?: number;
  received_at?: number;
  timestamp?: string;
}

export interface StateComparison {
  status: 'synced' | 'divergence';
  divergence_detected: boolean;
  buffer_latest_block?: BlockState;
  rpc_latest_block?: BlockState;
  reorg_depth: number;
  warning?: string;
  comparison_timestamp: string;
}

export interface EventStats {
  zmq_listener_status: 'connected' | 'disconnected';
  buffer_blocks_count: number;
  buffer_blocks_capacity: number;
  buffer_transactions_count: number;
  buffer_transactions_capacity: number;
  last_block_received?: string;
  last_transaction_received?: string;
  uptime_seconds?: number;
  events_received: {
    blocks: number;
    transactions: number;
  };
}

export interface EventSummary {
  blocks_observed: number;
  tx_observed: number;
  last_event_time?: number;
  tx_per_second: number;
}

export interface LatestEvents {
  blocks: Array<{ hash: string; ts: number }>;
  txs: Array<{ txid: string; ts: number }>;
}
