# Plano de Correção de Erros

## Problema Atual

A aplicação frontend exibe "Unable to connect to Bitcoin backend" intermitentemente. O backend está funcional, mas os componentes mostram erro de conexão.

## Análise

### Causa Raiz
O `DataPollingService` usa `forkJoin` para fazer polling de todos os endpoints simultaneamente. Quando **um endpoint falha**, todo o polling falha e `health` é setado para `false`.

Exemplo de falha:
- `/wallet/status` → 400 Bad Request ("No wallet selected")

Isso faz o entire `forkJoin` erro, setando `healthSubject.next(false)`.

### Fluxo do Problema

```
DataPollingService.pollAll()
  → forkJoin { health, mempool, walletStatus, ... }
      → walletStatus falha (400)
          → forkJoin completa com erro
              → healthSubject.next(false)
                  → "Unable to connect to Bitcoin backend"
```

## Soluções

### [x] Correção 1: Isolamento de Erros por Endpoint

**Implementado.** Cada request agora usa `catchError(() => of(null))` para falhar individualmente sem quebrar o polling inteiro.

Benefício: Endpoints opcionais (wallet, events) não travam o health check.

---

### [x] Correção 2: Wallet Auto-Select

**Problema:** Nenhum wallet está selecionado, causando 400 em `/wallet/status`.

**Solução:** Selecionar/criar wallet automaticamente na inicialização.

**Passos:**
1. Verificar wallets existentes via `bitcoin-cli listwallets`
2. Se existir wallet padrão, selecionar via `POST /wallet/select`
3. Se não existir, criar wallet via `bitcoin-cli createwallet`
4. Atualizar estado da aplicação

**Comando para testar manualmente:**
```bash
# Criar wallet
/home/lucas/research/bitcoincoders/bitcoin-31.0/bin/bitcoin-cli \
  -datadir=/home/lucas/research/bitcoincoders/btc-regtest-n1 \
  createwallet default

# Listar wallets
/home/lucas/research/bitcoincoders/bitcoin-31.0/bin/bitcoin-cli \
  -datadir=/home/lucas/research/bitcoincoders/btc-regtest-n1 \
  listwallets
```

---

### [x] Correção 3: Health Check Robusto

**Problema:** O health check depende de resposta RPC específica.

**Solução:** Criar endpoint `/health` mais robusto que:
- Retorne `rpc: "connected"` apenas se RPC responder
- Não dependa de estado de wallet
- Tenha timeout configurável

**Passos:**
1. Revisar `routes/health.py` no backend
2. Simplificar lógica para apenas verificar conexão RPC
3. Remover dependência de wallet selecionado

---

### [x] Correção 4: Graceful Degradation

**Problema:** Componentes individuais podem ficar em estado de erro mesmo quando backend está ok.

**Solução:** Componentes devem:
- Mostrar últimos dados conhecidos (BehaviorSubject mantém valor)
- Exibir indicador de "stale data" se dados > 1min
- Não mostrar erro se endpoint é opcional

---

## Prioridades

1. **[Alta] Correção 2 - Wallet Auto-Select**: Resolve 400 mais frequente
2. **[Alta] Correção 3 - Health Check Robusto**: Garante status correto
3. **[Média] Correção 4 - Graceful Degradation**: Melhor UX
4. **[Baixa] Correção 1 - Isolamento**: Já implementado

## Comandos Úteis

```bash
# Verificar status do backend
curl http://localhost:8000/health

# Verificar logs backend
tail -f /tmp/backend.log

# Verificar status bitcoind
/home/lucas/research/bitcoincoders/bitcoin-31.0/bin/bitcoin-cli \
  -datadir=/home/lucas/research/bitcoincoders/btc-regtest-n1 getblockchaininfo

# Verificar logs frontend
tail -f /tmp/frontend.log
```

## Timeline

- Correção 2: 15 minutos
- Correção 3: 30 minutos
- Correção 4: 1 hora

**Total estimado: ~2 horas**
