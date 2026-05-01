import { Component, Input, OnInit } from '@angular/core';
import { MempoolSummary } from '../models/mempool.model';
import { ChartConfiguration } from 'chart.js';

@Component({
  selector: 'app-mempool-card',
  templateUrl: './mempool-card.component.html',
  styleUrls: ['./mempool-card.component.scss']
})
export class MempoolCardComponent implements OnInit {
  @Input() data: MempoolSummary | null = null;

  feeChartOptions: ChartConfiguration['options'] = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        position: 'bottom'
      }
    }
  };

  feeChartData: any = {};

  ngOnInit(): void {
    if (this.data) {
      this.updateChart();
    }
  }

  ngOnChanges(): void {
    if (this.data) {
      this.updateChart();
    }
  }

  private updateChart(): void {
    if (!this.data) return;

    const total = this.data.fee_distribution.low + this.data.fee_distribution.medium + this.data.fee_distribution.high;
    const percentages = {
      low: ((this.data.fee_distribution.low / total) * 100).toFixed(1),
      medium: ((this.data.fee_distribution.medium / total) * 100).toFixed(1),
      high: ((this.data.fee_distribution.high / total) * 100).toFixed(1)
    };

    this.feeChartData = {
      labels: [
        `Low (${percentages.low}%)`,
        `Medium (${percentages.medium}%)`,
        `High (${percentages.high}%)`
      ],
      datasets: [{
        data: [
          this.data.fee_distribution.low,
          this.data.fee_distribution.medium,
          this.data.fee_distribution.high
        ],
        backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
        borderColor: ['#059669', '#d97706', '#dc2626'],
        borderWidth: 1
      }]
    };
  }

  getDoughnutChartOptions(): ChartConfiguration['options'] {
    return {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          position: 'bottom'
        }
      }
    };
  }
}
