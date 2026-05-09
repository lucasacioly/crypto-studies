import { Component, OnInit, OnDestroy } from '@angular/core';
import { SentTransaction } from '../models/wallet.model';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { DataPollingService } from '../services/data-polling.service';

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

  constructor(private dataPolling: DataPollingService) {}

  ngOnInit(): void {
    this.dataPolling.sentTransactions$.pipe(takeUntil(this.destroy$)).subscribe(txs => {
      this.transactions = [...txs].sort((a, b) =>
        new Date(b.broadcast_at).getTime() - new Date(a.broadcast_at).getTime()
      );
      this.isLoading = false;
    });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  getStatusColor(status: string): string {
    switch (status) {
      case 'broadcast': return 'warning';
      case 'confirmed': return 'success';
      case 'failed': return 'error';
      default: return 'info';
    }
  }

  getStatusIcon(status: string): string {
    switch (status) {
      case 'broadcast': return '⏳';
      case 'confirmed': return '✅';
      case 'failed': return '❌';
      default: return '?';
    }
  }

  formatDate(dateString: string): string {
    return new Date(dateString).toLocaleString();
  }

  copyToClipboard(text: string): void {
    navigator.clipboard.writeText(text);
  }

  refresh(): void {}
}
