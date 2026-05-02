# Snapshot Inteligente - Architecture Design

**Date:** 2026-05-01  
**Project:** Bitcoin Node State Interpretation System  
**Status:** Design Approved

---

## **Vision & Objectives**

Build a lightweight backend service and frontend dashboard to interpret Bitcoin node state by analyzing mempool data and blockchain sync status in real-time. This system performs intelligent data analysis on raw RPC calls without persistent storage, focusing on clarity, maintainability, and future ZMQ event extensibility.

### **High-Level Goals**
- **Mempool Intelligence:** Extract and visualize transaction fee distribution and network activity
- **Node Sync Status:** Monitor blockchain synchronization lag to detect network delays
- **Layered Architecture:** Enable clean separation of concerns for testability and future Task 2 integration
- **Configurable Thresholds:** Allow runtime customization of fee classification boundaries
- **Performance:** Minimize RPC calls through intelligent caching (5-30s TTL)

---

## **1. Project Structure**

```
snapshot-inteligente/
├── backend/
│   ├── app.py                       # FastAPI application entry point
│   ├── config.py                    # Configuration management
│   ├── dependencies.py              # Dependency injection setup
│   ├── requirements.txt             # Python dependencies
│   ├── layers/
│   │   ├── __init__.py
│   │   ├── rpc_client.py           # Bitcoin RPC communication (Task 1)
│   │   ├── cache_layer.py          # Time-based caching decorator (Task 1)
│   │   ├── bitcoin_service.py      # Business logic & interpretation (Task 1)
│   │   └── event_buffer.py         # Event streaming & ZMQ listener (Task 2)
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── health.py               # Health check endpoint
│   │   ├── mempool.py              # Mempool summary endpoints (Task 1)
│   │   ├── blockchain.py           # Blockchain sync endpoints (Task 1)
│   │   └── events.py               # Event streaming endpoints (Task 2)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── errors.py               # Custom exception classes
│   │   └── responses.py            # Pydantic response schemas
│   ├── utils/
│   │   ├── __init__.py
│   │   └── logger.py               # Logging configuration
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_rpc_client.py
│   │   ├── test_cache_layer.py
│   │   ├── test_bitcoin_service.py
│   │   └── test_event_buffer.py     # Tests for Task 2
│   └── .env.example                # Environment variables template
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/
│   │   │   │   ├── dashboard.component.ts
│   │   │   │   ├── dashboard.component.html
│   │   │   │   ├── dashboard.component.scss
│   │   │   │   ├── mempool-card.component.ts
│   │   │   │   ├── mempool-card.component.html
│   │   │   │   ├── mempool-card.component.scss
│   │   │   │   ├── blockchain-card.component.ts
│   │   │   │   ├── blockchain-card.component.html
│   │   │   │   ├── blockchain-card.component.scss
│   │   │   │   ├── event-activity-card.component.ts      # Task 2
│   │   │   │   ├── event-activity-card.component.html
│   │   │   │   └── event-activity-card.component.scss
│   │   │   ├── services/
│   │   │   │   ├── bitcoin-api.service.ts
│   │   │   │   ├── bitcoin-api.service.spec.ts
│   │   │   │   └── auto-refresh.service.ts
│   │   │   ├── models/
│   │   │   │   ├── mempool.model.ts
│   │   │   │   ├── blockchain.model.ts
│   │   │   │   └── events.model.ts                        # Task 2
│   │   │   └── app.module.ts
│   │   └── environments/
│   │       ├── environment.ts
│   │       └── environment.prod.ts
│   ├── angular.json
│   ├── package.json
│   ├── tailwind.config.js
│   └── Dockerfile
│
├── docs/
│   └── superpowers/
│       ├── specs/
│       │   └── 2026-05-01-snapshot-inteligente-design.md (this file)
│       └── plans/
│           └── 2026-05-01-snapshot-inteligente-implementation.md
│
├── docker-compose.yml
└── README.md
```

---

## **2. Layered Architecture Design**

### **2.1 RPC Client Layer (`layers/rpc_client.py`)**

**Purpose:** Handle all direct communication with Bitcoin Core RPC. No business logic—purely transport.

**Key Responsibilities:**
- Establish TCP connection to Bitcoin Core at configurable host/port
- Serialize method calls and parameters to JSON-RPC 2.0 format
- Deserialize responses and handle RPC-level errors
- Implement connection pooling for efficiency
- Provide retry logic with exponential backoff for transient failures

