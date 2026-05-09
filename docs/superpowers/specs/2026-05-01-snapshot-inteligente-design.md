# Snapshot Inteligente - Architecture Design

**Date:** 2026-05-01 (Updated: 2026-05-09)
**Project:** Bitcoin Node State Interpretation System
**Status:** Tasks 1, 2, 3 Complete

---

## **Vision & Objectives**

Build a lightweight backend service and frontend dashboard to interpret Bitcoin node state by analyzing mempool data, blockchain sync status, real-time ZMQ events, and multi-wallet operations. The system performs intelligent data analysis on raw RPC calls without persistent storage, focusing on clarity, maintainability, and real-time extensibility.

### **High-Level Goals**
- **Mempool Intelligence:** Extract and visualize transaction fee distribution and network activity
- **Node Sync Status:** Monitor blockchain synchronization lag to detect network delays
- **Real-Time Events:** Stream Bitcoin events (blocks, transactions) via ZMQ for immediate updates
- **Multi-Wallet Support:** Manage multiple wallets with real-time balance and UTXO tracking
- **Transaction Operations:** Create, sign, and broadcast transactions from the UI
- **Layered Architecture:** Enable clean separation of concerns for testability and extensibility
- **Reactive Frontend:** Stream-based data polling to eliminate page reload glitches
- **Performance:** Minimize RPC calls through intelligent caching

---

## **1. Project Structure**

```
snapshot-inteligente/
├── bitcoin-31.0/                    # Bitcoin Core binaries
├── btc-regtest-n1/                   # Bitcoin node data (regtest)
├── backend/
│   ├── app.py                       # FastAPI application entry point
│   ├── config.py                    # Configuration management
│   ├── dependencies.py              # Dependency injection setup
│   ├── requirements.txt             # Python dependencies
│   ├── layers/
│   │   ├── rpc_client.py           # Bitcoin RPC communication
│   │   ├── cache_layer.py          # Time-based caching decorator
│   │   ├── bitcoin_service.py      # Business logic & interpretation
│   │   └── event_buffer.py         # Event streaming & ZMQ listener
│   ├── routes/
│   │   ├── health.py               # Health check endpoint
│   │   ├── mempool.py              # Mempool summary endpoints
│   │   ├── blockchain.py           # Blockchain sync endpoints
│   │   ├── events.py               # Event streaming endpoints
│   │   ├── wallets.py              # Wallet management endpoints
│   │   └── transactions.py         # Transaction operation endpoints
│   ├── models/
│   ├── utils/
│   ├── tests/
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/
│   │   │   │   ├── dashboard.component.ts
│   │   │   │   ├── wallet-selector.component.ts
│   │   │   │   ├── wallet-status-card.component.ts
│   │   │   │   ├── send-transaction.component.ts
│   │   │   │   ├── transaction-history.component.ts
│   │   │   │   ├── mempool-card.component.ts
│   │   │   │   ├── blockchain-card.component.ts
│   │   │   │   ├── blockchain-reorg-detector.component.ts
│   │   │   │   ├── event-activity-card.component.ts
│   │   │   │   └── latest-events-card.component.ts
│   │   │   ├── services/
│   │   │   │   ├── bitcoin-api.service.ts
│   │   │   │   └── data-polling.service.ts    # Centralized reactive polling
│   │   │   ├── models/
│   │   │   │   ├── mempool.model.ts
│   │   │   │   ├── blockchain.model.ts
│   │   │   │   ├── events.model.ts
│   │   │   │   └── wallet.model.ts
│   │   │   └── app.module.ts
│   │   └── environments/
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
│           ├── error-correction-plan.md
│           └── defect-analysis-2026-05-09.md
│
├── docker-compose.yml
└── README.md
```

---

## **2. Layered Architecture Design**

### **2.1 RPC Client Layer (`layers/rpc_client.py`)**

**Purpose:** Handle all direct communication with Bitcoin Core RPC.

