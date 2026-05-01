from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from models.responses import HealthStatus
from models.errors import RPCConnectionError
from layers.rpc_client import RPCClient
from dependencies import get_rpc_client
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])

@router.get("/health", response_model=HealthStatus)
async def health_check(rpc_client: RPCClient = Depends(get_rpc_client)):
    """
    Check API and RPC connectivity.
    
    Returns:
        200 OK: {status: ok, rpc: connected}
        503 Service Unavailable: {status: error, rpc: disconnected}
    """
    try:
        rpc_client.call('getblockchaininfo')
        return HealthStatus(
            status="ok",
            rpc="connected",
            timestamp=datetime.utcnow().isoformat()
        )
    except RPCConnectionError as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "error",
                "rpc": "disconnected",
                "message": str(e)
            }
        )
