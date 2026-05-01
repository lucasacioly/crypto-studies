# Snapshot Inteligente Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python FastAPI backend that analyzes Bitcoin mempool and blockchain state, plus an Angular frontend dashboard that visualizes this data with auto-refresh.

**Architecture:** Layered system with RPC Client → Cache Layer → Business Logic → Routes. Frontend fetches via HTTP every 15 seconds and displays fee distributions and sync lag.

**Tech Stack:** Python 3.11+, FastAPI, Pydantic, Angular 17+, TailwindCSS, Angular Material, Docker

---

## **File Structure Overview**

### Backend Project Tree
```
snapshot-inteligente-backend/
├── app.py                          # FastAPI application entry
├── config.py                       # Configuration from env vars
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment template
├── .gitignore
├── layers/
│   ├── __init__.py
│   ├── rpc_client.py              # Bitcoin RPC communication
│   ├── cache_layer.py             # Caching decorator
│   └── bitcoin_service.py         # Business logic
├── routes/
│   ├── __init__.py
│   ├── mempool.py                 # /api/mempool/* endpoints
│   ├── blockchain.py              # /api/blockchain/* endpoints
│   └── health.py                  # /health endpoint
├── models/
│   ├── __init__.py
│   ├── responses.py               # Pydantic response schemas
│   └── errors.py                  # Custom exceptions
├── utils/
│   ├── __init__.py
│   └── logger.py                  # Logging setup
├── tests/
│   ├── __init__.py
│   ├── test_rpc_client.py
│   ├── test_cache_layer.py
│   └── test_bitcoin_service.py
└── Dockerfile

### Frontend Project Tree
```
snapshot-inteligente-frontend/
├── src/
│   ├── app/
│   │   ├── components/
│   │   │   ├── dashboard.component.ts
│   │   │   ├── dashboard.component.html
│   │   │   ├── dashboard.component.scss
│   │   │   ├── mempool-card.component.ts
│   │   │   ├── mempool-card.component.html
│   │   │   ├── mempool-card.component.scss
│   │   │   ├── blockchain-card.component.ts
│   │   │   ├── blockchain-card.component.html
│   │   │   └── blockchain-card.component.scss
│   │   ├── services/
│   │   │   ├── bitcoin-api.service.ts
│   │   │   ├── bitcoin-api.service.spec.ts
│   │   │   └── auto-refresh.service.ts
│   │   ├── models/
│   │   │   ├── mempool.model.ts
│   │   │   └── blockchain.model.ts
│   │   ├── app.module.ts
│   │   └── app.component.html
│   └── environments/
│       ├── environment.ts
│       └── environment.prod.ts
├── angular.json
├── tsconfig.json
├── tailwind.config.js
├── package.json
└── Dockerfile

---

## **BACKEND IMPLEMENTATION TASKS**

### Task 1: Project Setup & Dependencies

**Files:**
- Create: `snapshot-inteligente-backend/requirements.txt`
- Create: `snapshot-inteligente-backend/.env.example`
- Create: `snapshot-inteligente-backend/config.py`
- Create: `snapshot-inteligente-backend/.gitignore`

- [ ] **Step 1: Create requirements.txt**

Create file `snapshot-inteligente-backend/requirements.txt`:
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0
requests==2.31.0
python-dotenv==1.0.0
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
```

- [ ] **Step 2: Create .env.example**

Create file `snapshot-inteligente-backend/.env.example`:
```
# Bitcoin RPC Configuration
BITCOIN_RPC_HOST=localhost
BITCOIN_RPC_PORT=8332
BITCOIN_RPC_USER=bitcoin
BITCOIN_RPC_PASSWORD=changeme
RPC_TIMEOUT_SECONDS=5

# Cache Configuration
CACHE_TTL_SECONDS=10

# Fee Thresholds (sat/vB)
FEE_LOW_THRESHOLD=10
FEE_HIGH_THRESHOLD=50

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_URL=http://localhost:4200

# Environment
DEBUG=true
```

- [ ] **Step 3: Create config.py**

Create file `snapshot-inteligente-backend/config.py`:
```python
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
    
    # Environment
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True

config = Config()
```

- [ ] **Step 4: Create .gitignore**

Create file `snapshot-inteligente-backend/.gitignore`:
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Environment
.env
.env.local

# Testing
.pytest_cache/
.coverage
htmlcov/

# OS
.DS_Store
Thumbs.db
```

- [ ] **Step 5: Verify setup**

Run:
```bash
cd snapshot-inteligente-backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Expected: All packages install successfully, no errors.

- [ ] **Step 6: Commit**

```bash
git add requirements.txt .env.example config.py .gitignore
git commit -m "chore: Add project setup and dependencies"
```

---

### Task 2: Custom Exceptions & Models

**Files:**
- Create: `snapshot-inteligente-backend/models/errors.py`
- Create: `snapshot-inteligente-backend/models/responses.py`

- [ ] **Step 1: Create errors.py with custom exceptions**

Create file `snapshot-inteligente-backend/models/errors.py`:
```python
class BitcoinServiceError(Exception):
    """Base exception for all Bitcoin service errors."""
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

- [ ] **Step 2: Create responses.py with Pydantic models**

Create file `snapshot-inteligente-backend/models/responses.py`:
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
```

- [ ] **Step 3: Create __init__.py in models**

Create file `snapshot-inteligente-backend/models/__init__.py`:
```python
from .errors import BitcoinServiceError, RPCConnectionError, RPCMethodError
from .responses import MempoolSummary, BlockchainLag, HealthStatus

__all__ = [
    "BitcoinServiceError",
    "RPCConnectionError", 
    "RPCMethodError",
    "MempoolSummary",
    "BlockchainLag",
    "HealthStatus",
]
```

- [ ] **Step 4: Commit**

```bash
git add models/errors.py models/responses.py models/__init__.py
git commit -m "feat: Add custom exceptions and Pydantic response models"
```

---

### Task 3: RPC Client Layer

**Files:**
- Create: `snapshot-inteligente-backend/layers/rpc_client.py`

- [ ] **Step 1: Create RPC client with connection handling**

Create file `snapshot-inteligente-backend/layers/rpc_client.py`:
```python
import requests
import json
from typing import Any, List, Optional, Dict
from config import config
from models.errors import RPCConnectionError, RPCMethodError
import logging

logger = logging.getLogger(__name__)

class RPCClient:
    """
    Bitcoin Core RPC client.
    Handles connection, serialization, and error handling.
    """
    
    def __init__(
        self,
        host: str = None,
        port: int = None,
        user: str = None,
        password: str = None,
        timeout: int = None
    ):
        self.host = host or config.BITCOIN_RPC_HOST
        self.port = port or config.BITCOIN_RPC_PORT
        self.user = user or config.BITCOIN_RPC_USER
        self.password = password or config.BITCOIN_RPC_PASSWORD
        self.timeout = timeout or config.RPC_TIMEOUT_SECONDS
        self.url = f"http://{self.host}:{self.port}"
        self.auth = (self.user, self.password)
        self._session = requests.Session()
        self._session.auth = self.auth
    
    def call(self, method: str, params: List[Any] = None) -> dict:
        """
        Execute a Bitcoin RPC call.
        
        Args:
            method: RPC method name (e.g., 'getmempoolinfo')
            params: List of parameters or None
            
        Returns:
            Response data from Bitcoin Core
            
        Raises:
            RPCConnectionError: Network/connection issues
            RPCMethodError: RPC returns error response
        """
        if params is None:
            params = []
        
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1,
        }
        
        try:
            logger.debug(f"RPC call: {method} with params: {params}")
            response = self._session.post(
                self.url,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
        except requests.exceptions.ConnectionError as e:
            logger.error(f"RPC Connection failed: {e}")
            raise RPCConnectionError(f"Cannot connect to {self.url}: {str(e)}")
        except requests.exceptions.Timeout as e:
            logger.error(f"RPC Timeout: {e}")
            raise RPCConnectionError(f"RPC call timed out after {self.timeout}s")
        except requests.exceptions.RequestException as e:
            logger.error(f"RPC Request failed: {e}")
            raise RPCConnectionError(f"Request failed: {str(e)}")
        
        try:
            result = response.json()
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse RPC response: {e}")
            raise RPCConnectionError(f"Invalid JSON response: {str(e)}")
        
        # Check for JSON-RPC error
        if "error" in result and result["error"] is not None:
            error = result["error"]
            error_code = error.get("code", -1)
            error_msg = error.get("message", "Unknown error")
            logger.error(f"RPC error for {method}: [{error_code}] {error_msg}")
            raise RPCMethodError(method, error_code, error_msg)
        
        if "result" not in result:
            logger.error(f"Invalid RPC response format: {result}")
            raise RPCConnectionError("Invalid RPC response format")
        
        logger.debug(f"RPC response for {method}: success")
        return result["result"]
    
    def close(self):
        """Close the RPC session."""
        self._session.close()
```

- [ ] **Step 2: Create __init__.py in layers**

Create file `snapshot-inteligente-backend/layers/__init__.py`:
```python
from .rpc_client import RPCClient

__all__ = ["RPCClient"]
```

- [ ] **Step 3: Write test for RPC client**

Create file `snapshot-inteligente-backend/tests/test_rpc_client.py`:
```python
import pytest
from unittest.mock import patch, MagicMock
from layers.rpc_client import RPCClient
from models.errors import RPCConnectionError, RPCMethodError

@pytest.fixture
def rpc_client():
    return RPCClient(
        host="localhost",
        port=8332,
        user="test",
        password="test",
        timeout=5
    )

def test_rpc_client_init(rpc_client):
    assert rpc_client.host == "localhost"
    assert rpc_client.port == 8332
    assert rpc_client.user == "test"
    assert rpc_client.password == "test"
    assert rpc_client.timeout == 5
    assert rpc_client.url == "http://localhost:8332"

@patch('requests.Session.post')
def test_rpc_call_success(mock_post, rpc_client):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "jsonrpc": "2.0",
        "result": {"blocks": 100},
        "id": 1
    }
    mock_post.return_value = mock_response
    
    result = rpc_client.call('getblockchaininfo')
    assert result == {"blocks": 100}
    mock_post.assert_called_once()

