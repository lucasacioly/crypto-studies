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