**Core Methods:**

```python
class RPCClient:
    def __init__(self, host: str, port: int, user: str, password: str, timeout: int = 5):
        """Initialize RPC connection parameters."""
        
    def call(self, method: str, params: List[Any] = None) -> dict:
        """
        Execute raw RPC call.
        
        Args:
            method: RPC method name (e.g., 'getmempoolinfo')
            params: List of parameters or empty list
            
        Returns:
            Response dict from Bitcoin Core
            
        Raises:
            RPCConnectionError: Network/connection issues
            RPCMethodError: Bitcoin Core returns error response
        """
        
    def _make_request(self, payload: dict) -> dict:
        """Internal: Send HTTP POST request to RPC endpoint."""
        
    def _validate_response(self, response: dict) -> None:
        """Internal: Check for RPC errors in response."""
```

**Error Handling:**
- `RPCConnectionError`: Raised on network failures (connection refused, timeout)
  - Includes retry count and last error message
  - Propagates to upper layers for 503 Service Unavailable response
- `RPCMethodError`: Raised when RPC call returns error code
  - Includes RPC error message and code
  - Logged for debugging

**Configuration:**
- `BITCOIN_RPC_HOST` (env var, default: `localhost`)
- `BITCOIN_RPC_PORT` (env var, default: `8332`)
- `BITCOIN_RPC_USER` (env var, required)
- `BITCOIN_RPC_PASSWORD` (env var, required)
- `RPC_TIMEOUT_SECONDS` (env var, default: `5`)

---

### **2.2 Cache Layer (`layers/cache_layer.py`)**

**Purpose:** Reduce RPC call frequency by caching responses with time-based expiration.

**Key Responsibilities:**
- Store responses with TTL (Time-To-Live)
- Provide decorator syntax for easy application to methods
- Track cache hits/misses for metrics
- Auto-evict expired entries

**Core Mechanism:**

```python
class CacheLayer:
    def __init__(self):
        """Initialize in-memory cache storage (dict-based)."""
        self.cache: Dict[str, CacheEntry] = {}
        self.hits: int = 0
        self.misses: int = 0
        
    def cached(self, ttl_seconds: int = 10):
        """
        Decorator factory for caching method responses.
        
        Usage:
            @cache_layer.cached(ttl_seconds=10)
            def get_mempool_summary(self):
                return ...
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                # Create cache key from function name + args
                cache_key = self._make_key(func.__name__, args, kwargs)
                
                # Check if cache hit and not expired
                if cache_key in self.cache:
                    entry = self.cache[cache_key]
                    if time.time() < entry.expiry_time:
                        self.hits += 1
                        return entry.data
                
                # Cache miss or expired
                self.misses += 1
                result = func(*args, **kwargs)
                self.cache[cache_key] = CacheEntry(
                    data=result,
                    expiry_time=time.time() + ttl_seconds
                )
                return result
            return wrapper
        return decorator
        
    def _make_key(self, func_name: str, args, kwargs) -> str:
        """Generate unique cache key from function name and parameters."""
        
    def get_stats(self) -> dict:
        """Return cache hit/miss statistics."""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": self.hits / (self.hits + self.misses) if (self.hits + self.misses) > 0 else 0
        }
```

**Cache Entry Structure:**
```python
@dataclass
class CacheEntry:
    data: Any
    expiry_time: float
```

**Configuration:**
- `CACHE_TTL_SECONDS` (env var, default: `10`, range: `5-30`)
- Cache is in-memory only (no persistence)
- Cleared on application restart

**Behavior:**
- Cache key includes method name but NOT class instance (singleton pattern)
- If method has no parameters, key is just method name
- Expired entries remain in memory until next cache eviction cycle
- No automatic background cleanup (eviction on access)

---

### **2.3 Business Logic Layer (`layers/bitcoin_service.py`)**

**Purpose:** Interpret raw Bitcoin data, classify transactions, and compute derived metrics.

**Key Responsibilities:**
- Fetch mempool data via RPC
- Classify transactions by fee levels using configurable thresholds
- Calculate mempool statistics (averages, distributions)
- Compare blockchain headers vs blocks to detect sync lag
- Apply caching decorator to expensive operations
- Validate and transform data into domain models

**Core Methods:**

