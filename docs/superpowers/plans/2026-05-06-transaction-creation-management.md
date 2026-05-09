# Transaction Creation & Management Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement complete transaction creation, signing, broadcasting workflow with UTXO selection, fee estimation, and transaction history display.

**Architecture:** Backend provides REST endpoints for building, signing, and broadcasting transactions with persistent history. Frontend offers simple card-based form with automatic/manual UTXO selection, fee estimation, and transaction history table. Multi-wallet support throughout.

**Tech Stack:** FastAPI (backend), Angular (frontend), Bitcoin Core RPC, Pydantic models, TypeScript interfaces

---

## File Structure

### Backend Files
- **New:** `layers/transaction_builder.py` - UTXO selection, coin selection logic
- **New:** `layers/transaction_signer.py` - Transaction signing wrapper
- **New:** `models/transaction_creation.py` - Request/response models for creation workflow
- **Modify:** `routes/transactions.py` - Add new endpoints for create/sign/broadcast
- **New:** `sent_transactions.json` - Persistent storage of broadcast transactions
- **Modify:** `layers/rpc_client.py` - Add fee estimation RPC calls
- **Modify:** `dependencies.py` - Inject new layers

### Frontend Files
- **New:** `src/app/components/send-transaction.component.ts` - Main form component
- **New:** `src/app/components/send-transaction.component.html` - Template
- **New:** `src/app/components/send-transaction.component.scss` - Styles
- **New:** `src/app/components/transaction-history.component.ts` - History display
- **New:** `src/app/components/transaction-history.component.html` - History template
- **Modify:** `src/app/models/wallet.model.ts` - Add transaction creation models
- **Modify:** `src/app/services/bitcoin-api.service.ts` - Add new API methods
- **Modify:** `src/app/components/dashboard.component.html` - Include new components
- **Modify:** `src/app/app.module.ts` - Register new components

---

## Implementation Tasks

### Task 1: Backend - RPC Client Fee Estimation

**Files:**
- Modify: `snapshot-inteligente-backend/layers/rpc_client.py:135-137`

- [ ] **Step 1: Add fee estimation method to RPCClient**

Edit `layers/rpc_client.py` and add after the `load_wallet` method:

```python
    def estimate_smart_fee(self, target_blocks: int = 2) -> dict:
        """
        Estimate smart fee using Bitcoin Core.
        
        Args:
            target_blocks: Target number of blocks (1-1008)
            
        Returns:
            Dict with fee_rate (BTC/kB) and warnings
        """
        return self.call('estimatesmartfee', [target_blocks])
    
    def estimate_fee_sat_vB(self, target_blocks: int = 2) -> float:
        """
        Estimate fee in sat/vB using Bitcoin Core.
        
        Args:
            target_blocks: Target number of blocks
            
        Returns:
            Fee rate in sat/vB (satoshis per virtual byte)
        """
        estimate = self.estimate_smart_fee(target_blocks)
        fee_btc_per_kb = estimate.get('feerate', 0.0001)
        # Convert BTC/kB to sat/vB: (BTC * 1e8 sat/BTC) / (1000 bytes)
        fee_sat_vB = (fee_btc_per_kb * 100_000_000) / 1000
        return fee_sat_vB
```

- [ ] **Step 2: Commit**

```bash
git add snapshot-inteligente-backend/layers/rpc_client.py
git commit -m "feat: add fee estimation RPC methods"
```

---

### Task 2: Backend - Transaction Builder Layer

**Files:**
- Create: `snapshot-inteligente-backend/layers/transaction_builder.py`

- [ ] **Step 1: Create transaction builder file with complete content**

[See full code in tasks details above]

- [ ] **Step 2: Commit**

```bash
git add snapshot-inteligente-backend/layers/transaction_builder.py
git commit -m "feat: add transaction builder with coin selection"
```

---

### Task 3: Backend - Transaction Signer Layer

**Files:**
- Create: `snapshot-inteligente-backend/layers/transaction_signer.py`

- [ ] **Step 1: Create transaction signer file**

[See full code in tasks details above]

- [ ] **Step 2: Commit**

```bash
git add snapshot-inteligente-backend/layers/transaction_signer.py
git commit -m "feat: add transaction signer and broadcaster"
```

---

### Task 4: Backend - Transaction Creation Models

**Files:**
- Modify: `snapshot-inteligente-backend/models/transactions.py:127-end`

- [ ] **Step 1: Add creation request/response models**

[See full code in tasks details above]

- [ ] **Step 2: Commit**

```bash
git add snapshot-inteligente-backend/models/transactions.py
git commit -m "feat: add transaction creation request/response models"
```

---

### Task 5: Backend - Transaction Routes (Create/Sign/Broadcast)

**Files:**
- Modify: `snapshot-inteligente-backend/routes/transactions.py:101-end`

- [ ] **Step 1: Update transactions.py with new endpoints**

[See full code in tasks details above - complete file replacement]

- [ ] **Step 2: Commit**

```bash
git add snapshot-inteligente-backend/routes/transactions.py
git commit -m "feat: add transaction creation, signing, and broadcasting endpoints"
```

---

### Task 6: Backend - Dependencies & Integration

**Files:**
- Modify: `snapshot-inteligente-backend/dependencies.py`

- [ ] **Step 1: Update dependencies**