@patch('requests.Session.post')
def test_rpc_call_with_params(mock_post, rpc_client):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "jsonrpc": "2.0",
        "result": "abc123",
        "id": 1
    }
    mock_post.return_value = mock_response
    
    result = rpc_client.call('getblockhash', [0])
    assert result == "abc123"
    call_args = mock_post.call_args
    assert call_args[1]['json']['params'] == [0]

@patch('requests.Session.post')
def test_rpc_call_connection_error(mock_post, rpc_client):
    import requests
    mock_post.side_effect = requests.exceptions.ConnectionError("Connection refused")
    
    with pytest.raises(RPCConnectionError):
        rpc_client.call('getblockchaininfo')

@patch('requests.Session.post')
def test_rpc_call_timeout(mock_post, rpc_client):
    import requests
    mock_post.side_effect = requests.exceptions.Timeout("Request timed out")
    
    with pytest.raises(RPCConnectionError):
        rpc_client.call('getblockchaininfo')

@patch('requests.Session.post')
def test_rpc_call_rpc_error(mock_post, rpc_client):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "jsonrpc": "2.0",
        "error": {"code": -32601, "message": "Method not found"},
        "id": 1
    }
    mock_post.return_value = mock_response
    
    with pytest.raises(RPCMethodError) as exc_info:
        rpc_client.call('nonexistentmethod')
    
    assert exc_info.value.error_code == -32601
    assert "Method not found" in str(exc_info.value)