```python
class BitcoinService:
    def __init__(self, rpc_client: RPCClient, cache_layer: CacheLayer):
        self.rpc = rpc_client
        self.cache = cache_layer
        self.config = Config()
        
    @property
    def fee_low_threshold(self) -> float:
        """Low fee threshold in sat/vB (e.g., 10)."""
        return self.config.FEE_LOW_THRESHOLD
        
    @property
    def fee_high_threshold(self) -> float:
        """High fee threshold in sat/vB (e.g., 50)."""
        return self.config.FEE_HIGH_THRESHOLD
    
    @cache_layer.cached(ttl_seconds=10)
    def get_mempool_summary(self) -> MempoolSummary:
        """
        Analyze mempool and return fee distribution summary.
        
        Flow:
        1. Fetch getmempoolinfo → basic stats (size, bytes)
        2. Fetch getrawmempool(true) → detailed TX info including fees
        3. Calculate stats: avg fee, min/max, distribution
        4. Classify transactions into low/medium/high buckets
        5. Return MempoolSummary model
        
        Returns:
            MempoolSummary with:
                - tx_count: total transactions
                - total_vsize: combined virtual size
                - avg_fee_rate: average sat/vB
                - min_fee_rate: minimum sat/vB
                - max_fee_rate: maximum sat/vB
                - fee_distribution: {low: N, medium: N, high: N}
                - timestamp: when fetched
        """
        mempool_info = self.rpc.call('getmempoolinfo')
        raw_mempool = self.rpc.call('getrawmempool', [True])
        
        # Extract fee rates from raw mempool
        fee_rates = [tx_data['fees']['base'] / tx_data['vsize'] 
                     for tx_data in raw_mempool.values()]
        
        # Classify by threshold
        low_count = sum(1 for rate in fee_rates if rate < self.fee_low_threshold)
        medium_count = sum(1 for rate in fee_rates 
                          if self.fee_low_threshold <= rate <= self.fee_high_threshold)
        high_count = sum(1 for rate in fee_rates if rate > self.fee_high_threshold)
        
        return MempoolSummary(
            tx_count=mempool_info['size'],
            total_vsize=mempool_info['total_fee'] if 'total_fee' in mempool_info else 0,
            avg_fee_rate=sum(fee_rates) / len(fee_rates) if fee_rates else 0,
            min_fee_rate=min(fee_rates) if fee_rates else 0,
            max_fee_rate=max(fee_rates) if fee_rates else 0,
            fee_distribution={
                'low': low_count,
                'medium': medium_count,
                'high': high_count
            },
            timestamp=datetime.utcnow().isoformat()
        )
    
    @cache_layer.cached(ttl_seconds=10)
    def get_blockchain_lag(self) -> BlockchainLag:
        """
        Compare blockchain synchronization status.
        
        Flow:
        1. Fetch getblockchaininfo
        2. Extract blocks and headers counts
        3. Calculate lag as difference
        4. Return BlockchainLag model
        
        Returns:
            BlockchainLag with:
                - blocks: number of blocks in main chain
                - headers: number of headers received
                - lag: difference (headers - blocks)
                - timestamp: when fetched
        """
        blockchain_info = self.rpc.call('getblockchaininfo')
        
        blocks = blockchain_info['blocks']
        headers = blockchain_info['headers']
        lag = headers - blocks
        
        return BlockchainLag(
            blocks=blocks,
            headers=headers,
            lag=lag,
            timestamp=datetime.utcnow().isoformat()
        )
```

**Fee Classification Logic:**

| Category | Condition | Default Range |
|----------|-----------|---|
| Low | fee_rate < FEE_LOW_THRESHOLD | < 10 sat/vB |
| Medium | FEE_LOW_THRESHOLD ≤ fee_rate ≤ FEE_HIGH_THRESHOLD | 10-50 sat/vB |
| High | fee_rate > FEE_HIGH_THRESHOLD | > 50 sat/vB |

**Configuration:**
- `FEE_LOW_THRESHOLD` (env var, default: `10` sat/vB)
- `FEE_HIGH_THRESHOLD` (env var, default: `50` sat/vB)

---

### **2.4 API Routes Layer**

**File: `routes/mempool.py`**

