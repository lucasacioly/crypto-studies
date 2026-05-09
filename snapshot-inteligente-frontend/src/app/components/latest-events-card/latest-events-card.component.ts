import { Component, OnInit, OnDestroy } from '@angular/core';
import { LatestEvents } from '../../models/events.model';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { DataPollingService } from '../../services/data-polling.service';

@Component({
  selector: 'app-latest-events-card',
  templateUrl: './latest-events-card.component.html',
  styleUrls: ['./latest-events-card.component.scss']
})
export class LatestEventsCardComponent implements OnInit, OnDestroy {
  latestEvents: LatestEvents | null = null;
  isLoading = false;
  error: string | null = null;
  private destroy$ = new Subject<void>();

  constructor(private dataPolling: DataPollingService) {}

  ngOnInit(): void {
    this.dataPolling.latestEvents$.pipe(takeUntil(this.destroy$)).subscribe(events => {
      this.latestEvents = events;
      this.isLoading = false;
    });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
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

  refresh(): void {}
}
