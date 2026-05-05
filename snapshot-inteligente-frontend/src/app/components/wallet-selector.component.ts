import { Component, OnInit, OnDestroy, EventEmitter, Output } from '@angular/core';
import { BitcoinApiService } from '../services/bitcoin-api.service';
import { WalletListResponse, WalletInfo } from '../models/wallet.model';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';

@Component({
  selector: 'app-wallet-selector',
  templateUrl: './wallet-selector.component.html',
  styleUrls: ['./wallet-selector.component.scss']
})
export class WalletSelectorComponent implements OnInit, OnDestroy {
  @Output() walletSelected = new EventEmitter<string>();

  availableWallets: string[] = [];
  selectedWallet: string | null | undefined = null;
  walletInfo: WalletInfo | null = null;
  isLoading = false;
  error: string | null = null;

  private destroy$ = new Subject<void>();

  constructor(private bitcoinApi: BitcoinApiService) {}

  ngOnInit(): void {
    this.loadWallets();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  loadWallets(): void {
    this.isLoading = true;
    this.error = null;

    this.bitcoinApi
      .listWallets()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response: WalletListResponse) => {
          this.availableWallets = response.available_wallets;
          this.selectedWallet = response.selected_wallet;

          // Auto-select if only one wallet exists
          if (this.availableWallets.length === 1 && !this.selectedWallet) {
            this.selectWallet(this.availableWallets[0]);
          }

          this.isLoading = false;
        },
        error: (error: any) => {
          console.error('Error loading wallets:', error);
          this.error = 'Failed to load wallets';
          this.isLoading = false;
        }
      });
  }

  selectWallet(wallet: string): void {
    if (wallet === this.selectedWallet) return;

    this.isLoading = true;
    this.error = null;

    this.bitcoinApi
      .selectWallet(wallet)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response) => {
          this.selectedWallet = response.selected_wallet as any;
          this.walletInfo = response.wallet_info;
          this.walletSelected.emit(wallet);
          this.isLoading = false;
        },
        error: (error: any) => {
          console.error('Error selecting wallet:', error);
          this.error = `Failed to select wallet: ${error.error?.detail || 'Unknown error'}`;
          this.isLoading = false;
        }
      });
  }

  getStatusColor(): string {
    if (!this.selectedWallet) return 'warning';
    return 'success';
  }

  getStatusIcon(): string {
    if (!this.selectedWallet) return '⚠️';
    return '✅';
  }
}