```

- [ ] **Step 4: Run tests to verify RPC client**

Run:
```bash
cd snapshot-inteligente-backend
source venv/bin/activate
pytest tests/test_rpc_client.py -v
```

Expected: All tests pass (8 passed).

- [ ] **Step 5: Commit**

```bash
git add layers/rpc_client.py layers/__init__.py tests/test_rpc_client.py
git commit -m "feat: Implement RPC client layer with connection handling"
```

---

### Task 4: Cache Layer Implementation

**Files:**
- Create: `snapshot-inteligente-backend/layers/cache_layer.py`

- [ ] **Step 1: Create cache layer with TTL support**

Create file `snapshot-inteligente-backend/layers/cache_layer.py`:
```python
import time
import hashlib
import json
from typing import Any, Callable, Dict, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Represents a cached value with expiration time."""
    data: Any
    expiry_time: float

class CacheLayer:
    """
    In-memory cache with TTL support.
    Provides decorator for caching method responses.
    """
    
    def __init__(self):
        self.cache: Dict[str, CacheEntry] = {}
        self.hits: int = 0
        self.misses: int = 0
    
    def cached(self, ttl_seconds: int = 10):
        """
        Decorator factory for caching method responses.
        
        Usage:
            cache = CacheLayer()
            
            @cache.cached(ttl_seconds=10)
            def expensive_method(self, param1):
                return compute_something()
        
        Args:
            ttl_seconds: Time-to-live in seconds
        """
        def decorator(func: Callable) -> Callable:
            def wrapper(*args, **kwargs) -> Any:
                # Generate cache key
                cache_key = self._make_key(func.__name__, args, kwargs)
                
                # Check if cache hit and not expired
                if cache_key in self.cache:
                    entry = self.cache[cache_key]
                    if time.time() < entry.expiry_time:
                        self.hits += 1
                        logger.debug(f"Cache hit for {func.__name__}")
                        return entry.data
                    else:
                        # Expired, remove from cache
                        del self.cache[cache_key]
                        logger.debug(f"Cache expired for {func.__name__}")
                
                # Cache miss
                self.misses += 1
                logger.debug(f"Cache miss for {func.__name__}")
                result = func(*args, **kwargs)
                
                # Store in cache with TTL
                expiry_time = time.time() + ttl_seconds
                self.cache[cache_key] = CacheEntry(data=result, expiry_time=expiry_time)
                
                return result
            
            return wrapper
        
        return decorator
    
    def _make_key(self, func_name: str, args: Tuple, kwargs: Dict) -> str:
        """
        Generate unique cache key from function name and parameters.
        
        Args:
            func_name: Function name
            args: Function args
            kwargs: Function kwargs
            
        Returns:
            Unique cache key string
        """
        # Ignore 'self' parameter (first arg in methods)
        args_to_hash = args[1:] if args and hasattr(args[0], '__dict__') else args
        
        # Convert to JSON-serializable format
        try:
            key_data = json.dumps({
                "func": func_name,
                "args": args_to_hash,
                "kwargs": kwargs
            }, sort_keys=True, default=str)
        except TypeError:
            # Fallback for non-serializable objects
            key_data = f"{func_name}_{str(args)}_{str(kwargs)}"
        
        # Create hash for shorter key
        hash_obj = hashlib.md5(key_data.encode())
        return hash_obj.hexdigest()
    
    def get_stats(self) -> Dict[str, any]:
        """
        Return cache statistics.
        
        Returns:
            Dict with hits, misses, hit_rate
        """
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        
        return {
            "hits": self.hits,
            "misses": self.misses,
            "total": total,
            "hit_rate_percent": round(hit_rate, 2),
            "cached_items": len(self.cache)
        }
    
    def clear(self):
        """Clear all cached data."""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def close(self):
        """Close cache (cleanup)."""
        self.clear()

# Global cache instance
cache_layer = CacheLayer()
```

- [ ] **Step 2: Write tests for cache layer**

Create file `snapshot-inteligente-backend/tests/test_cache_layer.py`:
```python
import pytest
import time
from layers.cache_layer import CacheLayer

class TestCacheLayer:
    @pytest.fixture
    def cache(self):
        return CacheLayer()
    
    def test_cache_hit(self, cache):
        call_count = 0
        
        @cache.cached(ttl_seconds=10)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # First call - cache miss
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count == 1
        
        # Second call - cache hit
        result2 = expensive_function(5)
        assert result2 == 10
        assert call_count == 1  # Function not called again
    
    def test_cache_miss_different_params(self, cache):
        call_count = 0
        
        @cache.cached(ttl_seconds=10)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        result1 = expensive_function(5)
        result2 = expensive_function(10)
        
        assert result1 == 10
        assert result2 == 20
        assert call_count == 2  # Function called twice (different params)
    
    def test_cache_expiration(self, cache):
        call_count = 0
        
        @cache.cached(ttl_seconds=1)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # First call
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count == 1
        
        # Immediate second call - cache hit
        result2 = expensive_function(5)
        assert call_count == 1
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Third call - cache expired, function called again
        result3 = expensive_function(5)
        assert call_count == 2
    
    def test_cache_stats(self, cache):
        @cache.cached(ttl_seconds=10)
        def test_func(x):
            return x + 1
        
        test_func(1)  # miss
        test_func(1)  # hit
        test_func(1)  # hit
        test_func(2)  # miss
        
        stats = cache.get_stats()
        assert stats['hits'] == 2
        assert stats['misses'] == 2
        assert stats['total'] == 4
        assert stats['hit_rate_percent'] == 50.0
    
    def test_cache_clear(self, cache):
        @cache.cached(ttl_seconds=10)
        def test_func(x):
            return x + 1
        
        test_func(1)
        assert len(cache.cache) > 0
        
        cache.clear()
        assert len(cache.cache) == 0
```

- [ ] **Step 3: Run cache layer tests**

Run:
```bash
pytest tests/test_cache_layer.py -v
```

Expected: All tests pass (6 passed).

- [ ] **Step 4: Commit**

```bash
git add layers/cache_layer.py tests/test_cache_layer.py
git commit -m "feat: Implement cache layer with TTL and decorator pattern"
```

---

### Task 5: Bitcoin Service - Business Logic

**Files:**
- Create: `snapshot-inteligente-backend/layers/bitcoin_service.py`

- [ ] **Step 1: Create Bitcoin service with mempool and blockchain logic**

Create file `snapshot-inteligente-backend/layers/bitcoin_service.py`:
```python
from datetime import datetime
from typing import List, Dict
from layers.rpc_client import RPCClient
from layers.cache_layer import CacheLayer
from models.responses import MempoolSummary, BlockchainLag
from models.errors import RPCConnectionError, RPCMethodError
from config import config
import logging

logger = logging.getLogger(__name__)

class BitcoinService:
    """
    Bitcoin data interpretation service.
    Analyzes raw RPC data and provides high-level metrics.
    """
    
    def __init__(self, rpc_client: RPCClient, cache_layer: CacheLayer):
        self.rpc = rpc_client
        self.cache = cache_layer
    
    @property
    def fee_low_threshold(self) -> float:
        """Low fee threshold in sat/vB."""
        return config.FEE_LOW_THRESHOLD
    
    @property
    def fee_high_threshold(self) -> float:
        """High fee threshold in sat/vB."""
        return config.FEE_HIGH_THRESHOLD
    
    def _classify_fee(self, fee_rate: float) -> str:
        """
        Classify transaction fee into low/medium/high category.
        
        Args:
            fee_rate: Fee rate in sat/vB
            
        Returns:
            Category: 'low', 'medium', or 'high'
        """
        if fee_rate < self.fee_low_threshold:
            return 'low'
        elif fee_rate <= self.fee_high_threshold:
            return 'medium'
        else:
            return 'high'
    
    def get_mempool_summary(self) -> MempoolSummary:
        """
        Analyze mempool and return fee distribution summary.
        
        Flow:
        1. Fetch getmempoolinfo → basic stats
        2. Fetch getrawmempool(true) → detailed TX info with fees
        3. Extract fee rates from each transaction
        4. Calculate statistics (avg, min, max)
        5. Classify transactions into buckets
        
        Returns:
            MempoolSummary with tx counts, fee stats, and distribution
            
        Raises:
            RPCConnectionError: RPC connection failed
            RPCMethodError: RPC call returned error
        """
        try:
            logger.info("Fetching mempool summary")
            
            # Fetch basic mempool info
            mempool_info = self.rpc.call('getmempoolinfo')
            
            # Fetch detailed mempool with verbose=true
            raw_mempool = self.rpc.call('getrawmempool', [True])
            
            # Extract fee rates from all transactions
            fee_rates: List[float] = []
            for txid, tx_data in raw_mempool.items():
                # Fee is in BTC, vsize is in vB
                # Convert fee rate to sat/vB: (fee_btc * 100_000_000 sat/BTC) / vsize
                if 'fees' in tx_data and 'vsize' in tx_data:
                    fee_btc = tx_data['fees'].get('base', 0)
                    vsize = tx_data.get('vsize', 1)
                    if vsize > 0:
                        fee_rate = (fee_btc * 100_000_000) / vsize
                        fee_rates.append(fee_rate)
            
            # Calculate statistics
            if fee_rates:
                avg_fee = sum(fee_rates) / len(fee_rates)
                min_fee = min(fee_rates)
                max_fee = max(fee_rates)
            else:
                avg_fee = min_fee = max_fee = 0.0
            
            # Classify transactions into buckets
            distribution: Dict[str, int] = {'low': 0, 'medium': 0, 'high': 0}
            for fee_rate in fee_rates:
                category = self._classify_fee(fee_rate)
                distribution[category] += 1
            
            # Get total vsize from mempool info
            total_vsize = mempool_info.get('total_vsize', 0)
            
            result = MempoolSummary(
                tx_count=len(raw_mempool),
                total_vsize=total_vsize,
                avg_fee_rate=round(avg_fee, 2),
                min_fee_rate=round(min_fee, 2),
                max_fee_rate=round(max_fee, 2),
                fee_distribution=distribution,
                timestamp=datetime.utcnow().isoformat()
            )
            
            logger.info(f"Mempool summary: {result.tx_count} txs, avg fee {result.avg_fee_rate} sat/vB")
            return result
            
        except (RPCConnectionError, RPCMethodError) as e:
            logger.error(f"Error fetching mempool summary: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in mempool summary: {e}")
            raise
    
    def get_blockchain_lag(self) -> BlockchainLag:
        """
        Compare blockchain synchronization status.
        
        Flow:
        1. Fetch getblockchaininfo
        2. Extract blocks and headers counts
        3. Calculate lag (headers - blocks)
        
        Returns:
            BlockchainLag with block counts and lag
            
        Raises:
            RPCConnectionError: RPC connection failed
            RPCMethodError: RPC call returned error
        """
        try:
            logger.info("Fetching blockchain lag")
            
            blockchain_info = self.rpc.call('getblockchaininfo')
            
            blocks = blockchain_info.get('blocks', 0)
            headers = blockchain_info.get('headers', 0)
            lag = headers - blocks
            
            result = BlockchainLag(
                blocks=blocks,
                headers=headers,
                lag=lag,
                timestamp=datetime.utcnow().isoformat()
            )
            
            logger.info(f"Blockchain lag: {lag} blocks behind headers")
            return result
            
        except (RPCConnectionError, RPCMethodError) as e:
            logger.error(f"Error fetching blockchain lag: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in blockchain lag: {e}")
            raise
```

- [ ] **Step 2: Write tests for Bitcoin service**

Create file `snapshot-inteligente-backend/tests/test_bitcoin_service.py`:
```python
import pytest
from unittest.mock import MagicMock, patch
from layers.bitcoin_service import BitcoinService
from layers.rpc_client import RPCClient
from layers.cache_layer import CacheLayer
from models.responses import MempoolSummary, BlockchainLag
from models.errors import RPCConnectionError, RPCMethodError

@pytest.fixture
def mock_rpc():
    return MagicMock(spec=RPCClient)

@pytest.fixture
def cache():
    return CacheLayer()

@pytest.fixture
def service(mock_rpc, cache):
    return BitcoinService(mock_rpc, cache)

def test_classify_fee_low(service):
    assert service._classify_fee(5.0) == 'low'
    assert service._classify_fee(9.9) == 'low'

def test_classify_fee_medium(service):
    assert service._classify_fee(10.0) == 'medium'
    assert service._classify_fee(25.0) == 'medium'
    assert service._classify_fee(50.0) == 'medium'

def test_classify_fee_high(service):
    assert service._classify_fee(50.1) == 'high'
    assert service._classify_fee(100.0) == 'high'

def test_get_mempool_summary_success(mock_rpc, service):
    # Mock RPC responses
    mock_rpc.call.side_effect = [
        # getmempoolinfo response
        {
            'size': 3,
            'bytes': 1000,
            'total_vsize': 900,
            'usage': 50000,
        },
        # getrawmempool(true) response
        {
            'tx1': {
                'fees': {'base': 0.0001},
                'vsize': 200
            },
            'tx2': {
                'fees': {'base': 0.0005},
                'vsize': 300
            },
            'tx3': {
                'fees': {'base': 0.003},
                'vsize': 400
            }
        }
    ]
    
    result = service.get_mempool_summary()
    
    assert isinstance(result, MempoolSummary)
    assert result.tx_count == 3
    assert result.total_vsize == 900
    assert result.fee_distribution['low'] >= 0
    assert result.fee_distribution['medium'] >= 0
    assert result.fee_distribution['high'] >= 0
    assert result.timestamp is not None

def test_get_mempool_summary_empty(mock_rpc, service):
    mock_rpc.call.side_effect = [
        {'size': 0, 'bytes': 0, 'total_vsize': 0},
        {}  # Empty mempool
    ]
    
    result = service.get_mempool_summary()
    
    assert result.tx_count == 0
    assert result.avg_fee_rate == 0.0
    assert result.fee_distribution == {'low': 0, 'medium': 0, 'high': 0}

def test_get_blockchain_lag_synced(mock_rpc, service):
    mock_rpc.call.return_value = {
        'blocks': 100000,
        'headers': 100000,
        'difficulty': 1234567.89,
    }
    
    result = service.get_blockchain_lag()
    
    assert isinstance(result, BlockchainLag)
    assert result.blocks == 100000
    assert result.headers == 100000
    assert result.lag == 0

def test_get_blockchain_lag_lagging(mock_rpc, service):
    mock_rpc.call.return_value = {
        'blocks': 100000,
        'headers': 100050,
        'difficulty': 1234567.89,
    }
    
    result = service.get_blockchain_lag()
    
    assert result.blocks == 100000
    assert result.headers == 100050
    assert result.lag == 50

def test_get_mempool_summary_rpc_error(mock_rpc, service):
    mock_rpc.call.side_effect = RPCConnectionError("Connection failed")
    
    with pytest.raises(RPCConnectionError):
        service.get_mempool_summary()

def test_get_blockchain_lag_rpc_error(mock_rpc, service):
    mock_rpc.call.side_effect = RPCMethodError("getblockchaininfo", -32600, "Invalid request")
    
    with pytest.raises(RPCMethodError):
        service.get_blockchain_lag()
```

- [ ] **Step 3: Run Bitcoin service tests**

Run:
```bash
pytest tests/test_bitcoin_service.py -v
```

Expected: All tests pass (12 passed).

- [ ] **Step 4: Commit**

```bash
git add layers/bitcoin_service.py tests/test_bitcoin_service.py
git commit -m "feat: Implement Bitcoin service with mempool and blockchain analysis"
```

---

### Task 6: FastAPI Application & Health Endpoint

**Files:**
- Create: `snapshot-inteligente-backend/app.py`
- Create: `snapshot-inteligente-backend/routes/health.py`
- Create: `snapshot-inteligente-backend/routes/__init__.py`

- [ ] **Step 1: Create app.py with FastAPI initialization**

Create file `snapshot-inteligente-backend/app.py`:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import config
from layers.rpc_client import RPCClient
from layers.cache_layer import CacheLayer
from layers.bitcoin_service import BitcoinService
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Snapshot Inteligente",
    description="Bitcoin node state interpretation API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[config.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services (singletons)
rpc_client = RPCClient()
cache_layer = CacheLayer()
bitcoin_service = BitcoinService(rpc_client, cache_layer)

# Dependency injection functions
def get_rpc_client():
    return rpc_client

def get_cache_layer():
    return cache_layer

def get_bitcoin_service():
    return bitcoin_service

# Include routes
from routes.health import router as health_router
from routes.mempool import router as mempool_router
from routes.blockchain import router as blockchain_router

app.include_router(health_router)
app.include_router(mempool_router)
app.include_router(blockchain_router)

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on app shutdown."""
    rpc_client.close()
    cache_layer.close()
    logger.info("Application shutdown")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=config.API_HOST,
        port=config.API_PORT,
        workers=1
    )
