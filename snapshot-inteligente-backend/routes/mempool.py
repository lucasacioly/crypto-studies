from fastapi import APIRouter, Depends, HTTPException
from models.responses import MempoolSummary
from models.errors import RPCConnectionError, RPCMethodError
from layers.bitcoin_service import BitcoinService
from dependencies import get_bitcoin_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/mempool", tags=["mempool"])

@router.get("/summary", response_model=MempoolSummary)
async def get_mempool_summary(
    service: BitcoinService = Depends(get_bitcoin_service)
):
    """
    Get current mempool analysis including fee distribution.
    
    Returns:
        200 OK: MempoolSummary with tx stats and fee distribution
        503 Service Unavailable: RPC connection failed
    """
    try:
        logger.info("GET /api/mempool/summary")
        return service.get_mempool_summary()
    except RPCConnectionError as e:
        logger.error(f"Mempool summary error: {e}")
        raise HTTPException(
            status_code=503,
            detail="Bitcoin RPC unavailable"
        )
    except RPCMethodError as e:
        logger.error(f"Mempool RPC method error: {e}")
        raise HTTPException(
            status_code=503,
            detail="Bitcoin RPC method error"
        )
    except Exception as e:
        logger.error(f"Unexpected error in mempool summary: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
