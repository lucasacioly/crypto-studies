import { Component, OnInit, OnDestroy } from '@angular/core';
import { BlockEvent, TransactionEvent, EventStats } from '../models/events.model';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { DataPollingService } from '../services/data-polling.service';

@Component({
  selector: 'app-event-activity-card',
  templateUrl: './event-activity-card.component.html',
  styleUrls: ['./event-activity-card.component.scss']
})
export class EventActivityCardComponent implements OnInit, OnDestroy {
  recentBlocks: BlockEvent[] = [];
  recentTransactions: TransactionEvent[] = [];
  eventStats: EventStats | null = null;
  isLoading = false;
  error: string | null = null;
  zmqStatus: 'connected' | 'disconnected' = 'disconnected';
  bufferFillBlocks = 0;
  bufferFillTransactions = 0;

  private destroy$ = new Subject<void>();

  constructor(private dataPolling: DataPollingService) {}

  ngOnInit(): void {
    this.dataPolling.recentBlocks$.pipe(takeUntil(this.destroy$)).subscribe(blocks => {
      this.recentBlocks = blocks;
    });

    this.dataPolling.recentTransactions$.pipe(takeUntil(this.destroy$)).subscribe(txs => {
      this.recentTransactions = txs;
    });

    this.dataPolling.eventStats$.pipe(takeUntil(this.destroy$)).subscribe(stats => {
      if (stats) {
        this.eventStats = stats;
        this.zmqStatus = stats.zmq_listener_status;
        this.bufferFillBlocks = (stats.buffer_blocks_count / stats.buffer_blocks_capacity) * 100;
        this.bufferFillTransactions = (stats.buffer_transactions_count / stats.buffer_transactions_capacity) * 100;
        this.isLoading = false;
      }
    });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  getRelativeTime(timestamp: string): string {
    const date = new Date(timestamp);
    const now = new Date();
    const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);
    if (seconds < 60) return `${seconds}s ago`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return date.toLocaleDateString();
  }

  truncateHash(hash: string, length: number = 16): string {
    return hash.substring(0, length) + '...';
  }

  getBufferFillClass(percentage: number): string {
    if (percentage < 25) return 'fill-low';
    if (percentage < 50) return 'fill-medium';
    if (percentage < 75) return 'fill-medium-high';
    return 'fill-high';
  }

  getStatusColor(): string {
    if (this.zmqStatus === 'connected') return 'success';
    return 'warning';
  }

  refresh(): void {}
}
