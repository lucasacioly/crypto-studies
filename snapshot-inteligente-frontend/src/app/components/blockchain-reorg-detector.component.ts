import { Component, OnInit, OnDestroy } from '@angular/core';
import { BitcoinApiService } from '../services/bitcoin-api.service';
import { StateComparison } from '../models/events.model';
import { Subject, interval } from 'rxjs';
import { takeUntil, switchMap } from 'rxjs/operators';

@Component({
  selector: 'app-blockchain-reorg-detector',
  templateUrl: './blockchain-reorg-detector.component.html',
  styleUrls: ['./blockchain-reorg-detector.component.scss']
})
export class BlockchainReorgDetectorComponent implements OnInit, OnDestroy {
  stateComparison: StateComparison | null = null;
  isLoading = false;
  error: string | null = null;
  refreshInterval = 30000; // 30 seconds (less frequent to avoid rate limiting)

  private destroy$ = new Subject<void>();

  constructor(private bitcoinApi: BitcoinApiService) {}

  ngOnInit(): void {
    this.loadStateComparison();

    // Auto-refresh every 30 seconds
    interval(this.refreshInterval)
      .pipe(
        switchMap(() => {
          this.loadStateComparison();
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

  /**
   * Load state comparison from API
   */
  private loadStateComparison(): void {
    this.isLoading = true;
    this.error = null;

    this.bitcoinApi.getStateComparison()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (comparison: StateComparison) => {
          this.stateComparison = comparison;
          this.isLoading = false;
        },
        error: (error: any) => {
          console.error('Error fetching state comparison:', error);
          this.error = 'Failed to fetch state comparison';
          this.isLoading = false;
        }
      });
  }

  /**
   * Get status color based on divergence
   */
  getStatusColor(): string {
    if (!this.stateComparison) return 'default';
    if (!this.stateComparison.buffer_latest_block) return 'waiting';
    return this.stateComparison.divergence_detected ? 'warning' : 'success';
  }

  /**
   * Get status icon
   */
  getStatusIcon(): string {
    if (!this.stateComparison) return '❓';
    if (!this.stateComparison.buffer_latest_block) return '⏳';
    return this.stateComparison.divergence_detected ? '⚠️' : '✅';
  }

  /**
   * Get status text
   */
  getStatusText(): string {
    if (!this.stateComparison) return 'Unknown';
    if (!this.stateComparison.buffer_latest_block) return 'WAITING FOR EVENTS';
    return this.stateComparison.divergence_detected ? 'DIVERGENCE DETECTED' : 'SYNCED';
  }

  /**
   * Manual refresh
   */
  refresh(): void {
    this.loadStateComparison();
  }

  /**
   * Truncate hash for display
   */
  truncateHash(hash: string, length: number = 16): string {
    return hash.substring(0, length) + '...';
  }
}
