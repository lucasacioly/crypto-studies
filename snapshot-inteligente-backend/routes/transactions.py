"""
Transaction management endpoints for Tarefa 3 (Task 3).
Provides transaction details with interpretation and wallet context.
Includes transaction creation, signing, broadcasting.
"""

from fastapi import APIRouter, HTTPException, Depends
import logging
import time
import json
from typing import List, Optional
from datetime import datetime
from pathlib import Path
from models.transactions import (
    TransactionDetail,
    TransactionCreateRequest,
    TransactionCreateResponse,
    TransactionSignRequest,
    TransactionSignResponse,
    TransactionBroadcastRequest,
    TransactionBroadcastResponse,
    UTXOListResponse,
    UTXOInfo,
    FeeEstimateResponse,
    SentTransaction
)
from models.errors import RPCConnectionError, RPCMethodError
from layers.rpc_client import RPCClient
from layers.transaction_interpreter import TransactionInterpreter
from layers.transaction_builder import TransactionBuilder, UTXO
from layers.transaction_signer import TransactionSigner

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tx", tags=["transactions"])

# Path to persistent sent transactions storage
SENT_TX_FILE = Path("sent_transactions.json")


def get_rpc_client() -> RPCClient:
    """Get the RPC client instance."""
    from dependencies import rpc_client
    return rpc_client


def load_sent_transactions() -> dict:
    """Load sent transactions from file."""
    if SENT_TX_FILE.exists():
        with open(SENT_TX_FILE, 'r') as f:
            return json.load(f)
    return {"transactions": []}


def save_sent_transactions(data: dict):
    """Save sent transactions to file."""
    with open(SENT_TX_FILE, 'w') as f:
        json.dump(data, f, indent=2)



@router.get("/estimate-fee", response_model=FeeEstimateResponse)
async def estimate_fee(
    target_blocks: int = 2,
    rpc_client: RPCClient = Depends(get_rpc_client)
):
    """
    Estimate transaction fee rate.
    
    Args:
        target_blocks: Target number of blocks (1-1008, default 2)
        
    Returns:
        FeeEstimateResponse with fee rate in sat/vB
        
    Raises:
        503: RPC connection failed
    """
    try:
        logger.info(f"GET /tx/estimate-fee - target_blocks={target_blocks}")
        
        # Clamp target_blocks to valid range
        target_blocks = max(1, min(target_blocks, 1008))
        
        try:
            fee_rate = rpc_client.estimate_fee_sat_vB(target_blocks)
            return FeeEstimateResponse(
                fee_rate_sat_vB=fee_rate,
                source="bitcoin_core",
                target_blocks=target_blocks
            )
        except Exception as e:
            logger.warning(f"Fee estimation failed, returning default: {e}")
            # Return default fee if estimation fails
            return FeeEstimateResponse(
                fee_rate_sat_vB=5.0,
                source="bitcoin_core",
                target_blocks=target_blocks
            )
    except Exception as e:
        logger.error(f"Error estimating fee: {e}")
        raise HTTPException(
            status_code=503,
            detail="Cannot estimate fee"
        )


@router.get("/utxos", response_model=UTXOListResponse)
async def get_utxos(
    rpc_client: RPCClient = Depends(get_rpc_client)
):
    """
    Get available UTXOs for the selected wallet.
    
    Returns:
        UTXOListResponse with list of available UTXOs
        
    Raises:
        400: No wallet selected
        503: RPC connection failed
    """
    try:
        logger.info("GET /tx/utxos")
        
        selected_wallet = rpc_client.get_selected_wallet()
        if not selected_wallet:
            raise HTTPException(
                status_code=400,
                detail="No wallet selected. Use POST /wallet/select first."
            )
        
        utxos = TransactionBuilder.get_utxos(rpc_client)
        
        utxo_list = [
            UTXOInfo(
                index=i,
                txid=u.txid,
                vout=u.vout,
                amount_btc=u.amount,
                amount_sat=u.amount_sat,
                confirmations=u.confirmations
            )
            for i, u in enumerate(utxos)
        ]
        
        total_sat = sum(u.amount_sat for u in utxos)
        
        logger.info(f"Returning {len(utxo_list)} UTXOs for wallet {selected_wallet}")
        
        return UTXOListResponse(
            wallet=selected_wallet,
            utxos=utxo_list,
            total_amount_sat=total_sat
        )
    except HTTPException:
        raise
    except (RPCConnectionError, RPCMethodError) as e:
        logger.error(f"Error getting UTXOs: {e}")
        raise HTTPException(
            status_code=503,
            detail="Cannot connect to Bitcoin RPC"
        )
    except Exception as e:
        logger.error(f"Unexpected error getting UTXOs: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/create", response_model=TransactionCreateResponse)
