import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { MempoolSummary } from '../models/mempool.model';
import { BlockchainLag } from '../models/blockchain.model';
import { BlockEvent, TransactionEvent, StateComparison, EventStats, EventSummary, LatestEvents } from '../models/events.model';
import { WalletListResponse, WalletSelectResponse, WalletStatus, TransactionDetail, TransactionCreateRequest, TransactionCreateResponse, TransactionSignRequest, TransactionSignResponse, TransactionBroadcastRequest, TransactionBroadcastResponse, UTXOListResponse, FeeEstimateResponse, SentTransaction, UTXO } from '../models/wallet.model';

@Injectable({
  providedIn: 'root'
})
export class BitcoinApiService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  // Task 1: Mempool & Blockchain
  getMempoolSummary(): Observable<MempoolSummary> {
    return this.http.get<MempoolSummary>(`${this.apiUrl}/mempool/summary`);
  }

  getBlockchainLag(): Observable<BlockchainLag> {
    return this.http.get<BlockchainLag>(`${this.apiUrl}/blockchain/lag`);
  }

  getHealth(): Observable<any> {
    return this.http.get('http://localhost:8000/health');
  }

  // Task 2: Event Streaming
  getEventSummary(): Observable<EventSummary> {
    return this.http.get<EventSummary>(`${this.apiUrl}/events/summary`);
  }

  getLatestEvents(limit: number = 10): Observable<LatestEvents> {
    const params = new HttpParams().set('limit', limit.toString());
    return this.http.get<LatestEvents>(`${this.apiUrl}/events/latest`, { params });
  }

  /**
   * Get recent block events from the buffer.
   * @param limit Number of blocks to return (1-50, default: 10)
   */
  getRecentBlocks(limit: number = 10): Observable<BlockEvent[]> {
    const params = new HttpParams().set('limit', limit.toString());
    return this.http.get<BlockEvent[]>(`${this.apiUrl}/events/blocks`, { params });
  }

  /**
   * Get recent transaction events from the buffer.
   * @param limit Number of transactions to return (1-100, default: 20)
   * @param feeCategory Optional filter by 'low', 'medium', or 'high'
   */
  getRecentTransactions(limit: number = 20, feeCategory?: string): Observable<TransactionEvent[]> {
    let params = new HttpParams().set('limit', limit.toString());
    if (feeCategory) {
      params = params.set('fee_category', feeCategory);
    }
    return this.http.get<TransactionEvent[]>(`${this.apiUrl}/events/transactions`, { params });
  }

  /**
   * Compare buffer state with live RPC to detect blockchain divergence.
   */
  getStateComparison(): Observable<StateComparison> {
    return this.http.get<StateComparison>(`${this.apiUrl}/events/state-comparison`);
  }

  /**
   * Get event buffer statistics and ZMQ listener status.
   */
  getEventStats(): Observable<EventStats> {
    return this.http.get<EventStats>(`${this.apiUrl}/events/stats`);
  }

  // Task 3: Multiple Wallets Support
  /**
   * List available and loaded wallets.
   */
  listWallets(): Observable<WalletListResponse> {
    return this.http.get<WalletListResponse>(`${this.apiUrl}/wallet/list`);
  }

  /**
   * Select a wallet for subsequent operations.
   * @param wallet Wallet name to select
   */
  selectWallet(wallet: string): Observable<WalletSelectResponse> {
    return this.http.post<WalletSelectResponse>(`${this.apiUrl}/wallet/select`, { wallet });
  }

  /**
   * Get current selected wallet status (balance and UTXOs).
   */
  getWalletStatus(): Observable<WalletStatus> {
    return this.http.get<WalletStatus>(`${this.apiUrl}/wallet/status`);
  }

  /**
   * Get detailed transaction information with interpretation.
   * @param txid Transaction ID
   */
  getTransactionDetail(txid: string): Observable<TransactionDetail> {
    return this.http.get<TransactionDetail>(`${this.apiUrl}/tx/${txid}`);
  }

  /**
   * Get available UTXOs for selected wallet.
   */
  getUTXOs(): Observable<UTXOListResponse> {
    return this.http.get<UTXOListResponse>(`${this.apiUrl}/tx/utxos`);
  }

  /**
   * Estimate transaction fee.
   * @param targetBlocks Target number of blocks (1-1008)
   */
  estimateFee(targetBlocks: number = 2): Observable<FeeEstimateResponse> {
    const params = new HttpParams().set('target_blocks', targetBlocks.toString());
    return this.http.get<FeeEstimateResponse>(`${this.apiUrl}/tx/estimate-fee`, { params });
  }

  /**
   * Create unsigned transaction.
   * @param request Transaction creation parameters
   */
  createTransaction(request: TransactionCreateRequest): Observable<TransactionCreateResponse> {
    return this.http.post<TransactionCreateResponse>(`${this.apiUrl}/tx/create`, request);
  }

  /**
   * Sign unsigned transaction.
   * @param request Unsigned transaction hex
   */
  signTransaction(request: TransactionSignRequest): Observable<TransactionSignResponse> {
    return this.http.post<TransactionSignResponse>(`${this.apiUrl}/tx/sign`, request);
  }

  /**
   * Broadcast signed transaction.
   * @param request Signed transaction hex
   */
  broadcastTransaction(request: TransactionBroadcastRequest): Observable<TransactionBroadcastResponse> {
    return this.http.post<TransactionBroadcastResponse>(`${this.apiUrl}/tx/broadcast`, request);
  }

  /**
   * Get history of sent transactions.
   */
  getSentTransactionHistory(): Observable<{ transactions: SentTransaction[] }> {
    return this.http.get<{ transactions: SentTransaction[] }>(`${this.apiUrl}/tx/sent-history`);
  }
}
