import { Component, OnDestroy } from '@angular/core';
import { WalletStatus } from '../models/wallet.model';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { DataPollingService } from '../services/data-polling.service';

@Component({
  selector: 'app-wallet-status-card',
  templateUrl: './wallet-status-card.component.html',
  styleUrls: ['./wallet-status-card.component.scss']
})
export class WalletStatusCardComponent implements OnDestroy {
  walletStatus: WalletStatus | null = null;
  isLoading = true;
  error: string | null = null;

  private destroy$ = new Subject<void>();

  constructor(private dataPolling: DataPollingService) {
    this.dataPolling.walletStatus$.pipe(takeUntil(this.destroy$)).subscribe({
      next: (status) => {
        this.walletStatus = status;
        this.isLoading = false;
        if (!status) {
          this.error = 'Nenhuma wallet selecionada';
        } else {
          this.error = null;
        }
      },
      error: (err) => {
        this.error = 'Erro ao carregar status da wallet';
        this.isLoading = false;
      }
    });
    
    this.dataPolling.refreshWalletStatus();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  refresh(): void {
    this.isLoading = true;
    this.dataPolling.refreshWalletStatus();
  }
}