```python
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from models.responses import MempoolSummary
from layers.bitcoin_service import BitcoinService

router = APIRouter(prefix="/api/mempool", tags=["mempool"])

@router.get("/summary", response_model=MempoolSummary)
async def get_mempool_summary(service: BitcoinService = Depends(get_bitcoin_service)):
    """
    GET /api/mempool/summary
    
    Returns current mempool analysis including fee distribution.
    
    Response (200 OK):
    {
        "tx_count": 12345,
        "total_vsize": 3456789,
        "avg_fee_rate": 42.3,
        "min_fee_rate": 5.1,
        "max_fee_rate": 120.8,
        "fee_distribution": {
            "low": 3200,
            "medium": 7000,
            "high": 2145
        },
        "timestamp": "2026-05-01T14:30:00"
    }
    
    Errors:
    - 503 Service Unavailable: RPC connection failed
    """
    try:
        return await service.get_mempool_summary()
    except RPCConnectionError as e:
        raise HTTPException(status_code=503, detail="Bitcoin RPC unavailable")
    except Exception as e:
        logger.error(f"Error in mempool summary: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

**File: `routes/blockchain.py`**

```python
from fastapi import APIRouter, HTTPException
from models.responses import BlockchainLag
from layers.bitcoin_service import BitcoinService

router = APIRouter(prefix="/api/blockchain", tags=["blockchain"])