```

- [ ] **Step 2: Create health.py route**

Create file `snapshot-inteligente-backend/routes/health.py`:
```python
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from models.responses import HealthStatus
from models.errors import RPCConnectionError
from layers.rpc_client import RPCClient
from app import get_rpc_client
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
```

- [ ] **Step 3: Create routes/__init__.py**

Create file `snapshot-inteligente-backend/routes/__init__.py`:
```python
# Routes package
```

- [ ] **Step 4: Test health endpoint manually**

Run (in one terminal):
```bash
cd snapshot-inteligente-backend
source venv/bin/activate
python app.py
```

Expected: Server starts on http://0.0.0.0:8000

Test (in another terminal):
```bash
curl http://localhost:8000/health
```

Expected output (when Bitcoin not running):
```json
{
  "detail": {
    "status": "error",
    "rpc": "disconnected",
    "message": "RPC Connection Error: Cannot connect to http://localhost:8332: ..."
  }
}
```

- [ ] **Step 5: Stop server and commit**

```bash
# Stop the server (Ctrl+C in the running terminal)
git add app.py routes/health.py routes/__init__.py
git commit -m "feat: Add FastAPI application and health endpoint"
```

---

### Task 7: Mempool & Blockchain Routes

**Files:**
- Create: `snapshot-inteligente-backend/routes/mempool.py`
- Create: `snapshot-inteligente-backend/routes/blockchain.py`

- [ ] **Step 1: Create mempool.py route**

Create file `snapshot-inteligente-backend/routes/mempool.py`:
```python
from fastapi import APIRouter, Depends, HTTPException
from models.responses import MempoolSummary
from models.errors import RPCConnectionError, RPCMethodError
from layers.bitcoin_service import BitcoinService
from app import get_bitcoin_service
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
```

- [ ] **Step 2: Create blockchain.py route**

Create file `snapshot-inteligente-backend/routes/blockchain.py`:
```python
from fastapi import APIRouter, Depends, HTTPException
from models.responses import BlockchainLag
from models.errors import RPCConnectionError, RPCMethodError
from layers.bitcoin_service import BitcoinService
from app import get_bitcoin_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/blockchain", tags=["blockchain"])

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
```

- [ ] **Step 3: Update app.py to fix circular import**

The app.py file has circular imports. Let me create a better structure:

Create file `snapshot-inteligente-backend/dependencies.py`:
```python
from layers.rpc_client import RPCClient
from layers.cache_layer import CacheLayer
from layers.bitcoin_service import BitcoinService

# Initialize services (singletons)
rpc_client = RPCClient()
cache_layer = CacheLayer()
bitcoin_service = BitcoinService(rpc_client, cache_layer)

# Dependency injection functions
def get_rpc_client():
    return rpc_client

def get_cache_layer():
    return cache_layer

def get_bitcoin_service():
    return bitcoin_service
```

Update app.py:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import config
from dependencies import rpc_client, cache_layer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Snapshot Inteligente",
    description="Bitcoin node state interpretation API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[config.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
from routes.health import router as health_router
from routes.mempool import router as mempool_router
from routes.blockchain import router as blockchain_router

app.include_router(health_router)
app.include_router(mempool_router)
app.include_router(blockchain_router)

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on app shutdown."""
    rpc_client.close()
    cache_layer.close()
    logger.info("Application shutdown")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=config.API_HOST,
        port=config.API_PORT,
        workers=1
    )
```

Update routes/health.py, routes/mempool.py, routes/blockchain.py to use:
```python
from dependencies import get_rpc_client, get_bitcoin_service, get_cache_layer
```

- [ ] **Step 4: Commit**

```bash
git add routes/mempool.py routes/blockchain.py dependencies.py
git commit -m "feat: Add mempool and blockchain API routes"
```

---

## **FRONTEND IMPLEMENTATION TASKS**

### Task 8: Frontend Project Setup

**Files:**
- Create: `snapshot-inteligente-frontend/angular.json`
- Create: `snapshot-inteligente-frontend/package.json`
- Create: `snapshot-inteligente-frontend/tsconfig.json`

- [ ] **Step 1: Create Angular project structure**

Run:
```bash
ng new snapshot-inteligente-frontend --routing --style=scss --package-manager=npm
cd snapshot-inteligente-frontend
```

