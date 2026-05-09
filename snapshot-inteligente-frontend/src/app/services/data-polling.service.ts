import { Injectable, OnDestroy } from '@angular/core';
import { BehaviorSubject, interval, Subscription, forkJoin, Subject, of } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { catchError, takeUntil } from 'rxjs/operators';
import { MempoolSummary } from '../models/mempool.model';
import { BlockchainLag } from '../models/blockchain.model';
import { BlockEvent, TransactionEvent, EventStats, LatestEvents, StateComparison } from '../models/events.model';
import { WalletStatus, SentTransaction } from '../models/wallet.model';

@Injectable({
  providedIn: 'root'
})
export class DataPollingService implements OnDestroy {
  private readonly POLL_INTERVAL = 15000;
  private stop$ = new Subject<void>();
  private pollSub: Subscription | null = null;

  private healthSubject = new BehaviorSubject<boolean>(false);
  private mempoolSubject = new BehaviorSubject<MempoolSummary | null>(null);
  private blockchainLagSubject = new BehaviorSubject<BlockchainLag | null>(null);
  private walletStatusSubject = new BehaviorSubject<WalletStatus | null>(null);
  private recentBlocksSubject = new BehaviorSubject<BlockEvent[]>([]);
  private recentTransactionsSubject = new BehaviorSubject<TransactionEvent[]>([]);
  private eventStatsSubject = new BehaviorSubject<EventStats | null>(null);
  private latestEventsSubject = new BehaviorSubject<LatestEvents | null>(null);
  private stateComparisonSubject = new BehaviorSubject<StateComparison | null>(null);
  private sentTransactionsSubject = new BehaviorSubject<SentTransaction[]>([]);

  health$ = this.healthSubject.asObservable();
  mempool$ = this.mempoolSubject.asObservable();
  blockchainLag$ = this.blockchainLagSubject.asObservable();
  walletStatus$ = this.walletStatusSubject.asObservable();
  recentBlocks$ = this.recentBlocksSubject.asObservable();
  recentTransactions$ = this.recentTransactionsSubject.asObservable();
  eventStats$ = this.eventStatsSubject.asObservable();
  latestEvents$ = this.latestEventsSubject.asObservable();
  stateComparison$ = this.stateComparisonSubject.asObservable();
  sentTransactions$ = this.sentTransactionsSubject.asObservable();

  private apiUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) {
    this.startPolling();
  }

  private startPolling(): void {
    this.pollAll();
    this.pollSub = interval(this.POLL_INTERVAL)
      .pipe(takeUntil(this.stop$))
      .subscribe(() => this.pollAll());
  }

  private req<T>(url: string): any {
    return this.http.get<T>(url).pipe(catchError(() => of(null as any)));
  }

  private pollAll(): void {
    forkJoin({
      health: this.req<any>(`${this.apiUrl}/health`),
      mempool: this.req<MempoolSummary>(`${this.apiUrl}/mempool/summary`),
      blockchainLag: this.req<BlockchainLag>(`${this.apiUrl}/blockchain/lag`),
      walletStatus: this.req<WalletStatus>(`${this.apiUrl}/wallet/status`),
      recentBlocks: this.req<BlockEvent[]>(`${this.apiUrl}/events/blocks?limit=10`),
      recentTransactions: this.req<TransactionEvent[]>(`${this.apiUrl}/events/transactions?limit=20`),
      eventStats: this.req<EventStats>(`${this.apiUrl}/events/stats`),
      latestEvents: this.req<LatestEvents>(`${this.apiUrl}/events/latest?limit=10`),
      stateComparison: this.req<StateComparison>(`${this.apiUrl}/events/state-comparison`),
      sentTransactions: this.req<any>(`${this.apiUrl}/tx/sent-history`)
    }).subscribe({
      next: (data: any) => {
        this.healthSubject.next(data.health?.rpc === 'connected');
        this.mempoolSubject.next(data.mempool);
        this.blockchainLagSubject.next(data.blockchainLag);
        this.walletStatusSubject.next(data.walletStatus);
        this.recentBlocksSubject.next(data.recentBlocks || []);
        this.recentTransactionsSubject.next(data.recentTransactions || []);
        this.eventStatsSubject.next(data.eventStats);
        this.latestEventsSubject.next(data.latestEvents);
        this.stateComparisonSubject.next(data.stateComparison);
        this.sentTransactionsSubject.next(data.sentTransactions?.transactions || []);
      },
      error: () => {
        this.healthSubject.next(false);
      }
    });
  }

  refreshWalletStatus(): void {
    this.http.get<WalletStatus>(`${this.apiUrl}/wallet/status`)
      .pipe(catchError(() => of(null as any)))
      .subscribe(status => this.walletStatusSubject.next(status));
  }

  ngOnDestroy(): void {
    this.stop$.next();
    this.stop$.complete();
    if (this.pollSub) {
      this.pollSub.unsubscribe();
    }
  }
}
