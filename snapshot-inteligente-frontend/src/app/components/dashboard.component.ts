import { Component, OnInit, OnDestroy } from '@angular/core';
import { BitcoinApiService } from '../services/bitcoin-api.service';
import { MempoolSummary } from '../models/mempool.model';
import { BlockchainLag } from '../models/blockchain.model';
import { Subject, interval, takeUntil, switchMap } from 'rxjs';
import { forkJoin } from 'rxjs';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit, OnDestroy {
  mempool: MempoolSummary | null = null;
  blockchain: BlockchainLag | null = null;
  loading = true;
  error: string | null = null;
  isConnected = false;
  lastUpdated: Date | null = null;

  private destroy$ = new Subject<void>();

  constructor(private bitcoinApi: BitcoinApiService) {}

  ngOnInit(): void {
    this.loadData();
    this.startAutoRefresh();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  loadData(): void {
    this.loading = true;
    this.error = null;

    this.bitcoinApi.getHealth().pipe(takeUntil(this.destroy$)).subscribe({
      next: () => {
        this.isConnected = true;
        this.fetchMempoolAndBlockchain();
      },
      error: (err) => {
        this.isConnected = false;
        this.error = 'Unable to connect to Bitcoin backend';
        this.loading = false;
      }
    });
  }

  private fetchMempoolAndBlockchain(): void {
    forkJoin([
      this.bitcoinApi.getMempoolSummary(),
      this.bitcoinApi.getBlockchainLag()
    ]).pipe(takeUntil(this.destroy$)).subscribe({
      next: ([mempoolData, blockchainData]) => {
        this.mempool = mempoolData;
        this.blockchain = blockchainData;
        this.lastUpdated = new Date();
        this.loading = false;
      },
      error: (err) => {
        console.error('Error fetching data:', err);
        this.error = 'Failed to fetch blockchain data';
        this.loading = false;
      }
    });
  }

  private startAutoRefresh(): void {
    interval(15000)
      .pipe(
        switchMap(() => {
          this.loadData();
          return [];
        }),
        takeUntil(this.destroy$)
      )
      .subscribe();
  }

  getRelativeTime(date: Date | null): string {
    if (!date) return '';
    const seconds = Math.floor((Date.now() - date.getTime()) / 1000);
    if (seconds < 60) return 'just now';
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    return `${Math.floor(minutes / 60)} hour${Math.floor(minutes / 60) > 1 ? 's' : ''} ago`;
  }
}
