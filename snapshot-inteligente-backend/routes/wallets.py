"""
Wallet management endpoints for Tarefa 3 (Task 3).
Handles wallet selection, listing, and status.
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from typing import List, Optional
import logging
from models.transactions import (
    WalletListResponse,
    WalletSelectResponse,
    WalletStatus,
    WalletInfo
)
from layers.rpc_client import RPCClient
from models.errors import RPCConnectionError, RPCMethodError
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/wallet", tags=["wallet"])


class WalletSelectRequest(BaseModel):
    """Request body for wallet selection."""
    wallet: str


def get_rpc_client() -> RPCClient:
    """Get the RPC client instance."""
    from dependencies import rpc_client
    return rpc_client


@router.get("/list", response_model=WalletListResponse)
async def list_wallets(rpc_client: RPCClient = Depends(get_rpc_client)):
    """
    List all available and loaded wallets.
    
    Returns:
        WalletListResponse with available, loaded, and selected wallets
        
    Raises:
        503: RPC connection failed
    """
    try:
        logger.info("GET /wallet/list")
        
        # Get list of wallet directories
        wallet_dir_data = rpc_client.list_wallet_dir()
        available_wallets = [w["name"] for w in wallet_dir_data.get("wallets", [])]
        
        # Get loaded wallets
        loaded_wallets = rpc_client.list_wallets()
        
        # Get selected wallet
        selected_wallet = rpc_client.get_selected_wallet()
        
        logger.info(f"Available wallets: {available_wallets}, Loaded: {loaded_wallets}, Selected: {selected_wallet}")
        
        return WalletListResponse(
            available_wallets=available_wallets,
            loaded_wallets=loaded_wallets,
            selected_wallet=selected_wallet
        )
    except (RPCConnectionError, RPCMethodError) as e:
        logger.error(f"Error listing wallets: {e}")
        raise HTTPException(
            status_code=503,
            detail="Cannot connect to Bitcoin RPC"
        )
    except Exception as e:
        logger.error(f"Unexpected error listing wallets: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/select", response_model=WalletSelectResponse)
async def select_wallet(
    request: WalletSelectRequest,
    rpc_client: RPCClient = Depends(get_rpc_client)
):
    """
    Select a wallet for subsequent operations.
    
    Args:
        request: Request body with wallet name
        
    Returns:
        WalletSelectResponse with selected wallet info
        
    Raises:
        400: Wallet does not exist
        503: RPC connection failed
    """
    try:
        wallet = request.wallet
        logger.info(f"POST /wallet/select - wallet: {wallet}")
        
        # Get list of available wallets
        wallet_dir_data = rpc_client.list_wallet_dir()
        available_wallets = [w["name"] for w in wallet_dir_data.get("wallets", [])]
        
        if wallet not in available_wallets:
            logger.warning(f"Wallet {wallet} not found in available wallets")
            raise HTTPException(
                status_code=400,
                detail=f"Wallet '{wallet}' does not exist"
            )
        
        # Load wallet if not already loaded
        loaded_wallets = rpc_client.list_wallets()
        if wallet not in loaded_wallets:
            logger.info(f"Loading wallet {wallet}")
            rpc_client.load_wallet(wallet)
        
        # Select the wallet
        rpc_client.select_wallet(wallet)
        
        # Get wallet info
        wallet_info_raw = rpc_client.call("getwalletinfo", wallet=wallet)
        
        wallet_info = WalletInfo(
            walletname=wallet_info_raw.get("walletname", wallet),
            balance=float(wallet_info_raw.get("balance", 0)),
            txcount=int(wallet_info_raw.get("txcount", 0))
        )
        
        logger.info(f"Selected wallet: {wallet}, balance: {wallet_info.balance}")
        
        return WalletSelectResponse(
            selected_wallet=wallet,
            wallet_info=wallet_info
        )
    except HTTPException:
        raise
    except (RPCConnectionError, RPCMethodError) as e:
        logger.error(f"Error selecting wallet: {e}")
        raise HTTPException(
            status_code=503,
            detail="Cannot connect to Bitcoin RPC"
        )
    except Exception as e:
        logger.error(f"Unexpected error selecting wallet: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/status", response_model=WalletStatus)
async def get_wallet_status(rpc_client: RPCClient = Depends(get_rpc_client)):
    """
    Get current selected wallet status (balance and UTXOs).
    
    Returns:
        WalletStatus with wallet name, balance, and UTXO count
        
    Raises:
        400: No wallet selected
        503: RPC connection failed
    """
    try:
        logger.info("GET /wallet/status")
        
        selected_wallet = rpc_client.get_selected_wallet()
        if not selected_wallet:
            raise HTTPException(
                status_code=400,
                detail="No wallet selected. Use POST /wallet/select first."
            )
        
        # Get wallet info
        wallet_info_raw = rpc_client.call("getwalletinfo")
        balance = float(wallet_info_raw.get("balance", 0))
        
        # Get UTXOs
        utxos_raw = rpc_client.call("listunspent")
        utxos_count = len(utxos_raw)
        
        logger.info(f"Wallet {selected_wallet} status: balance={balance}, utxos={utxos_count}")
        
        return WalletStatus(
            wallet=selected_wallet,
            balance=balance,
            utxos=utxos_count
        )
    except HTTPException:
        raise
    except (RPCConnectionError, RPCMethodError) as e:
        logger.error(f"Error getting wallet status: {e}")
        raise HTTPException(
            status_code=503,
            detail="Cannot connect to Bitcoin RPC"
        )
    except Exception as e:
        logger.error(f"Unexpected error getting wallet status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
