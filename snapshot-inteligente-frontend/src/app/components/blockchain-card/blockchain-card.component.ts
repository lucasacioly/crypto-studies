import { Component, Input } from '@angular/core';
import { BlockchainLag } from '../../models/blockchain.model';

@Component({
  selector: 'app-blockchain-card',
  templateUrl: './blockchain-card.component.html',
  styleUrls: ['./blockchain-card.component.scss']
})
export class BlockchainCardComponent {
  @Input() data: BlockchainLag | null = null;

  isLagging(): boolean {
    return this.data ? this.data.lag > 5 : false;
  }

  getLagStatus(): string {
    if (!this.data) return 'unknown';
    if (this.data.lag === 0) return 'synced';
    if (this.data.lag <= 5) return 'syncing';
    return 'lagging';
  }

  getLagColor(): string {
    const status = this.getLagStatus();
    switch (status) {
      case 'synced': return 'text-green-600';
      case 'syncing': return 'text-yellow-600';
      case 'lagging': return 'text-red-600';
      default: return 'text-gray-600';
    }
  }

  getBgColor(): string {
    const status = this.getLagStatus();
    switch (status) {
      case 'synced': return 'bg-green-50';
      case 'syncing': return 'bg-yellow-50';
      case 'lagging': return 'bg-red-50';
      default: return 'bg-gray-50';
    }
  }

  getStatusIcon(): string {
    const status = this.getLagStatus();
    switch (status) {
      case 'synced': return '✓';
      case 'syncing': return '↻';
      case 'lagging': return '⚠';
      default: return '?';
    }
  }
}
