import { Component, OnInit, OnDestroy } from '@angular/core';
import { BitcoinApiService } from '../services/bitcoin-api.service';
import { FeeEstimateResponse, TransactionCreateResponse, UTXO } from '../models/wallet.model';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';

@Component({
  selector: 'app-send-transaction',
  templateUrl: './send-transaction.component.html',
  styleUrls: ['./send-transaction.component.scss']
})
export class SendTransactionComponent implements OnInit, OnDestroy {
  // Form inputs
  recipient: string = '';
  amountBTC: number = 0;
  selectedFeeRate: number = 5.0;
  utxoSelectionMode: 'automatic' | 'manual' = 'automatic';
  selectedUTXOIndices: Set<number> = new Set();

  // UI states
  step: 'form' | 'preview' | 'signing' | 'broadcasting' | 'success' = 'form';
  isLoading = false;
  error: string | null = null;
  successMessage: string | null = null;

  // Data
  availableUTXOs: UTXO[] = [];
  estimatedFee: FeeEstimateResponse | null = null;
  transactionPreview: TransactionCreateResponse | null = null;
  broadcastTxid: string | null = null;

  // UI flags
  showUTXOSelector = false;
  manualFeeInput: number = 5.0;

  private destroy$ = new Subject<void>();

  constructor(private bitcoinApi: BitcoinApiService) {}

  ngOnInit(): void {
    this.loadUTXOs();
    this.estimateFeeRate();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  loadUTXOs(): void {
    this.isLoading = true;
    this.error = null;

    this.bitcoinApi
      .getUTXOs()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response) => {
          this.availableUTXOs = response.utxos;
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Error loading UTXOs:', error);
          this.error = error.error?.detail || 'Failed to load UTXOs';
          this.isLoading = false;
        }
      });
  }

  estimateFeeRate(): void {
    this.bitcoinApi
      .estimateFee(2)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response) => {
          this.estimatedFee = response;
          this.selectedFeeRate = response.fee_rate_sat_vB;
          this.manualFeeInput = response.fee_rate_sat_vB;
        },
        error: (error) => {
          console.warn('Fee estimation failed, using default:', error);
          this.selectedFeeRate = 5.0;
          this.manualFeeInput = 5.0;
        }
      });
  }

  toggleUTXOSelector(): void {
    this.showUTXOSelector = !this.showUTXOSelector;
  }

  toggleUTXO(index: number): void {
    if (this.selectedUTXOIndices.has(index)) {
      this.selectedUTXOIndices.delete(index);
    } else {
      this.selectedUTXOIndices.add(index);
    }
  }

  selectAllUTXOs(): void {
    this.selectedUTXOIndices = new Set(this.availableUTXOs.map((_, i) => i));
  }

  deselectAllUTXOs(): void {
    this.selectedUTXOIndices.clear();
  }

  getTotalSelectedAmount(): number {
    let total = 0;
    this.selectedUTXOIndices.forEach((idx) => {
      if (idx < this.availableUTXOs.length) {
        total += this.availableUTXOs[idx].amount_btc;
      }
    });
    return total;
  }

  validateForm(): string | null {
    if (!this.recipient.trim()) {
      return 'Recipient address is required';
    }
    if (this.amountBTC <= 0) {
      return 'Amount must be greater than 0';
    }
    if (this.selectedFeeRate <= 0) {
      return 'Fee rate must be greater than 0';
    }
    if (this.utxoSelectionMode === 'manual' && this.selectedUTXOIndices.size === 0) {
      return 'Manual mode requires selecting at least one UTXO';
    }
    return null;
  }

  async createTransaction(): Promise<void> {
    const validationError = this.validateForm();
    if (validationError) {
      this.error = validationError;
      return;
    }

    this.isLoading = true;
    this.error = null;

    const request: any = {
      recipient: this.recipient.trim(),
      amount_btc: this.amountBTC,
      fee_rate_sat_vB: this.selectedFeeRate,
      utxo_selection_mode: this.utxoSelectionMode
    };

    if (this.utxoSelectionMode === 'manual') {
      request.selected_utxo_indices = Array.from(this.selectedUTXOIndices);
    }

    this.bitcoinApi
      .createTransaction(request)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response) => {
          this.transactionPreview = response;
          this.step = 'preview';
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Error creating transaction:', error);
          this.error = error.error?.detail || 'Failed to create transaction';
          this.isLoading = false;
        }
      });
  }

  async confirmAndSign(): Promise<void> {
    if (!this.transactionPreview) {
      this.error = 'No transaction to sign';
      return;
    }

    this.isLoading = true;
    this.error = null;
    this.step = 'signing';

    this.bitcoinApi
      .signTransaction({ tx_hex: this.transactionPreview.tx_hex })
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response) => {
          if (!response.complete) {
            this.error = `Signing incomplete. Errors: ${response.errors.join(', ')}`;
            this.step = 'preview';
            this.isLoading = false;
            return;
          }

          // Now broadcast
          this.broadcastSigned(response.tx_hex);
        },
        error: (error) => {
          console.error('Error signing transaction:', error);
          this.error = error.error?.detail || 'Failed to sign transaction';
          this.step = 'preview';
          this.isLoading = false;
        }
      });
  }

  private broadcastSigned(signedTxHex: string): void {
    this.step = 'broadcasting';

    this.bitcoinApi
      .broadcastTransaction({
        tx_hex: signedTxHex,
        recipient: this.recipient,
        amount_btc: this.amountBTC,
        fee_sat: this.transactionPreview?.estimated_fee_sat || 0
      })
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response) => {
          this.broadcastTxid = response.txid;
          this.successMessage = `Transaction broadcast successfully! TXID: ${response.txid}`;
          this.step = 'success';
          this.isLoading = false;
          this.resetForm();
        },
        error: (error) => {
          console.error('Error broadcasting transaction:', error);
          this.error = error.error?.detail || 'Failed to broadcast transaction';
          this.step = 'preview';
          this.isLoading = false;
        }
      });
  }

  resetForm(): void {
    this.recipient = '';
    this.amountBTC = 0;
    this.selectedFeeRate = this.estimatedFee?.fee_rate_sat_vB || 5.0;
    this.utxoSelectionMode = 'automatic';
    this.selectedUTXOIndices.clear();
    this.showUTXOSelector = false;
    this.transactionPreview = null;
    this.broadcastTxid = null;
    this.step = 'form';
    this.error = null;
    this.loadUTXOs();
  }

  goBack(): void {
    this.step = 'form';
    this.error = null;
  }

  closeSuccess(): void {
    this.successMessage = null;
  }
}
