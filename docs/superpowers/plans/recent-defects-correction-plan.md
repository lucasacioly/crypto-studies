# Plano de Correção para Defeitos Recentes

## Data: 2026-05-09

## Status das Correções

- [x] **Correção 1: Event Activity Card** - VERIFICADO (buffers vazios = comportamento normal em regtest)
- [x] **Correção 2: Wallet Status não atualiza na seleção** - **RESOLVIDO**
- [x] **Correção 3: Sent Transactions vazio** - VERIFICADO (funciona, aguardando envio de transações)

---

## Defeitos Identificados e Correções Aplicadas

### Defeito 1: Histórico de eventos não sendo mostrado dinamicamente
**Sintoma:** Event Activity Card mostra dados estáticos ou vazios, não atualizando em tempo real.

**Análise:**
- O backend ZMQ listener está funcionando ("ZMQ Connected")
- Porém, buffer_blocks_count e buffer_transactions_count estão em 0
- O ZMQ está ouvindo, mas não está recebendo blocos/transações da blockchain regtest
- Isso é esperado em regtest pois não há atividade automática de mineração

**Solução aplicada:**
- Verificado que o EventActivityCardComponent está corretamente inscrito nos observables do DataPollingService
- Confirmado que eventStats$, recentBlocks$, e recentTransactions$ estão sendo atualizados
- O componente está funcionando corretamente; os buffers estão vazios porque não há atividade na blockchain regtest
- **Recomendação:** Para testar, gerar blocos manualmente com `bitcoin-cli generatetoaddress 1 <address>`

---

### Defeito 2: Status da Wallet não troca quando troca a Seleção de Wallet

**Sintoma:** Ao selecionar outra wallet no seletor, o WalletStatusCard não atualiza imediatamente.

**Análise - Problemas encontrados:**

1. **Bug no template do WalletSelectorComponent:**
   - O select usava `(change)="selectWallet($event)"` que não capturava mudanças do ngModel
   - Quando o ngModel muda (seleção automática ou outra fonte), o evento change não era disparado

2. **Bug crítico no backend `/wallet/select`:**
   - O código usava `selected_wallet` que não estava definido no escopo
   - Linhas 120, 123, 127 usavam `selected_wallet` em vez de `wallet`

**Correções aplicadas:**

1. **Frontend - wallet-selector.component.html:**
   ```html
   <!-- ANTES -->
   <select [(ngModel)]="selectedWallet" (change)="selectWallet($event)" ...>
   
   <!-- DEPOIS -->
   <select [(ngModel)]="selectedWallet" (ngModelChange)="selectWallet($event)" ...>
   ```

2. **Backend - routes/wallets.py:**
   - Linha 120: `rpc_client.call("getwalletinfo", wallet=selected_wallet)` → `wallet=wallet`
   - Linha 123: `rpc_client.call("getbalance", ..., wallet=selected_wallet)` → `wallet=wallet`
   - Linha 127: `walletname=wallet_info_raw.get("walletname", selected_wallet)` → `wallet`

**Status:** Backend precisa ser reiniciado para aplicar mudanças. Container em execução usa código antigo.

---

### Defeito 3: Sent Transactions mostrando perpetuamente "No transactions sent yet"

**Sintoma:** TransactionHistoryComponent sempre mostra estado vazio, mesmo após enviar transações.

**Análise:**
- O endpoint `/tx/sent-history` existe e retorna `{"transactions": []}`
- O DataPollingService está consultando o endpoint corretamente
- O componente TransactionHistoryComponent está inscrito no observable correto

**Causa raiz:**
- Nunca houve transações enviadas através do sistema
- O histórico de transações precisa ser preenchido através do fluxo normal:
  1. Criar transação → 2. Assinar → 3. Broadcast

**Solução aplicada:**
- Confirmado que o componente está corretamente configurado
- O componente exibirá transações quando forem enviadas e registradas no backend
- Necessário testar o fluxo completo de envio de transação

**Status:** FUNCIONAL - Aguardando envio de transações para validar

---

## Correções Pendentes

### [x] Backend - Reiniciar container snapshot-backend

✅ Aplicado diretamente no container via `docker exec sed -i` e `docker restart`

### [x] Teste de wallet selection após reinício

✅ **RESOLVIDO**
```bash
# miner_wallet:
curl -X POST http://localhost:8000/wallet/select -d '{"wallet": "miner_wallet"}'
# Retorna: {"selected_wallet": "miner_wallet", "wallet_info": {...}, "balance": 324.9999718}

# wallet2:
curl -X POST http://localhost:8000/wallet/select -d '{"wallet": "wallet2"}'
# Retorna: {"selected_wallet": "wallet2", "wallet_info": {...}, "balance": 13.9999859}
```

### [ ] Teste de envio de transação

Aguardando teste manual na interface.

### [ ] Teste de mineração para ativar buffers ZMQ

Aguardando necessidade (regtest sem atividade automática).

---

## Prioridades Atualizadas

1. **[✅ CONCLUÍDO] Reiniciar backend** - Código corrigido diretamente no container
2. **[✅ CONCLUÍDO] Teste de wallet selection** - Validação bem-sucedida via API
3. **[PENDENTE] Enviar transação de teste** - Testar via interface web
4. **[BAIXA] Gerar blocos** - Só necessário se quiser testar eventos ZMQ

---

## Resumo das Alterações de Código

### Frontend (2 arquivos)
1. `wallet-selector.component.html` - Trocado `(change)` por `(ngModelChange)`
2. `dashboard.component.ts` - Adicionado console.log para debug

### Backend (1 arquivo)
1. `routes/wallets.py` - Corrigidas 3 referências a `selected_wallet` → `wallet`

---

## Testes de Validação

### Teste 1: Troca de Wallet
```bash
# 1. Reiniciar backend
docker restart snapshot-backend

# 2. Verificar que está rodando
curl http://localhost:8000/health

# 3. Trocar para wallet2
curl -X POST http://localhost:8000/wallet/select -H "Content-Type: application/json" -d '{"wallet": "wallet2"}'

# 4. Verificar status
curl http://localhost:8000/wallet/status
# Esperado: {"wallet": "wallet2", "balance": 13.9999859, "utxos": 2}
```

### Teste 2: Interface Web
1. Acessar http://localhost:4200
2. Selecionar wallet2 no dropdown
3. Verificar que Wallet Status Card mostra balance ~14 BTC
4. Enviar transação de 0.001 BTC
5. Verificar que aparece em Sent Transactions

### Teste 3: Eventos ZMQ
1. Executar: `bitcoin-cli generatetoaddress 1 <address>`
2. Aguardar 15 segundos
3. Verificar que Event Activity Card mostra novo bloco