Or manually create files. First, create `package.json`:
```json
{
  "name": "snapshot-inteligente-frontend",
  "version": "1.0.0",
  "scripts": {
    "ng": "ng",
    "start": "ng serve",
    "build": "ng build",
    "watch": "ng build --watch --configuration development",
    "test": "ng test"
  },
  "private": true,
  "dependencies": {
    "@angular/animations": "^17.0.0",
    "@angular/common": "^17.0.0",
    "@angular/compiler": "^17.0.0",
    "@angular/core": "^17.0.0",
    "@angular/forms": "^17.0.0",
    "@angular/material": "^17.0.0",
    "@angular/platform-browser": "^17.0.0",
    "@angular/platform-browser-dynamic": "^17.0.0",
    "@angular/router": "^17.0.0",
    "rxjs": "^7.8.0",
    "tslib": "^2.6.0",
    "zone.js": "^0.14.0",
    "chart.js": "^4.4.0",
    "ng2-charts": "^4.1.0"
  },
  "devDependencies": {
    "@angular-devkit/build-angular": "^17.0.0",
    "@angular/cli": "^17.0.0",
    "@angular/compiler-cli": "^17.0.0",
    "@types/jasmine": "~5.1.0",
    "jasmine-core": "~5.1.0",
    "karma": "~6.4.0",
    "karma-chrome-launcher": "~3.2.0",
    "karma-coverage": "~2.2.0",
    "karma-jasmine": "~5.1.0",
    "karma-jasmine-html-reporter": "~2.1.0",
    "typescript": "~5.2.0",
    "tailwindcss": "^3.3.0",
    "postcss": "^8.4.0",
    "autoprefixer": "^10.4.0"
  }
}
```

- [ ] **Step 2: Install dependencies**

Run:
```bash
npm install
```

- [ ] **Step 3: Set up Tailwind CSS**

Create `tailwind.config.js`:
```javascript
module.exports = {
  content: [
    "./src/**/*.{html,ts}"
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

Create `postcss.config.js`:
```javascript
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

Update `src/styles.scss`:
```scss
@tailwind base;
@tailwind components;
@tailwind utilities;
```

- [ ] **Step 4: Commit**

```bash
git add package.json tsconfig.json angular.json tailwind.config.js postcss.config.js
git commit -m "chore: Initialize Angular frontend project with Tailwind"
```

---

### Task 9: Frontend Models & Services

**Files:**
- Create: `snapshot-inteligente-frontend/src/app/models/mempool.model.ts`
- Create: `snapshot-inteligente-frontend/src/app/models/blockchain.model.ts`
- Create: `snapshot-inteligente-frontend/src/app/services/bitcoin-api.service.ts`

- [ ] **Step 1: Create mempool model**

Create file `snapshot-inteligente-frontend/src/app/models/mempool.model.ts`:
```typescript
export interface FeeDistribution {
  low: number;
  medium: number;
  high: number;
}

export interface MempoolSummary {
  tx_count: number;
  total_vsize: number;
  avg_fee_rate: number;
  min_fee_rate: number;
  max_fee_rate: number;
  fee_distribution: FeeDistribution;
  timestamp: string;
}
```

- [ ] **Step 2: Create blockchain model**

Create file `snapshot-inteligente-frontend/src/app/models/blockchain.model.ts`:
```typescript
export interface BlockchainLag {
  blocks: number;
  headers: number;
  lag: number;
  timestamp: string;
}
```

- [ ] **Step 3: Create Bitcoin API service**

Create file `snapshot-inteligente-frontend/src/app/services/bitcoin-api.service.ts`:
```typescript
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../environments/environment';
import { MempoolSummary } from '../models/mempool.model';
import { BlockchainLag } from '../models/blockchain.model';

@Injectable({
  providedIn: 'root'
})
export class BitcoinApiService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getMempoolSummary(): Observable<MempoolSummary> {
    return this.http.get<MempoolSummary>(`${this.apiUrl}/mempool/summary`);
  }

  getBlockchainLag(): Observable<BlockchainLag> {
    return this.http.get<BlockchainLag>(`${this.apiUrl}/blockchain/lag`);
  }

  getHealth(): Observable<any> {
    return this.http.get(`${this.apiUrl}/health`);
  }
}
```

- [ ] **Step 4: Create test for service**

Create file `snapshot-inteligente-frontend/src/app/services/bitcoin-api.service.spec.ts`:
```typescript
import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { BitcoinApiService } from './bitcoin-api.service';
import { MempoolSummary } from '../models/mempool.model';
import { BlockchainLag } from '../models/blockchain.model';

describe('BitcoinApiService', () => {
  let service: BitcoinApiService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [BitcoinApiService]
    });
    service = TestBed.inject(BitcoinApiService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should fetch mempool summary', () => {
    const mockData: MempoolSummary = {
      tx_count: 1000,
      total_vsize: 50000,
      avg_fee_rate: 25.5,
      min_fee_rate: 1.0,
      max_fee_rate: 100.0,
      fee_distribution: { low: 500, medium: 400, high: 100 },
      timestamp: '2026-05-01T12:00:00'
    };

    service.getMempoolSummary().subscribe(data => {
      expect(data.tx_count).toBe(1000);
      expect(data.avg_fee_rate).toBe(25.5);
    });

    const req = httpMock.expectOne(request => request.url.includes('/mempool/summary'));
    expect(req.request.method).toBe('GET');
    req.flush(mockData);
  });

  it('should fetch blockchain lag', () => {
    const mockData: BlockchainLag = {
      blocks: 100000,
      headers: 100050,
      lag: 50,
      timestamp: '2026-05-01T12:00:00'
    };

    service.getBlockchainLag().subscribe(data => {
      expect(data.lag).toBe(50);
    });

    const req = httpMock.expectOne(request => request.url.includes('/blockchain/lag'));
    expect(req.request.method).toBe('GET');
    req.flush(mockData);
  });
});
```

- [ ] **Step 5: Commit**

```bash
git add src/app/models/ src/app/services/
git commit -m "feat: Add Bitcoin API service and data models"
```

---

### Task 10: Frontend Components - Dashboard

**Files:**
- Create: `snapshot-inteligente-frontend/src/app/components/dashboard.component.ts`
- Create: `snapshot-inteligente-frontend/src/app/components/dashboard.component.html`
- Create: `snapshot-inteligente-frontend/src/app/components/dashboard.component.scss`

- [ ] **Step 1: Create dashboard component**

Generate component:
```bash
ng generate component components/dashboard --skip-tests
```

Or create manually. Update `dashboard.component.ts`:
```typescript
import { Component, OnInit, OnDestroy } from '@angular/core';
import { BitcoinApiService } from '../services/bitcoin-api.service';
import { MempoolSummary } from '../models/mempool.model';
import { BlockchainLag } from '../models/blockchain.model';
import { Subject, interval, takeUntil, switchMap } from 'rxjs';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit, OnDestroy {
  mempool: MempoolSummary | null = null;
  blockchain: BlockchainLag | null = null;
  loading = true;
  error: string | null = null;
  isConnected = false;
  lastUpdated: Date | null = null;

  private destroy$ = new Subject<void>();

  constructor(private bitcoinApi: BitcoinApiService) {}

  ngOnInit(): void {
    this.loadData();
    this.startAutoRefresh();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  loadData(): void {
    this.loading = true;
    this.error = null;

    this.bitcoinApi.getHealth().subscribe({
      next: () => {
        this.isConnected = true;
        this.fetchMempoolAndBlockchain();
      },
      error: (err) => {
        this.isConnected = false;
        this.error = 'Unable to connect to Bitcoin backend';
        this.loading = false;
      }
    });
  }

  private fetchMempoolAndBlockchain(): void {
    Promise.all([
      new Promise<void>((resolve, reject) => {
        this.bitcoinApi.getMempoolSummary().subscribe({
          next: (data) => {
            this.mempool = data;
            this.lastUpdated = new Date();
            resolve();
          },
          error: (err) => {
            this.error = 'Failed to fetch mempool data';
            reject(err);
          }
        });
      }),
      new Promise<void>((resolve, reject) => {
        this.bitcoinApi.getBlockchainLag().subscribe({
          next: (data) => {
            this.blockchain = data;
            resolve();
          },
          error: (err) => {
            this.error = 'Failed to fetch blockchain data';
            reject(err);
          }
        });
      })
    ]).finally(() => {
      this.loading = false;
    });
  }

  private startAutoRefresh(): void {
    interval(15000)
      .pipe(
        switchMap(() => {
          this.loadData();
          return [];
        }),
        takeUntil(this.destroy$)
      )
      .subscribe();
  }

  getRelativeTime(date: Date | null): string {
    if (!date) return '';
    const seconds = Math.floor((Date.now() - date.getTime()) / 1000);
    if (seconds < 60) return 'just now';
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    return `${Math.floor(minutes / 60)} hour${Math.floor(minutes / 60) > 1 ? 's' : ''} ago`;
  }
}
```

