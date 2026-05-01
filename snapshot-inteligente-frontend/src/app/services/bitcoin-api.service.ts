import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { MempoolSummary } from '../models/mempool.model';
import { BlockchainLag } from '../models/blockchain.model';

@Injectable({
  providedIn: 'root'
})
export class BitcoinApiService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getMempoolSummary(): Observable<MempoolSummary> {
    return this.http.get<MempoolSummary>(`${this.apiUrl}/mempool/summary`);
  }

  getBlockchainLag(): Observable<BlockchainLag> {
    return this.http.get<BlockchainLag>(`${this.apiUrl}/blockchain/lag`);
  }

  getHealth(): Observable<any> {
    return this.http.get('http://localhost:8000/health');
  }
}
