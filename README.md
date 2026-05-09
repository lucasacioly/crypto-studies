# Snapshot Inteligente

Bitcoin node state interpretation system with real-time analysis, event streaming, and multi-wallet support.

## Overview

Snapshot Inteligente interprets Bitcoin node state by analyzing mempool data, blockchain synchronization, real-time events via ZMQ, and provides a modern web dashboard for monitoring and wallet operations.

## Project Structure

```
bitcoincoders/
├── bitcoin-31.0/                    # Bitcoin Core binaries
├── btc-regtest-n1/                   # Bitcoin node data directory (regtest)
├── snapshot-inteligente-backend/     # FastAPI backend
├── snapshot-inteligente-frontend/    # Angular frontend
├── docs/                            # Documentation
├── docker-compose.yml                # Container orchestration
└── README.md                        # This file
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Bitcoin Core 24.0+

### 1. Start Bitcoin Node (Regtest)

```bash
# Create data directory and config
mkdir -p btc-regtest-n1
cp btc-regtest-n1/bitcoin.conf.bak btc-regtest-n1/bitcoin.conf

# Start bitcoind
./bitcoin-31.0/bin/bitcoind -datadir=./btc-regtest-n1 -daemon

# Create wallets
./bitcoin-31.0/bin/bitcoin-cli -datadir=./btc-regtest-n1 createwallet default
./bitcoin-31.0/bin/bitcoin-cli -datadir=./btc-regtest-n1 createwallet wallet2
```

### 2. Start Backend

```bash
cd snapshot-inteligente-backend
source ../.venv/bin/activate
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

### 3. Start Frontend

```bash
cd snapshot-inteligente-frontend
npm install
npm run start
```

Access:
- Frontend: http://localhost:4200
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Features

### Task 1: Mempool & Blockchain Analysis (Complete)
✅ Real-time mempool analysis with fee classification  
✅ Blockchain sync status monitoring  
✅ Auto-refresh dashboard via DataPollingService (15s interval)  
✅ Fee distribution visualization  
✅ Configurable thresholds via environment variables  
✅ Health check endpoint  
✅ Full API documentation with Swagger

### Task 2: Real-Time Event Streaming (Complete)
✅ Bitcoin ZMQ event listener (hashblock, rawtx)  
✅ Circular buffers for blocks (50) & transactions (500)  
✅ REST endpoints for event history  
✅ Blockchain state comparison (reorg detection)  
✅ Frontend event activity visualization  
✅ ZMQ connection status monitoring

### Task 3: Multiple Wallets Support (Complete)
✅ List available wallets  
✅ Dynamic wallet selection  
✅ Real-time wallet status (balance, UTXOs)  
✅ Transaction creation, signing, and broadcasting  
✅ Transaction history tracking  
✅ UTXO management  
✅ Fee estimation

## Architecture

- **Backend:** FastAPI with layered architecture (RPC Client → Cache → Service → Routes)
- **Frontend:** Angular with TypeScript, Tailwind CSS, DataPollingService for reactive data
- **Caching:** In-memory TTL-based cache (configurable)
- **RPC:** Bitcoin Core JSON-RPC 2.0
- **Events:** ZMQ pub/sub for real-time Bitcoin events

## API Endpoints

### Health & Core
- `GET /health` - Health check (RPC + ZMQ status)

### Mempool & Blockchain
- `GET /api/mempool/summary` - Mempool analysis
- `GET /api/blockchain/lag` - Sync status

### Event Streaming
- `GET /api/events/blocks` - Recent block events from buffer
- `GET /api/events/transactions` - Recent transaction events
- `GET /api/events/stats` - Buffer statistics & ZMQ status
- `GET /api/events/state-comparison` - Blockchain reorg detection
- `GET /api/events/latest` - Combined latest events

### Wallet Operations
- `GET /api/wallet/list` - List available wallets
- `POST /api/wallet/select` - Select active wallet
- `GET /api/wallet/status` - Current wallet status

### Transaction Operations
- `GET /api/tx/utxos` - List wallet UTXOs
- `GET /api/tx/estimate-fee` - Estimate transaction fee
- `POST /api/tx/create` - Create unsigned transaction
- `POST /api/tx/sign` - Sign transaction
- `POST /api/tx/broadcast` - Broadcast transaction
- `GET /api/tx/sent-history` - Transaction history

## Configuration

Backend configuration via `.env` file:

```
# Bitcoin RPC (Regtest)
BITCOIN_RPC_HOST=localhost
BITCOIN_RPC_PORT=18443
BITCOIN_RPC_USER=teste
BITCOIN_RPC_PASSWORD=teste

# Cache
CACHE_TTL_SECONDS=10

# Fee Thresholds (sat/vB)
FEE_LOW_THRESHOLD=10
FEE_HIGH_THRESHOLD=50

# ZMQ
ZMQ_HOST=localhost
ZMQ_PORT=28332

# Event Buffers
EVENT_BUFFER_BLOCKS=50
EVENT_BUFFER_TRANSACTIONS=500

# API
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_URL=http://localhost:4200
```

Bitcoin Core configuration (`btc-regtest-n1/bitcoin.conf`):

```
regtest=1
rpcuser=teste
rpcpassword=teste
rpcallowip=127.0.0.1
fallbackfee=0.0001
rpcport=18443
port=18444
zmqpubhashblock=tcp://127.0.0.1:28332
zmqpubrawtx=tcp://127.0.0.1:28332
```

## Development

### Start All Services

```bash
# 1. Bitcoin node
./bitcoin-31.0/bin/bitcoind -datadir=./btc-regtest-n1 -daemon

# 2. Backend
cd snapshot-inteligente-backend
source ../.venv/bin/activate
python -m uvicorn app:app --host 0.0.0.0 --port 8000

# 3. Frontend
cd snapshot-inteligente-frontend
npm run start
```

### Testing

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

## Frontend Architecture

The frontend uses a **reactive data polling service** to avoid F5-like glitches:

```
DataPollingService (centralized polling every 15s)
├── health$           → Connection status
├── mempool$          → Mempool data
├── blockchainLag$    → Sync status
├── walletStatus$     → Wallet balance/UTXOs
├── recentBlocks$     → ZMQ block events
├── recentTransactions$ → ZMQ transaction events
└── sentTransactions$ → Broadcast history
```

Components subscribe to BehaviorSubjects and receive updates reactively without page reloads.

## Deployment

See `docs/superpowers/specs/2026-05-01-snapshot-inteligente-design.md` for detailed deployment guide.

## License

MIT