- [ ] **Step 2: Create dashboard template**

Update `dashboard.component.html`:
```html
<div class="min-h-screen bg-gray-50 p-6">
  <!-- Header -->
  <div class="max-w-7xl mx-auto mb-8">
    <div class="flex justify-between items-center mb-2">
      <h1 class="text-4xl font-bold text-gray-900">Bitcoin Node Status</h1>
      <div class="flex items-center gap-4">
        <div class="flex items-center gap-2">
          <div [class.bg-green-500]="isConnected" [class.bg-red-500]="!isConnected" class="w-3 h-3 rounded-full"></div>
          <span class="text-sm font-medium" [class.text-green-700]="isConnected" [class.text-red-700]="!isConnected">
            {{ isConnected ? 'Connected' : 'Disconnected' }}
          </span>
        </div>
        <button (click)="loadData()" class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition">
          Refresh
        </button>
      </div>
    </div>
    <p class="text-gray-600">
      Last updated: {{ lastUpdated ? getRelativeTime(lastUpdated) : 'Never' }}
    </p>
  </div>

  <!-- Error Message -->
  <div *ngIf="error" class="max-w-7xl mx-auto mb-8 p-4 bg-red-100 border border-red-400 text-red-700 rounded-md">
    {{ error }}
  </div>

  <!-- Loading State -->
  <div *ngIf="loading" class="max-w-7xl mx-auto">
    <div class="text-center py-12">
      <div class="inline-block">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
      <p class="mt-4 text-gray-600">Loading Bitcoin data...</p>
    </div>
  </div>

  <!-- Cards Grid -->
  <div *ngIf="!loading" class="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-6">
    <!-- Mempool Card -->
    <app-mempool-card [data]="mempool"></app-mempool-card>
    
    <!-- Blockchain Card -->
    <app-blockchain-card [data]="blockchain"></app-blockchain-card>
  </div>
</div>
```

- [ ] **Step 3: Create dashboard styling**

Create `dashboard.component.scss`:
```scss
// Dashboard specific styles (mostly handled by Tailwind)
```

- [ ] **Step 4: Commit**

```bash
git add src/app/components/dashboard.*
git commit -m "feat: Add dashboard component with auto-refresh"
```

---

### Task 11: Frontend Components - Mempool Card

**Files:**
- Create: `snapshot-inteligente-frontend/src/app/components/mempool-card.component.ts`
- Create: `snapshot-inteligente-frontend/src/app/components/mempool-card.component.html`
- Create: `snapshot-inteligente-frontend/src/app/components/mempool-card.component.scss`

- [ ] **Step 1: Create mempool card component**

Generate:
```bash
ng generate component components/mempool-card --skip-tests
```

Update `mempool-card.component.ts`:
```typescript
import { Component, Input, OnInit } from '@angular/core';
import { MempoolSummary } from '../models/mempool.model';
import { ChartConfiguration } from 'chart.js';

@Component({
  selector: 'app-mempool-card',
  templateUrl: './mempool-card.component.html',
  styleUrls: ['./mempool-card.component.scss']
})
export class MempoolCardComponent implements OnInit {
  @Input() data: MempoolSummary | null = null;

  feeChartOptions: ChartConfiguration['options'] = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        position: 'bottom'
      }
    }
  };

  feeChartData: any = {};

  ngOnInit(): void {
    if (this.data) {
      this.updateChart();
    }
  }

  ngOnChanges(): void {
    if (this.data) {
      this.updateChart();
    }
  }

  private updateChart(): void {
    if (!this.data) return;

    const total = this.data.fee_distribution.low + this.data.fee_distribution.medium + this.data.fee_distribution.high;
    const percentages = {
      low: ((this.data.fee_distribution.low / total) * 100).toFixed(1),
      medium: ((this.data.fee_distribution.medium / total) * 100).toFixed(1),
      high: ((this.data.fee_distribution.high / total) * 100).toFixed(1)
    };

    this.feeChartData = {
      labels: [
        `Low (${percentages.low}%)`,
        `Medium (${percentages.medium}%)`,
        `High (${percentages.high}%)`
      ],
      datasets: [{
        data: [
          this.data.fee_distribution.low,
          this.data.fee_distribution.medium,
          this.data.fee_distribution.high
        ],
        backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
        borderColor: ['#059669', '#d97706', '#dc2626'],
        borderWidth: 1
      }]
    };
  }

  getDoughnutChartOptions(): ChartConfiguration['options'] {
    return {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          position: 'bottom'
        }
      }
    };
  }
}
```

- [ ] **Step 2: Create mempool card template**

Create `mempool-card.component.html`:
```html
<div class="bg-white rounded-lg shadow-md p-6">
  <h2 class="text-2xl font-bold text-gray-900 mb-6">Mempool Intelligence</h2>

  <div *ngIf="data" class="space-y-6">
    <!-- Stats Grid -->
    <div class="grid grid-cols-2 gap-4">
      <div class="bg-blue-50 p-4 rounded-md">
        <p class="text-sm text-gray-600 font-medium">Total Transactions</p>
        <p class="text-2xl font-bold text-blue-600">{{ data.tx_count | number }}</p>
      </div>
      <div class="bg-purple-50 p-4 rounded-md">
        <p class="text-sm text-gray-600 font-medium">Total Size (vB)</p>
        <p class="text-2xl font-bold text-purple-600">{{ data.total_vsize | number }}</p>
      </div>
    </div>

    <!-- Fee Rates -->
    <div class="bg-gray-50 p-4 rounded-md space-y-3">
      <p class="text-sm font-medium text-gray-700">Fee Rates (sat/vB)</p>
      <div class="space-y-2">
        <div class="flex justify-between items-center">
          <span class="text-sm text-gray-600">Average:</span>
          <span class="font-semibold text-gray-900">{{ data.avg_fee_rate }} sat/vB</span>
        </div>
        <div class="flex justify-between items-center">
          <span class="text-sm text-gray-600">Min:</span>
          <span class="font-semibold text-green-600">{{ data.min_fee_rate }} sat/vB</span>
        </div>
        <div class="flex justify-between items-center">
          <span class="text-sm text-gray-600">Max:</span>
          <span class="font-semibold text-red-600">{{ data.max_fee_rate }} sat/vB</span>
        </div>
      </div>
    </div>

    <!-- Fee Distribution -->
    <div class="bg-gray-50 p-4 rounded-md">
      <p class="text-sm font-medium text-gray-700 mb-4">Fee Distribution</p>
      <div class="space-y-3">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <div class="w-3 h-3 bg-green-500 rounded-full"></div>
            <span class="text-sm text-gray-600">Low Fee</span>
          </div>
          <span class="font-semibold text-gray-900">{{ data.fee_distribution.low }}</span>
        </div>
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <div class="w-3 h-3 bg-yellow-500 rounded-full"></div>
            <span class="text-sm text-gray-600">Medium Fee</span>
          </div>
          <span class="font-semibold text-gray-900">{{ data.fee_distribution.medium }}</span>
        </div>
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <div class="w-3 h-3 bg-red-500 rounded-full"></div>
            <span class="text-sm text-gray-600">High Fee</span>
          </div>
          <span class="font-semibold text-gray-900">{{ data.fee_distribution.high }}</span>
        </div>
      </div>
    </div>
  </div>
</div>
```

- [ ] **Step 3: Commit**

```bash
git add src/app/components/mempool-card.*
git commit -m "feat: Add mempool card component"
```

---

### Task 12: Frontend Components - Blockchain Card

**Files:**
- Create: `snapshot-inteligente-frontend/src/app/components/blockchain-card.component.ts`
- Create: `snapshot-inteligente-frontend/src/app/components/blockchain-card.component.html`

- [ ] **Step 1: Create blockchain card component**

Generate:
```bash
ng generate component components/blockchain-card --skip-tests
```