**Core Methods:**
- `call(method, params)` - Execute raw RPC call
- Error handling: `RPCConnectionError`, `RPCMethodError`

**Configuration:**
- `BITCOIN_RPC_HOST`, `BITCOIN_RPC_PORT`
- `BITCOIN_RPC_USER`, `BITCOIN_RPC_PASSWORD`
- `RPC_TIMEOUT_SECONDS` (default: 5)

---

### **2.2 Cache Layer (`layers/cache_layer.py`)**

**Purpose:** Reduce RPC call frequency by caching responses with TTL.

**Key Mechanism:**
- `@cache_layer.cached(ttl_seconds=N)` decorator
- Cache hit/miss statistics
- Automatic expiration on access

**Configuration:**
- `CACHE_TTL_SECONDS` (default: 10)

---

### **2.3 Business Logic Layer (`layers/bitcoin_service.py`)**

**Purpose:** Interpret raw Bitcoin data, classify transactions, compute derived metrics.

**Core Methods:**
- `get_mempool_summary()` - Fee distribution analysis
- `get_blockchain_lag()` - Sync status monitoring

**Fee Classification:**
| Category | Condition | Default Range |
|----------|-----------|---------------|
| Low | fee_rate < FEE_LOW_THRESHOLD | < 10 sat/vB |
| Medium | FEE_LOW_THRESHOLD ≤ rate ≤ FEE_HIGH_THRESHOLD | 10-50 sat/vB |
| High | fee_rate > FEE_HIGH_THRESHOLD | > 50 sat/vB |

---

### **2.4 Event Buffer Layer (`layers/event_buffer.py`)**

**Purpose:** Real-time Bitcoin event streaming via ZMQ.

**Components:**
- `EventBuffer` - Circular buffers (50 blocks, 500 transactions)
- `ZMQListener` - Async listener for hashblock/rawtx topics

**Configuration:**
- `ZMQ_HOST` (default: localhost)
- `ZMQ_PORT` (default: 28332)
- `EVENT_BUFFER_BLOCKS` (default: 50)
- `EVENT_BUFFER_TRANSACTIONS` (default: 500)

---

### **2.5 API Routes Layer**

**Files:** `routes/health.py`, `mempool.py`, `blockchain.py`, `events.py`, `wallets.py`, `transactions.py`

---

## **3. Task 3: Multiple Wallets Support**

### **3.1 Overview**

Task 3 extends the system with **multi-wallet management** and **transaction operations** directly from the frontend UI.

**Key Features:**
- List and select from multiple Bitcoin wallets
- Real-time wallet status (balance, UTXOs)
- UTXO management and selection
- Transaction creation, signing, and broadcasting
- Transaction history tracking

### **3.2 New Backend Endpoints**

#### **Wallet Management**

```python
# GET /api/wallet/list
Response: {
    "available_wallets": ["default", "wallet2"],
    "loaded_wallets": ["default"],
    "selected_wallet": "default"
}

# POST /api/wallet/select
Request: {"wallet": "wallet2"}
Response: {
    "selected_wallet": "wallet2",
    "wallet_info": {
        "walletname": "wallet2",
        "balance": 0.5,
        "txcount": 12
    }
}

# GET /api/wallet/status
Response: {
    "wallet": "wallet2",
    "balance": 0.5,
    "utxos": 3
}
```

#### **Transaction Operations**

