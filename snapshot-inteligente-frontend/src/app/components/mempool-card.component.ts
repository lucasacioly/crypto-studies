import { Component, Input, OnInit, OnChanges, SimpleChanges } from '@angular/core';
import { MempoolSummary } from '../models/mempool.model';

@Component({
  selector: 'app-mempool-card',
  templateUrl: './mempool-card.component.html',
  styleUrls: ['./mempool-card.component.scss']
})
export class MempoolCardComponent implements OnInit, OnChanges {
  @Input() data: MempoolSummary | null = null;

  ngOnInit(): void {
    if (this.data) {
      this.updateChart();
    }
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['data'] && !changes['data'].firstChange) {
      this.updateChart();
    }
  }

  private updateChart(): void {
    if (!this.data) return;
    // Chart updates happen through template binding
  }
}
