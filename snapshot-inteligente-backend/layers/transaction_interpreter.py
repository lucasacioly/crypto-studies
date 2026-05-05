"""
Transaction state interpreter for Tarefa 3 (Task 3).
Interprets raw transaction data and provides human-readable context.
"""

from datetime import datetime
import time
import logging
from typing import Optional, Tuple
from models.transactions import TransactionStatus, TransactionInterpretation

logger = logging.getLogger(__name__)


class TransactionInterpreter:
    """Interprets transaction states and provides context."""
    
    # Threshold for "delayed" transactions in mempool (seconds)
    MEMPOOL_DELAY_THRESHOLD = 120  # 2 minutes
    
    @staticmethod
    def interpret_status(tx_data: dict, current_time: float) -> Tuple[TransactionStatus, str, Optional[str]]:
        """
        Interpret transaction status from raw data.
        
        Args:
            tx_data: Raw transaction data from RPC
            current_time: Current time in unix timestamp
            
        Returns:
            Tuple of (status, message, warning)
        """
        confirmations = tx_data.get("confirmations", 0)
        
        # Confirmed transaction
        if confirmations > 0:
            return TransactionStatus.CONFIRMED, f"Transação confirmada em {confirmations} bloco(s).", None
        
        # Transaction in mempool (0 confirmations but exists in wallet)
        if confirmations == 0 and "blockhash" not in tx_data:
            # Check if transaction is delayed in mempool
            tx_time = tx_data.get("time", current_time)
            age_seconds = int(current_time - tx_time)
            
            message = "Transação aceita na mempool, aguardando inclusão em bloco."
            warning = None
            
            if age_seconds > self.MEMPOOL_DELAY_THRESHOLD:
                warning = f"Transação está na mempool há mais de 2 minutos ({age_seconds}s)."
            
            return TransactionStatus.MEMPOOL, message, warning
        
        # Broadcast but not yet in mempool
        if confirmations == -1 or (confirmations == 0 and "blockhash" in tx_data):
            return TransactionStatus.BROADCAST, "Transação enviada ao node, aguardando aceitação na mempool.", None
        
        # Unknown state
        return TransactionStatus.UNKNOWN, "Transação não localizada.", None
    
    @staticmethod
    def get_transaction_age(tx_data: dict, current_time: Optional[float] = None) -> int:
        """
        Calculate transaction age in seconds.
        
        Args:
            tx_data: Raw transaction data
            current_time: Current time (defaults to now)
            
        Returns:
            Age in seconds
        """
        if current_time is None:
            current_time = time.time()
        
        tx_time = tx_data.get("time", current_time)
        return max(0, int(current_time - tx_time))
    
    @staticmethod
    def get_interpretation(tx_data: dict, current_time: Optional[float] = None) -> TransactionInterpretation:
        """
        Get full interpretation of a transaction.
        
        Args:
            tx_data: Raw transaction data from RPC
            current_time: Current time (defaults to now)
            
        Returns:
            TransactionInterpretation with status, message, and warning
        """
        if current_time is None:
            current_time = time.time()
        
        status, message, warning = TransactionInterpreter.interpret_status(tx_data, current_time)
        
        return TransactionInterpretation(
            status=status,
            message=message,
            warning=warning
        )
    
    @staticmethod
    def is_delayed(tx_data: dict, current_time: Optional[float] = None) -> bool:
        """
        Check if transaction is delayed in mempool.
        
        Args:
            tx_data: Raw transaction data
            current_time: Current time (defaults to now)
            
        Returns:
            True if transaction is delayed
        """
        if current_time is None:
            current_time = time.time()
        
        confirmations = tx_data.get("confirmations", 0)
        
        # Only check delay for unconfirmed transactions
        if confirmations != 0:
            return False
        
        tx_time = tx_data.get("time", current_time)
        age_seconds = int(current_time - tx_time)
        
        return age_seconds > TransactionInterpreter.MEMPOOL_DELAY_THRESHOLD
