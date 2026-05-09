import { Component, OnInit, OnDestroy } from '@angular/core';
import { forkJoin } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { Subject } from 'rxjs';
import { DataPollingService } from '../services/data-polling.service';
import { MempoolSummary } from '../models/mempool.model';
import { BlockchainLag } from '../models/blockchain.model';

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

  constructor(private dataPolling: DataPollingService) {}

  ngOnInit(): void {
    this.dataPolling.mempool$.pipe(takeUntil(this.destroy$)).subscribe(m => this.mempool = m);
    this.dataPolling.blockchainLag$.pipe(takeUntil(this.destroy$)).subscribe(b => {
      this.blockchain = b;
      this.loading = false;
    });
    this.dataPolling.health$.pipe(takeUntil(this.destroy$)).subscribe(c => {
      this.isConnected = c;
      if (c) {
        this.error = null;
      } else {
        this.error = 'Unable to connect to Bitcoin backend';
      }
    });
    this.lastUpdated = new Date();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  getRelativeTime(date: Date | null): string {
    if (!date) return '';
    const seconds = Math.floor((Date.now() - date.getTime()) / 1000);
    if (seconds < 60) return 'just now';
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    return `${Math.floor(minutes / 60)} hour${Math.floor(minutes / 60) > 1 ? 's' : ''} ago`;
  }

  onWalletSelected(wallet: string): void {
    console.log(`Wallet selected: ${wallet}`);
    this.dataPolling.refreshWalletStatus();
  }
}
