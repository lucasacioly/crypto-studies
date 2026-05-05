"""
Transaction management endpoints for Tarefa 3 (Task 3).
Provides transaction details with interpretation and wallet context.
"""

from fastapi import APIRouter, HTTPException, Depends
import logging
import time
from typing import List, Optional
from models.transactions import TransactionDetail
from models.errors import RPCConnectionError, RPCMethodError
from layers.rpc_client import RPCClient
from layers.transaction_interpreter import TransactionInterpreter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tx", tags=["transactions"])


def get_rpc_client() -> RPCClient:
    """Get the RPC client instance."""
    from dependencies import rpc_client
    return rpc_client


@router.get("/{txid}", response_model=TransactionDetail)
async def get_transaction_detail(
    txid: str,
    rpc_client: RPCClient = Depends(get_rpc_client)
):
    """
    Get detailed transaction information with interpretation.
    
    Args:
        txid: Transaction ID
        
    Returns:
        TransactionDetail with status, confirmations, and interpretation
        
    Raises:
        400: No wallet selected
        404: Transaction not found
        503: RPC connection failed
    """
    try:
        logger.info(f"GET /tx/{txid}")
        
        selected_wallet = rpc_client.get_selected_wallet()
        if not selected_wallet:
            raise HTTPException(
                status_code=400,
                detail="No wallet selected. Use POST /wallet/select first."
            )
        
        # Get transaction from wallet
        try:
            tx_data = rpc_client.call("gettransaction", [txid])
        except RPCMethodError as e:
            if "not found" in str(e).lower():
                raise HTTPException(
                    status_code=404,
                    detail=f"Transaction {txid} not found in wallet {selected_wallet}"
                )
            raise
        
        # Get current time
        current_time = time.time()
        
        # Get interpretation
        interpretation = TransactionInterpreter.get_interpretation(tx_data, current_time)
        
        # Extract relevant data
        confirmations = tx_data.get("confirmations", 0)
        confirmed = confirmations > 0
        block_hash = tx_data.get("blockhash")
        age_seconds = TransactionInterpreter.get_transaction_age(tx_data, current_time)
        
        logger.info(f"Transaction {txid}: {interpretation.status}, confirmations={confirmations}")
        
        return TransactionDetail(
            txid=txid,
            wallet=selected_wallet,
            status=interpretation.status,
            confirmed=confirmed,
            confirmations=confirmations,
            block_hash=block_hash,
            age_seconds=age_seconds,
            message=interpretation.message,
            warning=interpretation.warning
        )
    except HTTPException:
        raise
    except (RPCConnectionError, RPCMethodError) as e:
        logger.error(f"Error getting transaction: {e}")
        raise HTTPException(
            status_code=503,
            detail="Cannot connect to Bitcoin RPC"
        )
    except Exception as e:
        logger.error(f"Unexpected error getting transaction: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
