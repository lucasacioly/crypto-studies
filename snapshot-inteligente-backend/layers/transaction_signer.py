"""
Transaction signer for signing and broadcasting transactions.
"""

import logging
from layers.rpc_client import RPCClient
from models.errors import RPCMethodError

logger = logging.getLogger(__name__)


class TransactionSigner:
    """Signs and broadcasts transactions."""
    
    @staticmethod
    def sign_transaction(
        rpc_client: RPCClient,
        unsigned_tx_hex: str,
        wallet: str
    ) -> dict:
        """
        Sign a transaction with the selected wallet.
        
        Args:
            rpc_client: RPC client instance
            unsigned_tx_hex: Unsigned transaction hex
            wallet: Wallet name to sign with
            
        Returns:
            Dict with signed transaction hex and completeness
            
        Raises:
            RPCMethodError: Signing failed
        """
        logger.info(f"Signing transaction with wallet: {wallet}")
        
        try:
            result = rpc_client.call('signrawtransactionwithwallet', [unsigned_tx_hex], wallet=wallet)
            return {
                "tx_hex": result.get('hex'),
                "complete": result.get('complete', False),
                "errors": result.get('errors', [])
            }
        except RPCMethodError as e:
            logger.error(f"Signing failed: {e}")
            raise ValueError(f"Transaction signing failed: {str(e)}")
    
    @staticmethod
    def broadcast_transaction(rpc_client: RPCClient, signed_tx_hex: str) -> str:
        """
        Broadcast a signed transaction to the network.
        
        Args:
            rpc_client: RPC client instance
            signed_tx_hex: Signed transaction hex
            
        Returns:
            Transaction ID (txid)
            
        Raises:
            RPCMethodError: Broadcasting failed
        """
        logger.info("Broadcasting transaction")
        
        try:
            txid = rpc_client.call('sendrawtransaction', [signed_tx_hex])
            logger.info(f"Transaction broadcast successfully: {txid}")
            return txid
        except RPCMethodError as e:
            logger.error(f"Broadcasting failed: {e}")
            raise ValueError(f"Transaction broadcast failed: {str(e)}")
