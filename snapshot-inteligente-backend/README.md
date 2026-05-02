# Snapshot Inteligente - Backend

FastAPI backend service for Bitcoin node state interpretation with real-time event streaming.

## Features

### Task 1: Mempool & Blockchain Analysis
- Mempool fee distribution analysis
- Blockchain synchronization lag detection
- In-memory TTL-based caching (5-30s)
- RESTful API with Swagger documentation

### Task 2: Real-Time Event Streaming (In Progress)
- Bitcoin Core ZMQ event listener (hashblock, rawtx)
- Circular buffers (50 blocks, 500 transactions)
- Event history REST endpoints
- Blockchain state comparison for reorg detection

## Setup

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

## Configuration

Edit `.env`:
- **Bitcoin RPC:** `BITCOIN_RPC_HOST`, `BITCOIN_RPC_PORT`, `BITCOIN_RPC_USER`, `BITCOIN_RPC_PASSWORD`
- **Cache:** `CACHE_TTL_SECONDS` (default: 10)
- **Fee Thresholds:** `FEE_LOW_THRESHOLD` (default: 10), `FEE_HIGH_THRESHOLD` (default: 50)
- **ZMQ:** `ZMQ_HOST` (default: localhost), `ZMQ_PORT` (default: 28332)
- **Event Buffers:** `EVENT_BUFFER_BLOCKS` (default: 50), `EVENT_BUFFER_TRANSACTIONS` (default: 500)

**Bitcoin Core Configuration (bitcoin.conf):**
```
server=1
rpcuser=bitcoin
rpcpassword=secure-password
rpcallowip=127.0.0.1
zmqpubhashblock=tcp://127.0.0.1:28332
zmqpubrawtx=tcp://127.0.0.1:28332
```

## Running

```bash
python app.py
```

Server runs on http://0.0.0.0:8000

## API Documentation

Auto-generated Swagger docs: http://localhost:8000/docs

### Core Endpoints (Task 1)

- `GET /health` - Health check + RPC connectivity
- `GET /api/mempool/summary` - Mempool analysis with fee distribution
- `GET /api/blockchain/lag` - Blockchain sync status

**Example Response: `/api/mempool/summary`**
```json
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
```

### Event Streaming Endpoints (Task 2)

- `GET /api/events/blocks` - Recent block events (query param: `limit=10`)
- `GET /api/events/transactions` - Recent transaction events (query param: `limit=20`)
- `GET /api/events/state-comparison` - Compare buffer vs live RPC state

**Example Response: `/api/events/blocks`**
```json
[
  {
    "block_hash": "00000abc123...",
    "block_height": 572061,
    "timestamp": "2026-05-01T14:30:00",
    "received_at": 1234567890.123
  }
]
```

## Project Structure

```
snapshot-inteligente-backend/
├── app.py                           # FastAPI entry point
├── config.py                        # Configuration management
├── dependencies.py                  # DI setup
├── requirements.txt                 # Dependencies
├── layers/
│   ├── rpc_client.py               # Bitcoin RPC communication
│   ├── cache_layer.py              # TTL-based caching
│   ├── bitcoin_service.py          # Business logic (Task 1)
│   └── event_buffer.py             # Event streaming (Task 2)
├── routes/
│   ├── health.py                   # Health endpoint
│   ├── mempool.py                  # Mempool endpoints
│   ├── blockchain.py               # Blockchain endpoints
│   └── events.py                   # Event endpoints (Task 2)
├── models/
│   ├── errors.py                   # Custom exceptions
│   └── responses.py                # Pydantic response schemas
├── utils/
│   └── logger.py                   # Logging configuration
├── tests/
│   ├── test_rpc_client.py
│   ├── test_cache_layer.py
│   ├── test_bitcoin_service.py
│   └── test_event_buffer.py
└── .env.example                    # Environment template
```

## Testing

```bash
pytest tests/ -v
```

Tests cover:
- RPC client (connection, serialization, error handling)
- Cache layer (TTL, hit/miss, statistics)
- Bitcoin service (fee classification, lag calculation)
- Event buffer (circular buffer, thread-safety)

## Architecture

### Task 1: Layered RPC-Polling Architecture

```
FastAPI Routes
    ↓
BitcoinService (caches results)
    ↓
RPCClient (connects to Bitcoin Core)
    ↓
CacheLayer (TTL-based in-memory cache)
    ↓
Bitcoin Core (RPC interface)
```

### Task 2: Event-Driven Architecture (Parallel)

```
FastAPI Event Endpoints
    ↓
EventBuffer (thread-safe circular buffers)
    ↓
ZMQListener (async background task)
    ↓
Bitcoin Core (ZMQ event stream)
```

## Deployment

### Docker

```bash
docker build -t snapshot-inteligente-backend .
docker run -p 8000:8000 --env-file .env snapshot-inteligente-backend
```

### Manual

```bash
cd snapshot-inteligente-backend
python app.py
```

## Performance Characteristics

- **Mempool Query:** ~500ms (RPC call) → cached for 10s
- **Block Events:** <10ms latency (ZMQ push)
- **Transaction Events:** <50ms latency (ZMQ push)
- **Memory Usage:** ~10MB (buffers + service)
- **Event Buffer Capacity:** 50 blocks, 500 transactions

## Troubleshooting

**"Bitcoin RPC unavailable"**
- Check `BITCOIN_RPC_HOST:PORT` is correct
- Verify Bitcoin Core is running with `server=1` in bitcoin.conf
- Check RPC credentials match

**"ZMQ connection failed"**
- Ensure Bitcoin Core compiled with ZMQ support
- Check `zmqpubhashblock` and `zmqpubrawtx` in bitcoin.conf
- Verify firewall allows port 28332

**Cache not working**
- Check `CACHE_TTL_SECONDS` env var is set (default: 10)
- Monitor cache stats at `GET /cache/stats` (Task 2)

## Documentation

- [Architecture Design](../../docs/superpowers/specs/2026-05-01-snapshot-inteligente-design.md)
- [Implementation Plan](../../docs/superpowers/plans/2026-05-01-snapshot-inteligente-implementation.md)

## Support

For issues or questions, refer to:
- Backend README: This file
- Design Doc: `docs/superpowers/specs/2026-05-01-snapshot-inteligente-design.md`
- GitHub Issues: https://github.com/bitcoincoders/snapshot-inteligente/issues
