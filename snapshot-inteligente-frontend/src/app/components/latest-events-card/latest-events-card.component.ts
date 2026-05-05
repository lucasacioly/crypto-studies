import { Component, OnInit, OnDestroy } from '@angular/core';
import { BitcoinApiService } from '../../services/bitcoin-api.service';
import { LatestEvents } from '../../models/events.model';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';

@Component({
  selector: 'app-latest-events-card',
  templateUrl: './latest-events-card.component.html',
  styleUrls: ['./latest-events-card.component.scss']
})
export class LatestEventsCardComponent implements OnInit, OnDestroy {
  latestEvents: LatestEvents | null = null;
  isLoading = false;
  error: string | null = null;
  refreshInterval = 15000;
  private destroy$ = new Subject<void>();

  constructor(private bitcoinApi: BitcoinApiService) {}

  ngOnInit(): void {
    this.loadLatestEvents();
    setInterval(() => this.loadLatestEvents(), this.refreshInterval);
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  private loadLatestEvents(): void {
    this.isLoading = true;
    this.error = null;

    this.bitcoinApi.getLatestEvents(10)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (events: LatestEvents) => {
          this.latestEvents = events;
          this.isLoading = false;
        },
        error: (error: any) => {
          console.error('Error fetching latest events:', error);
          this.error = 'Failed to fetch latest events';
          this.isLoading = false;
        }
      });
  }

  formatTimestamp(ts: number): string {
    const date = new Date(ts * 1000);
    const now = new Date();
    const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);
    if (seconds < 60) return `${seconds}s ago`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    return date.toLocaleTimeString();
  }

  truncate(hash: string, length: number = 12): string {
    return hash.substring(0, length) + '...';
  }

  refresh(): void {
    this.loadLatestEvents();
  }
}