```python
# GET /api/tx/utxos
Response: {
    "utxos": [
        {
            "txid": "abc123...",
            "vout": 0,
            "amount": 0.25,
            "script": "0014...",
            "confirmations": 6
        }
    ],
    "total_balance": 0.5,
    "spendable_balance": 0.5
}

# GET /api/tx/estimate-fee
Query: ?target_blocks=2
Response: {
    "fee_rate": 15.5,
    "unit": "sat/vB",
    "estimated_satoshis": 2500,
    "target_blocks": 2
}

# POST /api/tx/create
Request: {
    "recipient_address": "bcrt1q...",
    "amount_satoshis": 100000,
    "fee_rate_sat_vb": 15.0
}
Response: {
    "unsigned_tx": "0200000001...",
    "fee_amount": 1500,
    "total_amount": 101500
}

# POST /api/tx/sign
Request: {"unsigned_tx": "0200000001..."}
Response: {
    "signed_tx": "0200000002...",
    "txid": "def456..."
}

# POST /api/tx/broadcast
Request: {"signed_tx": "0200000002..."}
Response: {
    "txid": "def456...",
    "broadcast": true,
    "mempool_rejected": false
}

# GET /api/tx/sent-history
Response: {
    "transactions": [
        {
            "txid": "def456...",
            "recipient": "bcrt1q...",
            "amount": 0.001,
            "fee": 1500,
            "broadcast_at": "2026-05-09T10:30:00Z",
            "status": "broadcast"
        }
    ]
}
```

### **3.3 Frontend Components**

#### **WalletSelectorComponent**
- Dropdown to list and select wallets
- Auto-select on single wallet
- Emits `walletSelected` event on change

#### **WalletStatusCardComponent**
- Displays current wallet balance
- Shows UTXO count
- Real-time updates via DataPollingService

#### **SendTransactionComponent**
- Recipient address input
- Amount input with BTC/sat conversion
- Fee rate selection
- Transaction creation wizard (create → sign → broadcast)

#### **TransactionHistoryComponent**
- List of sent transactions
- Status indicators (broadcast, confirmed, failed)
- Copy TXID functionality

### **3.4 Data Flow for Transaction Creation**

```
User enters recipient + amount
  → POST /api/tx/create → unsigned_tx
  → POST /api/tx/sign → signed_tx
  → POST /api/tx/broadcast → txid
  → Update sent-history + wallet status
```

### **3.5 Bitcoin Core Wallet Integration**

The backend uses `-rpcwallet` parameter to interact with specific wallets:
- `getwalletinfo` - Wallet balance and UTXO count
- `listunspent` - UTXO list for transaction creation
- `createrawtransaction` - Build unsigned transaction
- `signrawtransactionwithwallet` - Sign with wallet keys
- `sendrawtransaction` - Broadcast to network

---

## **4. Frontend Architecture: DataPollingService**

### **4.1 Overview**

The frontend uses a **centralized DataPollingService** with BehaviorSubjects for reactive data streaming. This eliminates the "F5 glitch" problem where page reloads would reset component state.

### **4.2 Architecture**

```typescript
@Injectable({ providedIn: 'root' })
export class DataPollingService implements OnDestroy {
  private readonly POLL_INTERVAL = 15000;
  
  // BehaviorSubjects for each data stream
  healthSubject = new BehaviorSubject<boolean>(false);
  mempoolSubject = new BehaviorSubject<MempoolSummary | null>(null);
  blockchainLagSubject = new BehaviorSubject<BlockchainLag | null>(null);
  walletStatusSubject = new BehaviorSubject<WalletStatus | null>(null);
  recentBlocksSubject = new BehaviorSubject<BlockEvent[]>([]);
  recentTransactionsSubject = new BehaviorSubject<TransactionEvent[]>([]);
  eventStatsSubject = new BehaviorSubject<EventStats | null>(null);
  latestEventsSubject = new BehaviorSubject<LatestEvents | null>(null);
  stateComparisonSubject = new BehaviorSubject<StateComparison | null>(null);
  sentTransactionsSubject = new BehaviorSubject<SentTransaction[]>([]);

  // Observable streams
  health$ = this.healthSubject.asObservable();
  mempool$ = this.mempoolSubject.asObservable();
  // ... etc
}
```

### **4.3 Polling Mechanism**

