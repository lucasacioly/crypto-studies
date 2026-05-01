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
