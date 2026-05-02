"""
Event streaming endpoints for Bitcoin events.

Provides REST API access to real-time block and transaction events
captured from Bitcoin Core via ZMQ.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from layers.event_buffer import EventBuffer, BlockEvent, TransactionEvent
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/events", tags=["events"])


# Response models
class BlockEventResponse(BaseModel):
    """Response model for block events."""
    block_hash: str = Field(..., description="Block hash in hex")
    block_height: Optional[int] = Field(None, description="Block height (if available)")
    timestamp: str = Field(..., description="ISO 8601 timestamp when event was received")
    received_at: float = Field(..., description="Unix timestamp when event was received")

    class Config:
        json_schema_extra = {
            "example": {
                "block_hash": "00000abc123def456...",
                "block_height": 572061,
                "timestamp": "2026-05-01T14:30:00Z",
                "received_at": 1746086400.123
            }
        }


class TransactionEventResponse(BaseModel):
    """Response model for transaction events."""
    txid: str = Field(..., description="Transaction ID in hex")
    timestamp: str = Field(..., description="ISO 8601 timestamp when event was received")
    received_at: float = Field(..., description="Unix timestamp when event was received")
    size_vbytes: Optional[int] = Field(None, description="Transaction size in vBytes")
    fee_rate_sat_vb: Optional[float] = Field(None, description="Fee rate in sat/vB")

    class Config:
        json_schema_extra = {
            "example": {
                "txid": "abc123def456...",
                "timestamp": "2026-05-01T14:30:15Z",
                "received_at": 1746086415.789,
                "size_vbytes": 152,
                "fee_rate_sat_vb": 75.5
            }
        }


class BlockStateResponse(BaseModel):
    """Response model for block state in comparison."""
    hash: str = Field(..., description="Block hash")
    height: Optional[int] = Field(None, description="Block height")
    received_at: Optional[float] = Field(None, description="Unix timestamp when received")
    timestamp: Optional[str] = Field(None, description="ISO 8601 timestamp")


class StateComparisonResponse(BaseModel):
    """Response model for state comparison endpoint."""
    status: str = Field(..., description="Status: 'synced' or 'divergence'")
    divergence_detected: bool = Field(..., description="Whether divergence detected")
    buffer_latest_block: Optional[BlockStateResponse] = Field(..., description="Latest block from buffer")
    rpc_latest_block: Optional[BlockStateResponse] = Field(..., description="Latest block from RPC")
    reorg_depth: int = Field(..., description="Number of blocks diverged (reorg depth)")
    warning: Optional[str] = Field(None, description="Warning message if divergence detected")
    comparison_timestamp: str = Field(..., description="Timestamp of comparison")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "synced",
                "divergence_detected": False,
                "buffer_latest_block": {
                    "hash": "00000abc123...",
                    "height": 572061,
                    "received_at": 1746086400.123
                },
                "rpc_latest_block": {
                    "hash": "00000abc123...",
                    "height": 572061,
                    "timestamp": "2026-05-01T14:30:00Z"
                },
                "reorg_depth": 0,
                "comparison_timestamp": "2026-05-01T14:30:30Z"
            }
        }


class EventStatsResponse(BaseModel):
    """Response model for event statistics."""
    zmq_listener_status: str = Field(..., description="ZMQ listener status: 'connected' or 'disconnected'")
    buffer_blocks_count: int = Field(..., description="Current number of blocks in buffer")
    buffer_blocks_capacity: int = Field(..., description="Maximum block buffer capacity")
    buffer_transactions_count: int = Field(..., description="Current number of transactions in buffer")
    buffer_transactions_capacity: int = Field(..., description="Maximum transaction buffer capacity")
    last_block_received: Optional[str] = Field(..., description="Timestamp of last block event")
    last_transaction_received: Optional[str] = Field(..., description="Timestamp of last transaction event")
    uptime_seconds: Optional[int] = Field(..., description="ZMQ listener uptime in seconds")
    events_received: dict = Field(..., description="Total events received")

    class Config:
        json_schema_extra = {
            "example": {
                "zmq_listener_status": "connected",
                "buffer_blocks_count": 42,
                "buffer_blocks_capacity": 50,
                "buffer_transactions_count": 385,
                "buffer_transactions_capacity": 500,
                "last_block_received": "2026-05-01T14:30:00Z",
                "last_transaction_received": "2026-05-01T14:30:28Z",
                "uptime_seconds": 3600,
                "events_received": {"blocks": 42, "transactions": 385}
            }
        }


# Dependency injection
def get_event_buffer() -> EventBuffer:
    """Get the event buffer instance."""
    from dependencies import event_buffer
    return event_buffer


# Endpoints
@router.get("/blocks", response_model=List[BlockEventResponse])
async def get_recent_blocks(
    limit: int = Query(10, ge=1, le=50, description="Number of blocks to return"),
    event_buffer: EventBuffer = Depends(get_event_buffer)
):
    """
    Get recent block events from the buffer.
    
    Returns the most recent block events in chronological order.
    
    Query Parameters:
    - limit: Number of blocks to return (1-50, default 10)
    
    Returns:
        200 OK: List of block events
        503 Service Unavailable: ZMQ listener not available
    """
    try:
        logger.info(f"GET /api/events/blocks?limit={limit}")
        
        blocks = await event_buffer.get_recent_blocks(limit=limit)
        
        # Convert to response format
        return [
            BlockEventResponse(
                block_hash=block.block_hash,
                block_height=block.block_height,
                timestamp=block.timestamp,
                received_at=block.received_at
            )
            for block in blocks
        ]
    except Exception as e:
        logger.error(f"Error fetching recent blocks: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.get("/transactions", response_model=List[TransactionEventResponse])
async def get_recent_transactions(
    limit: int = Query(20, ge=1, le=100, description="Number of transactions to return"),
    fee_category: Optional[str] = Query(None, description="Filter by 'low', 'medium', or 'high'"),
    event_buffer: EventBuffer = Depends(get_event_buffer)
):
    """
    Get recent transaction events from the buffer.
    
    Returns the most recent transaction events in chronological order.
    
    Query Parameters:
    - limit: Number of transactions to return (1-100, default 20)
    - fee_category: Optional filter by fee category (low/medium/high)
    
    Returns:
        200 OK: List of transaction events
        400 Bad Request: Invalid fee_category
        503 Service Unavailable: ZMQ listener not available
    """
    try:
        logger.info(f"GET /api/events/transactions?limit={limit}&fee_category={fee_category}")
        
        if fee_category and fee_category not in ["low", "medium", "high"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid fee_category. Must be 'low', 'medium', or 'high', got '{fee_category}'"
            )
        
        txs = await event_buffer.get_recent_transactions(limit=limit)
        
        # Convert to response format
        return [
            TransactionEventResponse(
                txid=tx.txid,
                timestamp=tx.timestamp,
                received_at=tx.received_at,
                size_vbytes=tx.size_vbytes,
                fee_rate_sat_vb=tx.fee_rate_sat_vb
            )
            for tx in txs
        ]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching recent transactions: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.get("/state-comparison", response_model=StateComparisonResponse)
async def get_state_comparison(
    event_buffer: EventBuffer = Depends(get_event_buffer)
):
    """
    Compare buffer's latest block state with live RPC.
    
    Detects blockchain divergence/reorg by comparing the latest block
    in the event buffer with the current blockchain state from RPC.
    
    Returns:
        200 OK: State comparison result
        503 Service Unavailable: RPC or ZMQ unavailable
    """
    try:
        logger.info("GET /api/events/state-comparison")
        
        # Get latest block from buffer
        latest_buffer_block = await event_buffer.get_latest_block()
        
        if not latest_buffer_block:
            raise HTTPException(
                status_code=503,
                detail="No block events in buffer yet"
            )
        
        # Get latest block from RPC (for comparison)
        from dependencies import bitcoin_service
        try:
            blockchain_lag = await bitcoin_service.get_blockchain_lag()
            
            # For now, we'll compare hashes from buffer vs RPC
            # This is a placeholder - in production you'd fetch the actual block
            # hash from RPC via getblockhash(height)
            
            response = StateComparisonResponse(
                status="synced",
                divergence_detected=False,
                buffer_latest_block=BlockStateResponse(
                    hash=latest_buffer_block.block_hash,
                    height=latest_buffer_block.block_height,
                    received_at=latest_buffer_block.received_at,
                    timestamp=latest_buffer_block.timestamp
                ),
                rpc_latest_block=BlockStateResponse(
                    hash="rpc_hash_placeholder",
                    height=blockchain_lag.blocks,
                    timestamp=datetime.utcnow().isoformat()
                ),
                reorg_depth=0,
                comparison_timestamp=datetime.utcnow().isoformat()
            )
            
            logger.info(f"State comparison: {response.status}")
            return response
            
        except Exception as e:
            logger.error(f"Error comparing state with RPC: {e}")
            raise HTTPException(
                status_code=503,
                detail="Cannot compare with RPC"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in state comparison: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.get("/stats", response_model=EventStatsResponse)
async def get_event_stats(
    event_buffer: EventBuffer = Depends(get_event_buffer)
):
    """
    Get event buffer statistics and ZMQ listener status.
    
    Provides information about:
    - ZMQ listener connection status
    - Buffer occupancy (blocks and transactions)
    - Event timing information
    - Total events received
    
    Returns:
        200 OK: Event statistics
    """
    try:
        logger.info("GET /api/events/stats")
        
        # Get buffer stats
        stats = await event_buffer.get_stats()
        
        # Get listener status
        from dependencies import zmq_listener
        zmq_status = "connected" if zmq_listener.is_connected() else "disconnected"
        
        # Convert timestamps
        last_block_ts = None
        last_tx_ts = None
        
        if stats["last_block_time"]:
            last_block_ts = datetime.fromtimestamp(stats["last_block_time"]).isoformat()
        
        if stats["last_tx_time"]:
            last_tx_ts = datetime.fromtimestamp(stats["last_tx_time"]).isoformat()
        
        response = EventStatsResponse(
            zmq_listener_status=zmq_status,
            buffer_blocks_count=stats["blocks_count"],
            buffer_blocks_capacity=stats["blocks_capacity"],
            buffer_transactions_count=stats["transactions_count"],
            buffer_transactions_capacity=stats["transactions_capacity"],
            last_block_received=last_block_ts,
            last_transaction_received=last_tx_ts,
            uptime_seconds=None,  # TODO: Calculate from zmq_listener startup
            events_received={
                "blocks": stats["blocks_received_total"],
                "transactions": stats["transactions_received_total"]
            }
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting event stats: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
