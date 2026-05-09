# Relatório de Defeitos e Plano de Correção

## Data: 2026-05-09

---

## Defeito 1: "Unable to connect to Bitcoin backend" persiste mesmo quando status é "Connected"

### Sintoma
- Indicador visual mostra "Connected" (verde)
- Mensagem de erro "Unable to connect to Bitcoin backend" ainda é exibida

### Análise

**Causa Raiz:** O erro nunca é limpo após ser setado.

Em `dashboard.component.ts:32-35`:
```typescript
this.dataPolling.health$.subscribe(c => {
  this.isConnected = c;
  if (!c) this.error = 'Unable to connect to Bitcoin backend';
  // ↑ Missing: if (c) this.error = null;
});
```

Uma vez que `error` é setado, permanece para sempre porque a condição só atribui quando `!c`.

**Causa Secundária:** O `forkJoin` no `DataPollingService` pode falhar se qualquer endpoint retornar erro, fazendo `healthSubject.next(false)` mesmo quando o backend está ok.

### Solução

1. Limpar `error` quando `isConnected = true`
2. Separar health check de endpoints de dados para não quebrar health quando outros endpoints falham

---

## Defeito 2: Seleção dinâmica de wallet não atualiza componente de Status

### Sintoma
- Usuário seleciona outro wallet no selector
- Componente `wallet-status-card` não atualiza imediatamente
- Leva até 15 segundos para mostrar novo balance

### Análise

**Causa Raiz:** Não há mecanismo de refresh imediato após seleção de wallet.

Fluxo atual:
```
selectWallet() → POST /wallet/select → emit walletSelected
                                         ↓
                              onWalletSelected() → console.log() ← Não faz nada
                                         ↓
                              walletStatus$ só atualiza no próximo poll (15s)
```

O evento `walletSelected` é emitido mas:
1. `onWalletSelected` apenas loga no console
2. `DataPollingService` não é notificado para refresh imediato
3. Próximo poll pode demorar até 15 segundos

### Solução

Adicionar método `refreshWalletStatus()` no `DataPollingService` que força refresh imediato do `walletStatusSubject` após seleção de wallet.

---

## Plano de Correção

### [x] Correção 1: Limpar erro quando conectado

**Arquivo:** `src/app/components/dashboard.component.ts`

```typescript
this.dataPolling.health$.subscribe(c => {
  this.isConnected = c;
  if (c) {
    this.error = null;
  } else {
    this.error = 'Unable to connect to Bitcoin backend';
  }
});
```

### [x] Correção 2: Refresh imediato de wallet status

**Arquivo:** `src/app/services/data-polling.service.ts`

Adicionar método:
```typescript
refreshWalletStatus(): void {
  this.http.get<WalletStatus>(`${this.apiUrl}/wallet/status`)
    .pipe(catchError(() => of(null)))
    .subscribe(status => this.walletStatusSubject.next(status));
}
```

**Arquivo:** `src/app/components/dashboard.component.ts`

Atualizar `onWalletSelected`:
```typescript
onWalletSelected(wallet: string): void {
  console.log(`Wallet selected: ${wallet}`);
  this.dataPolling.refreshWalletStatus();
}
```

---

## Prioridades

1. **[Alta] Correção 1** — Resolve "Unable to connect" fantasma
2. **[Alta] Correção 2** — Resolve latência de seleção de wallet

## Tempo Estimado

15 minutos para implementar ambas correções.
