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
