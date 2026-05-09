from fastapi import APIRouter, Depends, HTTPException
from models.responses import BlockchainLag
from models.errors import RPCConnectionError, RPCMethodError
from layers.bitcoin_service import BitcoinService
from dependencies import get_bitcoin_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/blockchain", tags=["blockchain"])

@router.get("/lag", response_model=BlockchainLag)
async def get_blockchain_lag(
    service: BitcoinService = Depends(get_bitcoin_service)
):
    """
    Get blockchain synchronization lag (headers vs blocks).
    
    Returns:
        200 OK: BlockchainLag with block counts and lag
        503 Service Unavailable: RPC connection failed
    """
    try:
        logger.info("GET /api/blockchain/lag")
        return service.get_blockchain_lag()
    except RPCConnectionError as e:
        logger.error(f"Blockchain lag error: {e}")
        raise HTTPException(
            status_code=503,
            detail="Bitcoin RPC unavailable"
        )
    except RPCMethodError as e:
        logger.error(f"Blockchain RPC method error: {e}")
        raise HTTPException(
            status_code=503,
            detail="Bitcoin RPC method error"
        )
    except Exception as e:
        logger.error(f"Unexpected error in blockchain lag: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
