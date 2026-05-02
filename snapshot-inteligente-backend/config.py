from pydantic_settings import BaseSettings
from typing import Optional

class Config(BaseSettings):
    # Bitcoin RPC
    BITCOIN_RPC_HOST: str = "localhost"
    BITCOIN_RPC_PORT: int = 8332
    BITCOIN_RPC_USER: str
    BITCOIN_RPC_PASSWORD: str
    RPC_TIMEOUT_SECONDS: int = 5
    
    # Cache
    CACHE_TTL_SECONDS: int = 10
    
    # Fee thresholds (sat/vB)
    FEE_LOW_THRESHOLD: float = 10.0
    FEE_HIGH_THRESHOLD: float = 50.0
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:4200"
    
    # ZMQ Event Streaming (Task 2)
    ZMQ_HOST: str = "localhost"
    ZMQ_PORT: int = 28332
    
    # Event Buffer Capacity
    EVENT_BUFFER_BLOCKS: int = 50
    EVENT_BUFFER_TRANSACTIONS: int = 500
    
    # Environment
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True

config = Config()