[See code in tasks details above]

- [ ] **Step 2: Commit**

```bash
git add snapshot-inteligente-backend/dependencies.py
git commit -m "feat: add transaction builder and signer imports"
```

---

### Task 7: Frontend - Data Models Update

**Files:**
- Modify: `snapshot-inteligente-frontend/src/app/models/wallet.model.ts:51-end`

- [ ] **Step 1: Add transaction creation models**

[See full code in tasks details above]

- [ ] **Step 2: Commit**

```bash
git add snapshot-inteligente-frontend/src/app/models/wallet.model.ts
git commit -m "feat: add transaction creation data models"
```

---

### Task 8: Frontend - API Service Methods

**Files:**
- Modify: `snapshot-inteligente-frontend/src/app/services/bitcoin-api.service.ts:107-end`

- [ ] **Step 1: Add new API methods**

[See full code in tasks details above]

- [ ] **Step 2: Commit**

```bash
git add snapshot-inteligente-frontend/src/app/services/bitcoin-api.service.ts
git commit -m "feat: add transaction creation API methods"
```

---

### Task 9: Frontend - Send Transaction Component (TypeScript)

**Files:**
- Create: `snapshot-inteligente-frontend/src/app/components/send-transaction.component.ts`

- [ ] **Step 1: Create component**

[See full code in tasks details above]

- [ ] **Step 2: Commit**

```bash
git add snapshot-inteligente-frontend/src/app/components/send-transaction.component.ts
git commit -m "feat: add send transaction component logic"
```

---

### Task 10: Frontend - Send Transaction Component (Template)

**Files:**
- Create: `snapshot-inteligente-frontend/src/app/components/send-transaction.component.html`

- [ ] **Step 1: Create template**

[See full HTML code in tasks details above]

- [ ] **Step 2: Commit**

```bash
git add snapshot-inteligente-frontend/src/app/components/send-transaction.component.html
git commit -m "feat: add send transaction template"
```

---

### Task 11: Frontend - Send Transaction Component (Styles)

**Files:**
- Create: `snapshot-inteligente-frontend/src/app/components/send-transaction.component.scss`

- [ ] **Step 1: Create stylesheet**

```scss
// No additional styles needed - using Tailwind CSS utility classes
```

- [ ] **Step 2: Commit**

```bash
git add snapshot-inteligente-frontend/src/app/components/send-transaction.component.scss
git commit -m "style: add send transaction stylesheet (Tailwind-based)"
```

---

### Task 12: Frontend - Transaction History Component (TypeScript)

**Files:**
- Create: `snapshot-inteligente-frontend/src/app/components/transaction-history.component.ts`

- [ ] **Step 1: Create component**

[See full code in tasks details above]

- [ ] **Step 2: Commit**

```bash
git add snapshot-inteligente-frontend/src/app/components/transaction-history.component.ts
git commit -m "feat: add transaction history component logic"
```

---

### Task 13: Frontend - Transaction History Component (Template)

**Files:**
- Create: `snapshot-inteligente-frontend/src/app/components/transaction-history.component.html`

- [ ] **Step 1: Create template**

[See full HTML code in tasks details above]

- [ ] **Step 2: Commit**

```bash
git add snapshot-inteligente-frontend/src/app/components/transaction-history.component.html
git commit -m "feat: add transaction history template"
```

---

### Task 14: Frontend - Transaction History Component (Styles)

**Files:**
- Create: `snapshot-inteligente-frontend/src/app/components/transaction-history.component.scss`

- [ ] **Step 1: Create stylesheet**

```scss
// Tailwind CSS handles all styling
```

- [ ] **Step 2: Commit**

```bash
git add snapshot-inteligente-frontend/src/app/components/transaction-history.component.scss
git commit -m "style: add transaction history stylesheet"
```

---

### Task 15: Frontend - Module Registration & Dashboard Integration

**Files:**
- Modify: `snapshot-inteligente-frontend/src/app/app.module.ts`
- Modify: `snapshot-inteligente-frontend/src/app/components/dashboard.component.html`

- [ ] **Step 1: Update module imports**

[See code in tasks details above]

- [ ] **Step 2: Update dashboard template**

[See template changes in tasks details above]

- [ ] **Step 3: Commit**

```bash
git add snapshot-inteligente-frontend/src/app/app.module.ts snapshot-inteligente-frontend/src/app/components/dashboard.component.html
git commit -m "feat: register send transaction and history components in dashboard"
```

---

## Summary

**15 tasks total:**
- 6 backend tasks (RPC, Builder, Signer, Models, Routes, Dependencies)
- 9 frontend tasks (Models, API, Components x3, Module, Dashboard)

**Endpoints Created:**
- `GET /tx/estimate-fee` - Fee estimation
- `GET /tx/utxos` - List available UTXOs
- `POST /tx/create` - Create unsigned transaction
- `POST /tx/sign` - Sign transaction
- `POST /tx/broadcast` - Broadcast and record
- `GET /tx/sent-history` - Transaction history

**Components Created:**
- `SendTransactionComponent` - Transaction creation form
- `TransactionHistoryComponent` - Sent transactions table

**Files Saved:** `/home/lucas/research/bitcoincoders/docs/superpowers/plans/2026-05-06-transaction-creation-management.md`
