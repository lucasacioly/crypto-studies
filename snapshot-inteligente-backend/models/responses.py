from pydantic import BaseModel, Field
from typing import Dict
from datetime import datetime

class MempoolSummary(BaseModel):
    """Response for /api/mempool/summary endpoint."""
    
    tx_count: int = Field(..., description="Total transactions in mempool")
    total_vsize: int = Field(..., description="Total virtual size in vB")
    avg_fee_rate: float = Field(..., description="Average fee rate in sat/vB")
    min_fee_rate: float = Field(..., description="Minimum fee rate in sat/vB")
    max_fee_rate: float = Field(..., description="Maximum fee rate in sat/vB")
    fee_distribution: Dict[str, int] = Field(
        ..., 
        description="Count of transactions by fee category (low, medium, high)"
    )
    timestamp: str = Field(..., description="ISO 8601 timestamp when data was fetched")
    
    class Config:
        json_schema_extra = {
            "example": {
                "tx_count": 12345,
                "total_vsize": 3456789,
                "avg_fee_rate": 42.3,
                "min_fee_rate": 5.1,
                "max_fee_rate": 120.8,
                "fee_distribution": {"low": 3200, "medium": 7000, "high": 2145},
                "timestamp": "2026-05-01T14:30:00"
            }
        }

class BlockchainLag(BaseModel):
    """Response for /api/blockchain/lag endpoint."""
    
    blocks: int = Field(..., description="Number of blocks in main chain")
    headers: int = Field(..., description="Number of headers received")
    lag: int = Field(..., description="Difference between headers and blocks")
    timestamp: str = Field(..., description="ISO 8601 timestamp when data was fetched")
    
    class Config:
        json_schema_extra = {
            "example": {
                "blocks": 572061,
                "headers": 572120,
                "lag": 59,
                "timestamp": "2026-05-01T14:30:00"
            }
        }

class HealthStatus(BaseModel):
    """Response for /health endpoint."""
    status: str = Field(..., description="Overall status: ok or error")
    rpc: str = Field(..., description="RPC connection status: connected or disconnected")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