Update `blockchain-card.component.ts`:
```typescript
import { Component, Input } from '@angular/core';
import { BlockchainLag } from '../models/blockchain.model';

@Component({
  selector: 'app-blockchain-card',
  templateUrl: './blockchain-card.component.html',
  styleUrls: ['./blockchain-card.component.scss']
})
export class BlockchainCardComponent {
  @Input() data: BlockchainLag | null = null;

  isLagging(): boolean {
    return this.data ? this.data.lag > 5 : false;
  }

  getLagStatus(): string {
    if (!this.data) return 'unknown';
    if (this.data.lag === 0) return 'synced';
    if (this.data.lag <= 5) return 'syncing';
    return 'lagging';
  }

  getLagColor(): string {
    const status = this.getLagStatus();
    switch (status) {
      case 'synced': return 'text-green-600';
      case 'syncing': return 'text-yellow-600';
      case 'lagging': return 'text-red-600';
      default: return 'text-gray-600';
    }
  }

  getBgColor(): string {
    const status = this.getLagStatus();
    switch (status) {
      case 'synced': return 'bg-green-50';
      case 'syncing': return 'bg-yellow-50';
      case 'lagging': return 'bg-red-50';
      default: return 'bg-gray-50';
    }
  }

  getStatusIcon(): string {
    const status = this.getLagStatus();
    switch (status) {
      case 'synced': return '✓';
      case 'syncing': return '↻';
      case 'lagging': return '⚠';
      default: return '?';
    }
  }
}
```

- [ ] **Step 2: Create blockchain card template**

Create `blockchain-card.component.html`:
```html
<div class="bg-white rounded-lg shadow-md p-6">
  <h2 class="text-2xl font-bold text-gray-900 mb-6">Node Sync Status</h2>

  <div *ngIf="data" class="space-y-6">
    <!-- Status Indicator -->
    <div [ngClass]="getBgColor()" class="p-4 rounded-md border-l-4" [ngClass]="{'border-l-green-600': getLagStatus() === 'synced', 'border-l-yellow-600': getLagStatus() === 'syncing', 'border-l-red-600': getLagStatus() === 'lagging'}">
      <div class="flex items-center gap-2">
        <span [ngClass]="getLagColor()" class="text-2xl">{{ getStatusIcon() }}</span>
        <div>
          <p class="text-sm font-medium text-gray-700">Status</p>
          <p [ngClass]="getLagColor()" class="font-bold capitalize">
            {{ getLagStatus() }}
          </p>
        </div>
      </div>
    </div>

    <!-- Block Count Stats -->
    <div class="grid grid-cols-2 gap-4">
      <div class="bg-blue-50 p-4 rounded-md">
        <p class="text-sm text-gray-600 font-medium">Blocks</p>
        <p class="text-2xl font-bold text-blue-600">{{ data.blocks | number }}</p>
      </div>
      <div class="bg-purple-50 p-4 rounded-md">
        <p class="text-sm text-gray-600 font-medium">Headers</p>
        <p class="text-2xl font-bold text-purple-600">{{ data.headers | number }}</p>
      </div>
    </div>

    <!-- Lag Indicator -->
    <div class="bg-gray-50 p-4 rounded-md">
      <p class="text-sm font-medium text-gray-700 mb-3">Sync Lag</p>
      <div class="flex items-baseline gap-2">
        <p [ngClass]="{'text-green-600': data.lag === 0, 'text-yellow-600': data.lag > 0 && data.lag <= 5, 'text-red-600': data.lag > 5}" class="text-3xl font-bold">
          {{ data.lag }}
        </p>
        <p class="text-gray-600">blocks behind</p>
      </div>
      <p class="text-xs text-gray-500 mt-2">
        Difference between headers received and blocks synced
      </p>
    </div>

    <!-- Warning (if lagging) -->
    <div *ngIf="isLagging()" class="bg-red-100 border border-red-400 text-red-700 p-4 rounded-md">
      <p class="font-semibold">⚠ Sync Lag Detected</p>
      <p class="text-sm mt-1">Your node is {{ data.lag }} blocks behind. It's still synchronizing.</p>
    </div>
  </div>
</div>
```

- [ ] **Step 3: Commit**

```bash
git add src/app/components/blockchain-card.*
git commit -m "feat: Add blockchain card component with sync status"
```

---

### Task 13: App Module & Main Component

**Files:**
- Modify: `snapshot-inteligente-frontend/src/app/app.module.ts`
- Modify: `snapshot-inteligente-frontend/src/app/app.component.html`
- Create: `snapshot-inteligente-frontend/src/environments/environment.ts`

- [ ] **Step 1: Create environment files**

Create `src/environments/environment.ts`:
```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api'
};
```

Create `src/environments/environment.prod.ts`:
```typescript
export const environment = {
  production: true,
  apiUrl: '/api'
};
```

- [ ] **Step 2: Update app.module.ts**

Update `src/app/app.module.ts`:
```typescript
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { HttpClientModule } from '@angular/common/http';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { CommonModule } from '@angular/common';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { MempoolCardComponent } from './components/mempool-card/mempool-card.component';
import { BlockchainCardComponent } from './components/blockchain-card/blockchain-card.component';

@NgModule({
  declarations: [
    AppComponent,
    DashboardComponent,
    MempoolCardComponent,
    BlockchainCardComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    HttpClientModule,
    MatCardModule,
    MatButtonModule,
    CommonModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
```

- [ ] **Step 3: Update app.component.html**

Update `src/app/app.component.html`:
```html
<app-dashboard></app-dashboard>
```

- [ ] **Step 4: Commit**

```bash
git add src/app/app.module.ts src/app/app.component.html src/environments/
git commit -m "feat: Configure app module and environment files"
```

---

## **Testing & Integration**

### Task 14: Test Backend Endpoints

**Files:** (No new files, testing existing code)

- [ ] **Step 1: Start Bitcoin Core in regtest mode**

Ensure Bitcoin Core is running with RPC enabled on localhost:8332:
```bash
bitcoind -regtest -server -rpcuser=bitcoin -rpcpassword=changeme
```

- [ ] **Step 2: Start backend**

In backend directory:
```bash
source venv/bin/activate
python app.py
```

Expected: Server starts on http://0.0.0.0:8000

- [ ] **Step 3: Test health endpoint**

```bash
curl http://localhost:8000/health
```

Expected: `{"status":"ok","rpc":"connected","timestamp":"..."}`

- [ ] **Step 4: Test mempool endpoint**

```bash
curl http://localhost:8000/api/mempool/summary
```

Expected: `{"tx_count":0,"total_vsize":0,"avg_fee_rate":0.0,"fee_distribution":{"low":0,"medium":0,"high":0},"timestamp":"..."}`

- [ ] **Step 5: Test blockchain endpoint**

```bash
curl http://localhost:8000/api/blockchain/lag
```

Expected: `{"blocks":0,"headers":0,"lag":0,"timestamp":"..."}`

- [ ] **Step 6: Commit test results**

```bash
git add docs/
git commit -m "test: Verify backend endpoints working correctly"
```

---

### Task 15: Test Frontend & Integration

**Files:** (No new files)

- [ ] **Step 1: Start frontend dev server**

In frontend directory:
```bash
npm start
```

Expected: Angular serves on http://localhost:4200

- [ ] **Step 2: Open browser and verify dashboard**

Navigate to: `http://localhost:4200`

Expected:
- Dashboard loads
- "Connected" indicator shows green
- Mempool card displays transaction count (0 in regtest)
- Blockchain card shows blocks/headers sync status

- [ ] **Step 3: Verify auto-refresh**

Wait 15 seconds, verify data refreshes automatically.

- [ ] **Step 4: Test manual refresh**

Click "Refresh" button, verify data updates immediately.

- [ ] **Step 5: Test error handling**

Stop Bitcoin Core, wait for backend to fail, verify:
- "Disconnected" indicator shows red
- Error message displays
- Retry button works

Restart Bitcoin Core, error should resolve.

- [ ] **Step 6: Commit integration test**

```bash
git add docs/
git commit -m "test: Frontend and backend integration verified"
```

---

## **Deployment & Documentation**

### Task 16: Create Dockerfile & Docker Compose

**Files:**
- Create: `snapshot-inteligente-backend/Dockerfile`
- Create: `snapshot-inteligente-backend/docker-compose.yml`
- Create: `snapshot-inteligente-frontend/Dockerfile`

- [ ] **Step 1: Create backend Dockerfile**

Create `snapshot-inteligente-backend/Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run application
CMD ["python", "app.py"]
```

- [ ] **Step 2: Create docker-compose.yml**

