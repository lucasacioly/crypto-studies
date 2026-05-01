from datetime import datetime
from typing import List, Dict
from layers.rpc_client import RPCClient
from layers.cache_layer import CacheLayer
from models.responses import MempoolSummary, BlockchainLag
from models.errors import RPCConnectionError, RPCMethodError
from config import config
import logging

logger = logging.getLogger(__name__)

class BitcoinService:
    """
    Bitcoin data interpretation service.
    Analyzes raw RPC data and provides high-level metrics.
    """
    
    def __init__(self, rpc_client: RPCClient, cache_layer: CacheLayer):
        self.rpc = rpc_client
        self.cache = cache_layer
    
    @property
    def fee_low_threshold(self) -> float:
        """Low fee threshold in sat/vB."""
        return config.FEE_LOW_THRESHOLD
    
    @property
    def fee_high_threshold(self) -> float:
        """High fee threshold in sat/vB."""
        return config.FEE_HIGH_THRESHOLD
    
    def _classify_fee(self, fee_rate: float) -> str:
        """
        Classify transaction fee into low/medium/high category.
        
        Args:
            fee_rate: Fee rate in sat/vB
            
        Returns:
            Category: 'low', 'medium', or 'high'
        """
        if fee_rate < self.fee_low_threshold:
            return 'low'
        elif fee_rate <= self.fee_high_threshold:
            return 'medium'
        else:
            return 'high'
    
    def get_mempool_summary(self) -> MempoolSummary:
        """
        Analyze mempool and return fee distribution summary.
        
        Flow:
        1. Fetch getmempoolinfo → basic stats
        2. Fetch getrawmempool(true) → detailed TX info with fees
        3. Extract fee rates from each transaction
        4. Calculate statistics (avg, min, max)
        5. Classify transactions into buckets
        
        Returns:
            MempoolSummary with tx counts, fee stats, and distribution
            
        Raises:
            RPCConnectionError: RPC connection failed
            RPCMethodError: RPC call returned error
        """
        try:
            logger.info("Fetching mempool summary")
            
            # Fetch basic mempool info
            mempool_info = self.rpc.call('getmempoolinfo')
            
            # Fetch detailed mempool with verbose=true
            raw_mempool = self.rpc.call('getrawmempool', [True])
            
            # Extract fee rates from all transactions
            fee_rates: List[float] = []
            for txid, tx_data in raw_mempool.items():
                # Fee is in BTC, vsize is in vB
                # Convert fee rate to sat/vB: (fee_btc * 100_000_000 sat/BTC) / vsize
                if 'fees' in tx_data and 'vsize' in tx_data:
                    fee_btc = tx_data['fees'].get('base', 0)
                    vsize = tx_data.get('vsize', 1)
                    if vsize > 0:
                        fee_rate = (fee_btc * 100_000_000) / vsize
                        fee_rates.append(fee_rate)
            
            # Calculate statistics
            if fee_rates:
                avg_fee = sum(fee_rates) / len(fee_rates)
                min_fee = min(fee_rates)
                max_fee = max(fee_rates)
            else:
                avg_fee = min_fee = max_fee = 0.0
            
            # Classify transactions into buckets
            distribution: Dict[str, int] = {'low': 0, 'medium': 0, 'high': 0}
            for fee_rate in fee_rates:
                category = self._classify_fee(fee_rate)
                distribution[category] += 1
            
            # Get total vsize from mempool info
            total_vsize = mempool_info.get('total_vsize', 0)
            
            result = MempoolSummary(
                tx_count=len(raw_mempool),
                total_vsize=total_vsize,
                avg_fee_rate=round(avg_fee, 2),
                min_fee_rate=round(min_fee, 2),
                max_fee_rate=round(max_fee, 2),
                fee_distribution=distribution,
                timestamp=datetime.utcnow().isoformat()
            )
            
            logger.info(f"Mempool summary: {result.tx_count} txs, avg fee {result.avg_fee_rate} sat/vB")
            return result
            
        except (RPCConnectionError, RPCMethodError) as e:
            logger.error(f"Error fetching mempool summary: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in mempool summary: {e}")
            raise
    
    def get_blockchain_lag(self) -> BlockchainLag:
        """
        Compare blockchain synchronization status.
        
        Flow:
        1. Fetch getblockchaininfo
        2. Extract blocks and headers counts
        3. Calculate lag (headers - blocks)
        
        Returns:
            BlockchainLag with block counts and lag
            
        Raises:
            RPCConnectionError: RPC connection failed
            RPCMethodError: RPC call returned error
        """
        try:
            logger.info("Fetching blockchain lag")
            
            blockchain_info = self.rpc.call('getblockchaininfo')
            
            blocks = blockchain_info.get('blocks', 0)
            headers = blockchain_info.get('headers', 0)
            lag = headers - blocks
            
            result = BlockchainLag(
                blocks=blocks,
                headers=headers,
                lag=lag,
                timestamp=datetime.utcnow().isoformat()
            )
            
            logger.info(f"Blockchain lag: {lag} blocks behind headers")
            return result
            
        except (RPCConnectionError, RPCMethodError) as e:
            logger.error(f"Error fetching blockchain lag: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in blockchain lag: {e}")
            raise
