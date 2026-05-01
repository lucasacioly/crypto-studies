export interface FeeDistribution {
  low: number;
  medium: number;
  high: number;
}

export interface MempoolSummary {
  tx_count: number;
  total_vsize: number;
  avg_fee_rate: number;
  min_fee_rate: number;
  max_fee_rate: number;
  fee_distribution: FeeDistribution;
  timestamp: string;
}
