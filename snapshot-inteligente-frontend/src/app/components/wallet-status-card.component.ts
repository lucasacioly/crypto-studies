import { Component, OnInit, OnDestroy, Input } from '@angular/core';
import { BitcoinApiService } from '../services/bitcoin-api.service';
import { WalletStatus } from '../models/wallet.model';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';

@Component({
  selector: 'app-wallet-status-card',
  templateUrl: './wallet-status-card.component.html',
  styleUrls: ['./wallet-status-card.component.scss']
})
export class WalletStatusCardComponent implements OnInit, OnDestroy {
  @Input() refreshInterval = 15000; // 15 seconds

  walletStatus: WalletStatus | null = null;
  isLoading = false;
  error: string | null = null;

  private destroy$ = new Subject<void>();

  constructor(private bitcoinApi: BitcoinApiService) {}

  ngOnInit(): void {
    this.loadWalletStatus();

    // Auto-refresh
    setInterval(() => {
      this.loadWalletStatus();
    }, this.refreshInterval);
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  loadWalletStatus(): void {
    this.isLoading = true;
    this.error = null;

    this.bitcoinApi
      .getWalletStatus()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (status: WalletStatus) => {
          this.walletStatus = status;
          this.isLoading = false;
        },
        error: (error: any) => {
          console.error('Error loading wallet status:', error);
          this.error = error.error?.detail || 'Failed to load wallet status';
          this.isLoading = false;
        }
      });
  }

  refresh(): void {
    this.loadWalletStatus();
  }
}
