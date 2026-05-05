import { Component, OnInit, OnDestroy } from '@angular/core';
import { BitcoinApiService } from '../services/bitcoin-api.service';
import { BlockEvent, TransactionEvent, EventStats } from '../models/events.model';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';

@Component({
  selector: 'app-event-activity-card',
  templateUrl: './event-activity-card.component.html',
  styleUrls: ['./event-activity-card.component.scss']
})
export class EventActivityCardComponent implements OnInit, OnDestroy {
  // Data
  recentBlocks: BlockEvent[] = [];
  recentTransactions: TransactionEvent[] = [];
  eventStats: EventStats | null = null;

  // UI State
  isLoading = false;
  error: string | null = null;
  zmqStatus: 'connected' | 'disconnected' = 'disconnected';
  bufferFillBlocks = 0;
  bufferFillTransactions = 0;

  // Refresh
  refreshInterval = 15000; // 15 seconds
  private destroy$ = new Subject<void>();

  constructor(private bitcoinApi: BitcoinApiService) {}

  ngOnInit(): void {
    // Initial load
    this.loadEventData();

    // Auto-refresh
    setInterval(() => {
      this.loadEventData();
    }, this.refreshInterval);
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  /**
   * Load event data from API
   */
  private loadEventData(): void {
    this.isLoading = true;
    this.error = null;

    // Load recent blocks
    this.bitcoinApi.getRecentBlocks(10)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (blocks: BlockEvent[]) => {
          this.recentBlocks = blocks;
        },
        error: (error: any) => {
          console.error('Error fetching recent blocks:', error);
          this.error = 'Failed to fetch recent blocks';
        }
      });

    // Load recent transactions
    this.bitcoinApi.getRecentTransactions(20)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (txs: TransactionEvent[]) => {
          this.recentTransactions = txs;
        },
        error: (error: any) => {
          console.error('Error fetching recent transactions:', error);
        }
      });

    // Load event stats
    this.bitcoinApi.getEventStats()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (stats: EventStats) => {
          this.eventStats = stats;
          this.zmqStatus = stats.zmq_listener_status;
          
          // Calculate buffer fill percentages
          this.bufferFillBlocks = (stats.buffer_blocks_count / stats.buffer_blocks_capacity) * 100;
          this.bufferFillTransactions = (stats.buffer_transactions_count / stats.buffer_transactions_capacity) * 100;
          
          this.isLoading = false;
        },
        error: (error: any) => {
          console.error('Error fetching event stats:', error);
          this.isLoading = false;
        }
      });
  }

  /**
   * Format timestamp to relative time
   */
  getRelativeTime(timestamp: string): string {
    const date = new Date(timestamp);
    const now = new Date();
    const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (seconds < 60) return `${seconds}s ago`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return date.toLocaleDateString();
  }

  /**
   * Truncate hash to first 16 characters for display
   */
  truncateHash(hash: string, length: number = 16): string {
    return hash.substring(0, length) + '...';
  }

  /**
   * Get CSS class for buffer fill level
   */
  getBufferFillClass(percentage: number): string {
    if (percentage < 25) return 'fill-low';
    if (percentage < 50) return 'fill-medium';
    if (percentage < 75) return 'fill-medium-high';
    return 'fill-high';
  }

  /**
   * Get status indicator color
   */
  getStatusColor(): string {
    if (this.zmqStatus === 'connected') return 'success';
    return 'warning';
  }

  /**
   * Manual refresh
   */
  refresh(): void {
    this.loadEventData();
  }
}