@router.get("/lag", response_model=BlockchainLag)
async def get_blockchain_lag(service: BitcoinService = Depends(get_bitcoin_service)):
    """
    GET /api/blockchain/lag
    
    Returns blockchain synchronization lag (headers vs blocks).
    
    Response (200 OK):
    {
        "blocks": 572061,
        "headers": 572120,
        "lag": 59,
        "timestamp": "2026-05-01T14:30:00"
    }
    
    Errors:
    - 503 Service Unavailable: RPC connection failed
    """
    try:
        return await service.get_blockchain_lag()
    except RPCConnectionError as e:
        raise HTTPException(status_code=503, detail="Bitcoin RPC unavailable")
    except Exception as e:
        logger.error(f"Error in blockchain lag: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

**File: `routes/health.py`**

```python
from fastapi import APIRouter, HTTPException
from layers.rpc_client import RPCClient

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check(rpc_client: RPCClient = Depends(get_rpc_client)):
    """
    GET /health
    
    Check API and RPC connectivity.
    
    Response (200 OK):
    {
        "status": "ok",
        "rpc": "connected",
        "timestamp": "2026-05-01T14:30:00"
    }
    
    Response (503 Service Unavailable):
    {
        "status": "error",
        "rpc": "disconnected",
        "message": "Cannot reach Bitcoin RPC"
    }
    """
    try:
        rpc_client.call('getblockchaininfo')
        return {
            "status": "ok",
            "rpc": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={"status": "error", "rpc": "disconnected", "message": str(e)}
        )
```

---

## **3. Data Models**

**File: `models/responses.py`**

```python
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
        schema_extra = {
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
        schema_extra = {
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
```

---

## **4. Error Handling Strategy**

**Custom Exceptions** (`utils/errors.py`):

```python
class BitcoinServiceError(Exception):
    """Base exception for all service errors."""
    pass

class RPCConnectionError(BitcoinServiceError):
    """Raised when RPC connection fails."""
    def __init__(self, message: str, retries: int = 0):
        self.message = message
        self.retries = retries
        super().__init__(f"RPC Connection Error (attempts: {retries}): {message}")

class RPCMethodError(BitcoinServiceError):
    """Raised when RPC method returns error."""
    def __init__(self, method: str, error_code: int, error_message: str):
        self.method = method
        self.error_code = error_code
        self.error_message = error_message
        super().__init__(f"RPC Method '{method}' failed: [{error_code}] {error_message}")
```

**HTTP Error Responses:**

| Status | Scenario | Response Body |
|--------|----------|---|
| 200 | Successful request | Pydantic model (JSON) |
| 503 | RPC unavailable | `{"detail": "Bitcoin RPC unavailable"}` |
| 500 | Unexpected error | `{"detail": "Internal server error"}` |

---

## **5. Configuration Management**

**File: `config.py`**

```python
from pydantic_settings import BaseSettings

class Config(BaseSettings):
    # Bitcoin RPC
    BITCOIN_RPC_HOST: str = "localhost"
    BITCOIN_RPC_PORT: int = 8332
    BITCOIN_RPC_USER: str
    BITCOIN_RPC_PASSWORD: str
    RPC_TIMEOUT_SECONDS: int = 5
    
    # Cache
    CACHE_TTL_SECONDS: int = 10
    
    # Fee thresholds
    FEE_LOW_THRESHOLD: float = 10.0  # sat/vB
    FEE_HIGH_THRESHOLD: float = 50.0  # sat/vB
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_WORKERS: int = 4
    
    # Frontend
    FRONTEND_URL: str = "http://localhost:4200"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
```

**File: `.env.example`**

```
BITCOIN_RPC_HOST=localhost
BITCOIN_RPC_PORT=8332
BITCOIN_RPC_USER=bitcoin
BITCOIN_RPC_PASSWORD=your-secure-password
RPC_TIMEOUT_SECONDS=5

CACHE_TTL_SECONDS=10
FEE_LOW_THRESHOLD=10
FEE_HIGH_THRESHOLD=50

API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_URL=http://localhost:4200
```

---

## **6. Frontend Architecture**

### **6.1 Component Structure**

**DashboardComponent** (Main Container)
- Layout: Two-column grid with cards
- Manages global state (loading, error states)
- Handles auto-refresh timer

**MempoolCardComponent**
- Displays: Transaction count, fee rates, distribution chart
- Uses Angular Material Card + Chart library (e.g., Chart.js)
- Color coding: Green (low), Yellow (medium), Red (high)

**BlockchainCardComponent**
- Displays: Block count, header count, lag indicator
- Shows warning if lag > 5 blocks
- Color coding: Green (synced), Yellow (lagging), Red (critical)

### **6.2 Data Flow**

```
Dashboard Component
  ↓
Bitcoin API Service (HttpClient)
  ↓
GET /api/mempool/summary  →  MempoolCard
GET /api/blockchain/lag   →  BlockchainCard
  ↓
Auto-refresh interval (15s)
  ↓
Timer triggers new requests
```

### **6.3 Auto-Refresh Service**

```typescript
@Injectable()
export class AutoRefreshService {
  private refreshInterval$: Observable<number>;
  
  startAutoRefresh(intervalMs: number = 15000) {
    this.refreshInterval$ = interval(intervalMs);
    this.refreshInterval$.subscribe(() => {
      this.bitcoinApi.getMempoolSummary().subscribe(...);
      this.bitcoinApi.getBlockchainLag().subscribe(...);
    });
  }
}
```

### **6.4 UI Features**

- **Loading State:** Spinner overlay while fetching
- **Error State:** Error message with "Retry" button
- **Last Updated:** Timestamp display with relative time (e.g., "2 seconds ago")
- **Status Indicators:** 
  - Green circle: Connected and synced
  - Yellow circle: Connected but lagging
  - Red circle: Disconnected

---

## **7. Data Flow Examples**

### **Example 1: GET /api/mempool/summary**

```
User Request
  ↓
FastAPI Route Handler
  ↓
CacheLayer.cached decorator
  ├─ Check cache: "bitcoin_service_get_mempool_summary"
  ├─ If hit & not expired: Return cached data
  └─ If miss or expired:
      ↓
      BitcoinService.get_mempool_summary()
        ↓
        RPCClient.call('getmempoolinfo')
          ↓
          Bitcoin Core responds
        ↓
        RPCClient.call('getrawmempool', [True])
          ↓
          Bitcoin Core responds with all TX data
        ↓
        Business Logic:
          - Extract fee rates from each transaction
          - Calculate avg, min, max
          - Classify into low/medium/high
          - Build fee_distribution dict
        ↓
        MempoolSummary(...)  ← Pydantic model
        ↓
      Store in cache with TTL
      ↓
Return JSON response to client
  ↓
Angular receives & updates MempoolCard
```

### **Example 2: Cache Hit Scenario**

```
Request #1 at T=0s
  → Cache miss
  → RPC calls executed
  → Response cached until T=10s
  → Return data

Request #2 at T=3s (3 seconds later)
  → Cache hit (not expired)
  → Return cached data immediately
  → No RPC calls made
  → Faster response

Request #3 at T=11s (11 seconds later)
  → Cache expired (TTL=10s)
  → Cache miss
  → RPC calls executed again
```

---

## **8. Error Handling Flow**

```
Client Request
  ↓
FastAPI Route
  ↓
Try:
  BitcoinService.get_mempool_summary()
    ↓
    RPCClient.call('getmempoolinfo')
      ↓
      Connection fails
        ↓
        Raise RPCConnectionError
      ↓
    Except RPCConnectionError:
      ↓
      Catch in Route Handler
      ↓
      Raise HTTPException(status_code=503)
      ↓
      Return JSON error response
      ↓
Client receives 503 + error detail
  ↓
Frontend shows "Bitcoin RPC unavailable" message
  ↓
User can click "Retry"
```

---

## **9. Testing Strategy**

### **Unit Tests** (`tests/test_rpc_client.py`)
- Mock Bitcoin Core responses
- Test RPC call serialization/deserialization
- Test error handling (connection failures, invalid JSON)

### **Unit Tests** (`tests/test_cache_layer.py`)
- Test cache hit/miss scenarios
- Test TTL expiration
- Test cache key generation

### **Unit Tests** (`tests/test_bitcoin_service.py`)
- Mock RPC client
- Test fee classification logic
- Test lag calculation
- Test MempoolSummary and BlockchainLag model creation

### **Integration Tests**
- Test full stack with real or containerized Bitcoin Core
- Test endpoint responses
- Test error scenarios (RPC timeout, connection refused)

---

## **10. Deployment Considerations**

### **Backend Deployment**
- Docker container with Python 3.11+
- Environment variables via `.env` file
- Health check endpoint for container orchestration
- Logs to stdout (container-friendly)

### **Frontend Deployment**
- Angular build (production)
- Static file serving via nginx or CDN
- CORS configuration to match backend URL

### **Bitcoin Core Integration**
- Task 1: Assumes Bitcoin Core on localhost:8332
- RPC credentials passed via environment variables
- Bitcoin Core should be configured with:
  ```
  server=1
  rpcuser=bitcoin
  rpcpassword=secure-password
  rpcallowip=127.0.0.1
  ```

---

## **11. Success Criteria**

✅ Backend exposes `/api/mempool/summary` returning correct fee distribution  
✅ Backend exposes `/api/blockchain/lag` with accurate block/header counts  
✅ Cache reduces RPC calls by ~80% during active usage  
✅ Frontend dashboards update every 15 seconds via auto-refresh  
✅ Health check endpoint reliably detects RPC availability  
✅ All error scenarios handled gracefully with user-friendly messages  
✅ Configuration via environment variables without hardcoding  

---

## **12. Task 2: Real-Time Event Streaming via ZMQ**

### **12.1 Overview**

Task 2 extends the snapshot system with **real-time Bitcoin event streaming** using ZeroMQ (ZMQ). Instead of polling RPC every 15 seconds, the backend now listens to Bitcoin Core's ZMQ event stream for immediate block and transaction notifications.

**Key Features:**
- **ZMQ Event Listener:** Async listener for hashblock and rawtx topics
- **Circular Buffers:** Keep last 50 blocks and 500 transactions in memory
- **Event REST Endpoints:** Serve buffered events to frontend
- **State Comparison:** Detect blockchain divergence/reorg scenarios
- **Thread-Safe Access:** AsyncIO locks for concurrent access

### **12.2 Architecture**

#### **New Layer: Event Buffer (`layers/event_buffer.py`)**

Manages in-memory circular buffers for Bitcoin events:

```python
@dataclass
class BlockEvent:
    """Represents a Bitcoin block event."""
    block_hash: str
    block_height: int
    timestamp: str
    received_at: float  # Unix timestamp
    
@dataclass
class TransactionEvent:
    """Represents a Bitcoin transaction event."""
    txid: str
    timestamp: str
    received_at: float

class EventBuffer:
    """
    Manages circular buffers for block and transaction events.
    Thread-safe using asyncio.Lock.
    """
    def __init__(self, block_capacity: int = 50, tx_capacity: int = 500):
        self.block_capacity = block_capacity
        self.tx_capacity = tx_capacity
        self.blocks: Deque[BlockEvent] = deque(maxlen=block_capacity)
        self.transactions: Deque[TransactionEvent] = deque(maxlen=tx_capacity)
        self.lock = asyncio.Lock()
    
    async def add_block(self, block_event: BlockEvent) -> None:
        """Add block to circular buffer (thread-safe)."""
        async with self.lock:
            self.blocks.append(block_event)
    
    async def add_transaction(self, tx_event: TransactionEvent) -> None:
        """Add transaction to circular buffer (thread-safe)."""
        async with self.lock:
            self.transactions.append(tx_event)
    
    async def get_recent_blocks(self, limit: int = None) -> List[BlockEvent]:
        """Get recent blocks from buffer."""
        async with self.lock:
            if limit:
                return list(self.blocks)[-limit:]
            return list(self.blocks)
    
    async def get_recent_transactions(self, limit: int = None) -> List[TransactionEvent]:
        """Get recent transactions from buffer."""
        async with self.lock:
            if limit:
                return list(self.transactions)[-limit:]
            return list(self.transactions)
```

#### **ZMQ Listener (`layers/event_buffer.py` - ZMQListener class)**

Asynchronous listener for Bitcoin Core ZMQ events:

```python
class ZMQListener:
    """
    Listens to Bitcoin Core ZMQ events (hashblock, rawtx).
    Pushes events into EventBuffer.
    """
    def __init__(self, event_buffer: EventBuffer, zmq_host: str = "localhost", zmq_port: int = 28332):
        self.event_buffer = event_buffer
        self.zmq_host = zmq_host
        self.zmq_port = zmq_port
        self.running = False
    
    async def start(self) -> None:
        """Start listening for ZMQ events."""
        # Use AsyncIO + ZMQ to listen for:
        # - tcp://host:port with topic "hashblock"
        # - tcp://host:port with topic "rawtx"
        # Parse events and push to event_buffer
        
    async def stop(self) -> None:
        """Stop the listener."""
```

### **12.3 New REST Endpoints**

**File: `routes/events.py`**

```python
@router.get("/api/events/blocks", response_model=List[BlockEventResponse])
async def get_recent_blocks(
    limit: int = Query(10, ge=1, le=50),
    event_buffer: EventBuffer = Depends(get_event_buffer)
):
    """Get recent block events from buffer."""
    
@router.get("/api/events/transactions", response_model=List[TransactionEventResponse])
async def get_recent_transactions(
    limit: int = Query(20, ge=1, le=100),
    event_buffer: EventBuffer = Depends(get_event_buffer)
):
    """Get recent transaction events from buffer."""
    
@router.get("/api/events/state-comparison")
async def get_state_comparison(
    event_buffer: EventBuffer = Depends(get_event_buffer),
    rpc: RPCClient = Depends(get_rpc_client)
):
    """
    Compare buffered state with live RPC.
    Detect blockchain divergence/reorg.
    
    Returns:
    {
        "divergence_detected": false,
        "latest_block_from_buffer": {...},
        "latest_block_from_rpc": {...},
        "reorg_depth": 0
    }
    """
```

### **12.4 Integration in `app.py`**

```python
# Initialize EventBuffer
event_buffer = EventBuffer(block_capacity=50, tx_capacity=500)
zmq_listener = ZMQListener(event_buffer, zmq_host="localhost", zmq_port=28332)

@app.on_event("startup")
async def startup_event():
    """Start ZMQ listener on app startup."""
    asyncio.create_task(zmq_listener.start())

@app.on_event("shutdown")
async def shutdown_event():
    """Stop ZMQ listener on app shutdown."""
    await zmq_listener.stop()
```

### **12.5 Frontend Enhancement**

New components:
- **EventActivityCardComponent:** Shows recent block/transaction activity
- **BlockReorgIndicator:** Detects and visualizes blockchain divergence
- **EventStreamMonitor:** Real-time event counter/indicator

### **12.6 Configuration**

**New `.env` variables:**
```
ZMQ_HOST=localhost
ZMQ_PORT=28332
EVENT_BUFFER_BLOCKS=50
EVENT_BUFFER_TRANSACTIONS=500
```

**Bitcoin Core configuration (bitcoin.conf):**
```
zmqpubhashblock=tcp://127.0.0.1:28332
zmqpubrawtx=tcp://127.0.0.1:28332
```

### **12.7 Task 2 API Specification**

#### **Endpoint: GET /api/events/blocks**

Retrieve recent block events from the circular buffer.

**Query Parameters:**
- `limit` (int, optional): Number of blocks to return (1-50, default: 10)

**Request:**
```
GET /api/events/blocks?limit=10
```

**Response (200 OK):**
```json
[
  {
    "block_hash": "00000abc123def456...",
    "block_height": 572061,
    "timestamp": "2026-05-01T14:30:00Z",
    "received_at": 1746086400.123
  },
  {
    "block_hash": "00000def456abc789...",
    "block_height": 572060,
    "timestamp": "2026-05-01T14:29:30Z",
    "received_at": 1746086370.456
  }
]
```

**Error Responses:**
- `503 Service Unavailable`: ZMQ listener not connected

---

#### **Endpoint: GET /api/events/transactions**

Retrieve recent transaction events from the circular buffer.

**Query Parameters:**
- `limit` (int, optional): Number of transactions to return (1-100, default: 20)
- `fee_category` (str, optional): Filter by "low", "medium", or "high"

**Request:**
```
GET /api/events/transactions?limit=20&fee_category=high
```

**Response (200 OK):**
```json
[
  {
    "txid": "abc123def456...",
    "timestamp": "2026-05-01T14:30:15Z",
    "received_at": 1746086415.789,
    "size_vbytes": 152,
    "fee_rate_sat_vb": 75.5
  },
  {
    "txid": "def456abc789...",
    "timestamp": "2026-05-01T14:30:10Z",
    "received_at": 1746086410.234,
    "size_vbytes": 225,
    "fee_rate_sat_vb": 82.3
  }
]
```

**Error Responses:**
- `400 Bad Request`: Invalid fee_category
- `503 Service Unavailable`: ZMQ listener not connected

---

#### **Endpoint: GET /api/events/state-comparison**

Compare the buffer's latest block state with live RPC to detect blockchain divergence/reorg.

**Request:**
```
GET /api/events/state-comparison
```

**Response (200 OK - No Divergence):**
```json
{
  "status": "synced",
  "divergence_detected": false,
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
```

**Response (200 OK - Divergence Detected):**
```json
{
  "status": "divergence",
  "divergence_detected": true,
  "buffer_latest_block": {
    "hash": "00000abc123...",
    "height": 572061,
    "received_at": 1746086400.123
  },
  "rpc_latest_block": {
    "hash": "00000xyz789...",
    "height": 572061,
    "timestamp": "2026-05-01T14:30:00Z"
  },
  "reorg_depth": 1,
  "warning": "Blockchain reorg detected at height 572061",
  "comparison_timestamp": "2026-05-01T14:30:30Z"
}
```

**Error Responses:**
- `503 Service Unavailable`: RPC or ZMQ unavailable

---

#### **Endpoint: GET /api/events/stats** (Task 2 Enhancement)

Get event buffer statistics and connection status.

**Request:**
```
GET /api/events/stats
```

**Response (200 OK):**
```json
{
  "zmq_listener_status": "connected",
  "buffer_blocks_count": 42,
  "buffer_blocks_capacity": 50,
  "buffer_transactions_count": 385,
  "buffer_transactions_capacity": 500,
  "last_block_received": "2026-05-01T14:30:00Z",
  "last_transaction_received": "2026-05-01T14:30:28Z",
  "uptime_seconds": 3600,
  "events_received": {
    "blocks": 42,
    "transactions": 385
  }
}
```

---

### **12.7 Success Criteria for Task 2**

✅ ZMQ listener streams block/transaction events in real-time  
✅ EventBuffer maintains circular buffers (50 blocks, 500 txs)  
✅ `/api/events/blocks` and `/api/events/transactions` endpoints work  
✅ State comparison detects blockchain reorg scenarios  
✅ `/api/events/state-comparison` endpoint returns correct divergence status  
✅ Frontend displays event activity without manual refresh  
✅ All events persisted in memory only (no database)  
✅ Thread-safe access via asyncio.Lock  
✅ Event stats endpoint provides buffer status  

---

## **13. Deployment Roadmap**

### **Phase 1: Backend Complete (Task 1 + 2)**
- Docker container with FastAPI + ZMQ listener
- Health check includes ZMQ status
- Environment variables for all config

### **Phase 2: Frontend Complete**
- Angular dashboard with event cards
- Auto-refresh every 15s (RPC polling)
- Real-time event activity (ZMQ-pushed data)

### **Phase 3: External Deployment (Task 3)**
- VPS/Cloud hosting (AWS, Linode, etc)
- Reverse proxy (nginx) for HTTPS
- Firewall rules for RPC/ZMQ access
- CI/CD pipeline (GitHub Actions)