```typescript
private pollAll(): void {
  forkJoin({
    health: this.req<any>('/health'),
    mempool: this.req<MempoolSummary>('/api/mempool/summary'),
    blockchainLag: this.req<BlockchainLag>('/api/blockchain/lag'),
    walletStatus: this.req<WalletStatus>('/api/wallet/status'),
    // ... all endpoints
  }).subscribe({
    next: (data) => {
      // Update each BehaviorSubject
      this.healthSubject.next(data.health?.rpc === 'connected');
      this.mempoolSubject.next(data.mempool);
      this.blockchainLagSubject.next(data.blockchainLag);
      // ...
    },
    error: () => {
      this.healthSubject.next(false);
    }
  });
}
```

### **4.4 Component Subscription Pattern**

```typescript
// In component
constructor(private dataPolling: DataPollingService) {}

ngOnInit(): void {
  this.dataPolling.walletStatus$
    .pipe(takeUntil(this.destroy$))
    .subscribe(status => {
      this.walletStatus = status;  // Direct update, no reload
    });
}

// On wallet selection
onWalletSelected(wallet: string): void {
  this.dataPolling.refreshWalletStatus();  // Immediate refresh
}
```

### **4.5 Benefits**

1. **No Page Reload:** Data updates via stream, not component re-initialization
2. **Centralized Polling:** Single forkJoin, 10 endpoints, 1 poll cycle
3. **Error Isolation:** Individual `catchError` per request
4. **Immediate Refresh:** `refreshWalletStatus()` for wallet changes
5. **Memory Efficient:** BehaviorSubjects keep last value for new subscribers

### **4.6 Error Handling**

Each request uses `catchError(() => of(null))` so one failed endpoint doesn't break the entire poll:

```typescript
private req<T>(url: string): Observable<T | null> {
  return this.http.get<T>(url).pipe(
    catchError(() => of(null as any))
  );
}
```

---

## **5. Configuration Reference**

### **Backend (.env)**

```env
# Bitcoin RPC (Regtest)
BITCOIN_RPC_HOST=localhost
BITCOIN_RPC_PORT=18443
BITCOIN_RPC_USER=teste
BITCOIN_RPC_PASSWORD=teste
RPC_TIMEOUT_SECONDS=5

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

### **Bitcoin Core (bitcoin.conf)**

```conf
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

---

## **6. Success Criteria**

### **Task 1: Mempool & Blockchain**
✅ Real-time mempool analysis with fee classification  
✅ Blockchain sync status monitoring  
✅ Auto-refresh dashboard every 15 seconds  
✅ Fee distribution visualization  
✅ Health check endpoint reliably detects RPC availability  

### **Task 2: Real-Time Event Streaming**
✅ ZMQ listener streams block/transaction events  
✅ EventBuffer maintains circular buffers (50 blocks, 500 txs)  
✅ State comparison detects blockchain reorg scenarios  
✅ Frontend displays event activity without manual refresh  

### **Task 3: Multiple Wallets Support**
✅ List and select from multiple wallets  
✅ Real-time wallet status updates  
✅ Transaction creation, signing, broadcasting  
✅ Transaction history tracking  
✅ UTXO management  

### **Frontend Architecture**
✅ DataPollingService with BehaviorSubjects  
✅ No F5-like glitches on data updates  
✅ Immediate refresh on wallet selection  
✅ Error isolation per endpoint  

---

## **7. Deployment Guide**

### **Start Bitcoin Node**

```bash
mkdir -p btc-regtest-n1
cp btc-regtest-n1/bitcoin.conf.bak btc-regtest-n1/bitcoin.conf
./bitcoin-31.0/bin/bitcoind -datadir=./btc-regtest-n1 -daemon

# Create wallets
./bitcoin-31.0/bin/bitcoin-cli -datadir=./btc-regtest-n1 createwallet default
```

### **Start Backend**

```bash
cd snapshot-inteligente-backend
source ../.venv/bin/activate
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

### **Start Frontend**

```bash
cd snapshot-inteligente-frontend
npm install
npm run start
```

### **Access Points**

- Frontend: http://localhost:4200
- Backend: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs

---

**Last Updated:** 2026-05-09