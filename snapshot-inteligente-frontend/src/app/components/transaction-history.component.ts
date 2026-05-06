import { Component, OnInit, OnDestroy } from '@angular/core';
import { BitcoinApiService } from '../services/bitcoin-api.service';
import { SentTransaction } from '../models/wallet.model';
import { Subject, interval } from 'rxjs';
import { takeUntil, switchMap } from 'rxjs/operators';

@Component({
  selector: 'app-transaction-history',
  templateUrl: './transaction-history.component.html',
  styleUrls: ['./transaction-history.component.scss']
})
export class TransactionHistoryComponent implements OnInit, OnDestroy {
  transactions: SentTransaction[] = [];
  isLoading = false;
  error: string | null = null;
  displayedColumns = ['date', 'recipient', 'amount', 'fee', 'status', 'action'];

  private destroy$ = new Subject<void>();

  constructor(private bitcoinApi: BitcoinApiService) {}

  ngOnInit(): void {
    this.loadHistory();
    // Auto-refresh every 30 seconds
    interval(30000)
      .pipe(
        switchMap(() => {
          this.loadHistory();
          return [];
        }),
        takeUntil(this.destroy$)
      )
      .subscribe();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  loadHistory(): void {
    this.isLoading = true;
    this.error = null;

    this.bitcoinApi
      .getSentTransactionHistory()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response) => {
          this.transactions = response.transactions.sort((a, b) => 
            new Date(b.broadcast_at).getTime() - new Date(a.broadcast_at).getTime()
          );
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Error loading history:', error);
          this.error = error.error?.detail || 'Failed to load transaction history';
          this.isLoading = false;
        }
      });
  }

  getStatusColor(status: string): string {
    switch (status) {
      case 'broadcast':
        return 'warning';
      case 'confirmed':
        return 'success';
      case 'failed':
        return 'error';
      default:
        return 'info';
    }
  }

  getStatusIcon(status: string): string {
    switch (status) {
      case 'broadcast':
        return '⏳';
      case 'confirmed':
        return '✅';
      case 'failed':
        return '❌';
      default:
        return '❓';
    }
  }

  formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleString();
  }

  copyToClipboard(text: string): void {
    navigator.clipboard.writeText(text).then(() => {
      console.log('Copied to clipboard');
    });
  }

  refresh(): void {
    this.loadHistory();
  }
}