Create `docker-compose.yml` in project root:
```yaml
version: '3.9'

services:
  bitcoin:
    image: bitcoin:latest
    container_name: bitcoin-regtest
    ports:
      - "8332:8332"
      - "18333:18333"
    environment:
      BITCOIN_NETWORK: regtest
    volumes:
      - bitcoin_data:/bitcoin/.bitcoin

  backend:
    build: ./snapshot-inteligente-backend
    container_name: snapshot-backend
    ports:
      - "8000:8000"
    environment:
      BITCOIN_RPC_HOST: bitcoin
      BITCOIN_RPC_PORT: 8332
      BITCOIN_RPC_USER: bitcoin
      BITCOIN_RPC_PASSWORD: changeme
      CACHE_TTL_SECONDS: 10
    depends_on:
      - bitcoin
    volumes:
      - ./snapshot-inteligente-backend:/app

  frontend:
    build: ./snapshot-inteligente-frontend
    container_name: snapshot-frontend
    ports:
      - "4200:80"
    environment:
      API_URL: http://localhost:8000/api
    depends_on:
      - backend

volumes:
  bitcoin_data:
```

- [ ] **Step 3: Create frontend Dockerfile**

Create `snapshot-inteligente-frontend/Dockerfile`:
```dockerfile
# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build -- --configuration production

# Runtime stage
FROM nginx:alpine

COPY --from=builder /app/dist/snapshot-inteligente-frontend /usr/share/nginx/html

COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

- [ ] **Step 4: Create nginx config for frontend**

Create `snapshot-inteligente-frontend/nginx.conf`:
```nginx
events {
  worker_connections 1024;
}

http {
  include /etc/nginx/mime.types;
  default_type application/octet-stream;

  server {
    listen 80;
    server_name _;
    root /usr/share/nginx/html;

    # Angular routing
    location / {
      try_files $uri $uri/ /index.html;
    }

    # API proxy
    location /api {
      proxy_pass http://backend:8000;
      proxy_http_version 1.1;
      proxy_set_header Upgrade $http_upgrade;
      proxy_set_header Connection 'upgrade';
      proxy_set_header Host $host;
      proxy_cache_bypass $http_upgrade;
    }
  }
}
```

- [ ] **Step 5: Commit**

```bash
git add Dockerfile docker-compose.yml nginx.conf
git commit -m "chore: Add Docker configuration for deployment"
```

---

### Task 17: Create README & Documentation

**Files:**
- Create: `README.md`
- Create: `snapshot-inteligente-backend/README.md`
- Create: `snapshot-inteligente-frontend/README.md`

- [ ] **Step 1: Create root README.md**

Create `README.md`:
```markdown
# Snapshot Inteligente

Bitcoin node state interpretation system with real-time analysis and visualization.

## Overview

Snapshot Inteligente interprets Bitcoin node state by analyzing mempool data and blockchain synchronization status. It provides a modern web dashboard for monitoring network activity and node health.

## Project Structure

```
snapshot-inteligente/
├── snapshot-inteligente-backend/   # FastAPI backend
├── snapshot-inteligente-frontend/  # Angular frontend
├── docs/                           # Documentation
├── docker-compose.yml              # Container orchestration
└── README.md                       # This file
```

## Quick Start

### Prerequisites

- Docker & Docker Compose (recommended)
- OR: Python 3.11+, Node.js 18+, Bitcoin Core 24.0+

### With Docker Compose

```bash
docker-compose up -d
```

Access:
- Frontend: http://localhost:4200
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Manual Setup

**Backend:**
```bash
cd snapshot-inteligente-backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your Bitcoin RPC credentials
python app.py
```

**Frontend:**
```bash
cd snapshot-inteligente-frontend
npm install
npm start
```

Visit: http://localhost:4200

## Features

✅ Real-time mempool analysis with fee classification  
✅ Blockchain sync status monitoring  
✅ Auto-refresh dashboard every 15 seconds  
✅ Fee distribution visualization  
✅ Configurable thresholds via environment variables  
✅ Health check endpoint  
✅ Full API documentation with Swagger  

## Architecture

- **Backend:** FastAPI with layered architecture (RPC Client → Cache → Service → Routes)
- **Frontend:** Angular with TypeScript, Tailwind CSS, Angular Material
- **Caching:** In-memory TTL-based cache (5-30s configurable)
- **RPC:** Bitcoin Core JSON-RPC 2.0

## API Endpoints

- `GET /health` - Health check
- `GET /api/mempool/summary` - Mempool analysis
- `GET /api/blockchain/lag` - Sync status

See backend README for detailed API documentation.

## Configuration

Backend configuration via `.env` file:

```
BITCOIN_RPC_HOST=localhost
BITCOIN_RPC_PORT=8332
BITCOIN_RPC_USER=bitcoin
BITCOIN_RPC_PASSWORD=changeme
CACHE_TTL_SECONDS=10
FEE_LOW_THRESHOLD=10
FEE_HIGH_THRESHOLD=50
```

## Development

See individual READMEs:
- [Backend Development](./snapshot-inteligente-backend/README.md)
- [Frontend Development](./snapshot-inteligente-frontend/README.md)

## Testing

**Backend:**
```bash
cd snapshot-inteligente-backend
pytest tests/ -v
```

**Frontend:**
```bash
cd snapshot-inteligente-frontend
npm test
```

## Deployment

See `docs/superpowers/specs/2026-05-01-snapshot-inteligente-design.md` for detailed deployment guide.

## License

MIT

## Support

For issues or questions, refer to the architecture document at `docs/superpowers/specs/2026-05-01-snapshot-inteligente-design.md`.
```

- [ ] **Step 2: Create backend README**

Create `snapshot-inteligente-backend/README.md`:
```markdown
# Snapshot Inteligente - Backend

FastAPI backend service for Bitcoin node state interpretation.

## Setup

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

## Configuration

Edit `.env`:
- `BITCOIN_RPC_HOST`, `BITCOIN_RPC_PORT` - Bitcoin Core connection
- `BITCOIN_RPC_USER`, `BITCOIN_RPC_PASSWORD` - RPC credentials
- `CACHE_TTL_SECONDS` - Cache expiration (default: 10)
- `FEE_LOW_THRESHOLD`, `FEE_HIGH_THRESHOLD` - Fee classification

## Running

```bash
python app.py
```

Server runs on http://0.0.0.0:8000

## API Documentation

Auto-generated Swagger docs: http://localhost:8000/docs

## Testing

```bash
pytest tests/ -v
```

## Project Structure

- `layers/` - Core business logic layers
  - `rpc_client.py` - Bitcoin RPC communication
  - `cache_layer.py` - Response caching
  - `bitcoin_service.py` - Data interpretation
- `routes/` - API endpoints
- `models/` - Pydantic schemas and exceptions
```

- [ ] **Step 3: Create frontend README**

Create `snapshot-inteligente-frontend/README.md`:
```markdown
# Snapshot Inteligente - Frontend

Angular dashboard for Bitcoin node monitoring.

## Setup

```bash
npm install
```

## Development

```bash
npm start
```

Dev server: http://localhost:4200

## Building

```bash
npm run build
```

Production build in `dist/`

## Testing

```bash
npm test
```

## Configuration

Backend API URL in `src/environments/environment.ts`:

```typescript
export const environment = {
  apiUrl: 'http://localhost:8000/api'
};
```

## Components

- `DashboardComponent` - Main container
- `MempoolCardComponent` - Mempool metrics
- `BlockchainCardComponent` - Sync status

## Services

- `BitcoinApiService` - Backend HTTP communication
```

- [ ] **Step 4: Commit**

```bash
git add README.md snapshot-inteligente-backend/README.md snapshot-inteligente-frontend/README.md
git commit -m "docs: Add comprehensive README documentation"
```

---

## **Final Summary**

All tasks for Task 1 implementation are now defined. The plan covers:

✅ **Backend:** RPC client, caching, business logic, API endpoints  
✅ **Frontend:** Components, services, auto-refresh, error handling  
✅ **Testing:** Unit tests and integration tests  
✅ **Deployment:** Docker setup  
✅ **Documentation:** READMEs and API docs  

**Total estimated commits:** 20+

**Next steps:**
1. Execute backend tasks 1-7
2. Execute frontend tasks 8-13
3. Run integration tests (task 14-15)
4. Deploy with Docker (task 16)
5. Verify all requirements met

---

Plan complete and saved to `docs/superpowers/plans/2026-05-01-snapshot-inteligente-implementation.md`.

Two execution options:

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?