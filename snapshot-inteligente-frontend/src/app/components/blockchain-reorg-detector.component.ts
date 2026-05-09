import { Component, OnInit, OnDestroy } from '@angular/core';
import { StateComparison } from '../models/events.model';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { DataPollingService } from '../services/data-polling.service';

@Component({
  selector: 'app-blockchain-reorg-detector',
  templateUrl: './blockchain-reorg-detector.component.html',
  styleUrls: ['./blockchain-reorg-detector.component.scss']
})
export class BlockchainReorgDetectorComponent implements OnInit, OnDestroy {
  stateComparison: StateComparison | null = null;
  isLoading = false;
  error: string | null = null;

  private destroy$ = new Subject<void>();

  constructor(private dataPolling: DataPollingService) {}

  ngOnInit(): void {
    this.dataPolling.stateComparison$.pipe(takeUntil(this.destroy$)).subscribe(comparison => {
      this.stateComparison = comparison;
      this.isLoading = false;
    });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  getStatusColor(): string {
    if (!this.stateComparison) return 'default';
    if (!this.stateComparison.buffer_latest_block) return 'waiting';
    return this.stateComparison.divergence_detected ? 'warning' : 'success';
  }

  getStatusIcon(): string {
    if (!this.stateComparison) return '?';
    if (!this.stateComparison.buffer_latest_block) return '⏳';
    return this.stateComparison.divergence_detected ? '⚠️' : '✅';
  }

  getStatusText(): string {
    if (!this.stateComparison) return 'Unknown';
    if (!this.stateComparison.buffer_latest_block) return 'WAITING FOR EVENTS';
    return this.stateComparison.divergence_detected ? 'DIVERGENCE DETECTED' : 'SYNCED';
  }

  truncateHash(hash: string, length: number = 16): string {
    return hash.substring(0, length) + '...';
  }

  refresh(): void {}
}