async def create_transaction(
    request: TransactionCreateRequest,
    rpc_client: RPCClient = Depends(get_rpc_client)
):
    """
    Create an unsigned transaction.
    
    Args:
        request: Transaction creation parameters
        
    Returns:
        TransactionCreateResponse with unsigned TX hex
        
    Raises:
        400: Invalid parameters or insufficient funds
        503: RPC connection failed
    """
    try:
        logger.info(f"POST /tx/create - {request.amount_btc} BTC to {request.recipient[:20]}...")
        
        selected_wallet = rpc_client.get_selected_wallet()
        if not selected_wallet:
            raise HTTPException(
                status_code=400,
                detail="No wallet selected. Use POST /wallet/select first."
            )
        
        # Create unsigned transaction
        result = TransactionBuilder.create_unsigned_transaction(
            rpc_client,
            recipient=request.recipient,
            amount_btc=request.amount_btc,
            fee_rate_sat_vB=request.fee_rate_sat_vB,
            utxo_selection_mode=request.utxo_selection_mode,
            selected_utxo_indices=request.selected_utxo_indices
        )
        
        return TransactionCreateResponse(**result)
    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except (RPCConnectionError, RPCMethodError) as e:
        logger.error(f"RPC error during creation: {e}")
        raise HTTPException(
            status_code=503,
            detail="Cannot connect to Bitcoin RPC"
        )
    except Exception as e:
        logger.error(f"Unexpected error creating transaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sign", response_model=TransactionSignResponse)
async def sign_transaction(
    request: TransactionSignRequest,
    rpc_client: RPCClient = Depends(get_rpc_client)
):
    """
    Sign an unsigned transaction with the selected wallet.
    
    Args:
        request: Unsigned transaction hex
        
    Returns:
        TransactionSignResponse with signed TX hex
        
    Raises:
        400: No wallet selected or signing failed
        503: RPC connection failed
    """
    try:
        logger.info("POST /tx/sign")
        
        selected_wallet = rpc_client.get_selected_wallet()
        if not selected_wallet:
            raise HTTPException(
                status_code=400,
                detail="No wallet selected. Use POST /wallet/select first."
            )
        
        result = TransactionSigner.sign_transaction(
            rpc_client,
            unsigned_tx_hex=request.tx_hex,
            wallet=selected_wallet
        )
        
        return TransactionSignResponse(**result)
    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"Signing error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except (RPCConnectionError, RPCMethodError) as e:
        logger.error(f"RPC error during signing: {e}")
        raise HTTPException(
            status_code=503,
            detail="Cannot connect to Bitcoin RPC"
        )
    except Exception as e:
        logger.error(f"Unexpected error signing transaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/broadcast", response_model=TransactionBroadcastResponse)
async def broadcast_transaction(
    request: TransactionBroadcastRequest,
    rpc_client: RPCClient = Depends(get_rpc_client)
):
    """
    Broadcast a signed transaction and record it.
    
    Args:
        request: Signed transaction hex
        
    Returns:
        TransactionBroadcastResponse with txid and status
        
    Raises:
        400: No wallet selected or broadcast failed
        503: RPC connection failed
    """
    try:
        logger.info("POST /tx/broadcast")
        
        selected_wallet = rpc_client.get_selected_wallet()
        if not selected_wallet:
            raise HTTPException(
                status_code=400,
                detail="No wallet selected. Use POST /wallet/select first."
            )
        
        # Broadcast transaction
        txid = TransactionSigner.broadcast_transaction(rpc_client, request.tx_hex)
        
        # Record sent transaction with metadata
        sent_data = load_sent_transactions()
        broadcast_time = datetime.utcnow().isoformat() + "Z"
        
        sent_tx = {
            "txid": txid,
            "wallet": selected_wallet,
            "recipient": request.recipient,
            "amount_btc": request.amount_btc,
            "fee_sat": request.fee_sat,
            "status": "broadcast",
            "created_at": broadcast_time,
            "broadcast_at": broadcast_time,
            "confirmations": 0
        }
        
        sent_data["transactions"].append(sent_tx)
        save_sent_transactions(sent_data)
        
        logger.info(f"Transaction {txid} broadcast and recorded")
        
        return TransactionBroadcastResponse(
            txid=txid,
            wallet=selected_wallet,
            status="broadcast",
            broadcast_time=broadcast_time
        )
    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"Broadcast error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except (RPCConnectionError, RPCMethodError) as e:
        logger.error(f"RPC error during broadcast: {e}")
        raise HTTPException(
            status_code=503,
            detail="Cannot connect to Bitcoin RPC"
        )
    except Exception as e:
        logger.error(f"Unexpected error broadcasting transaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sent-history", response_model=dict)
async def get_sent_history():
    """
    Get history of sent transactions.
    
    Returns:
        Dict with list of sent transactions
    """
    try:
        logger.info("GET /tx/sent-history")
        data = load_sent_transactions()
        return data
    except Exception as e:
        logger.error(f"Error loading sent history: {e}")
        raise HTTPException(status_code=500, detail="Error loading transaction history")


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

