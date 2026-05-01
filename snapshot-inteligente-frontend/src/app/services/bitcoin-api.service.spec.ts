import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { BitcoinApiService } from './bitcoin-api.service';
import { MempoolSummary } from '../models/mempool.model';
import { BlockchainLag } from '../models/blockchain.model';

describe('BitcoinApiService', () => {
  let service: BitcoinApiService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [BitcoinApiService]
    });
    service = TestBed.inject(BitcoinApiService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should fetch mempool summary', () => {
    const mockData: MempoolSummary = {
      tx_count: 1000,
      total_vsize: 50000,
      avg_fee_rate: 25.5,
      min_fee_rate: 1.0,
      max_fee_rate: 100.0,
      fee_distribution: { low: 500, medium: 400, high: 100 },
      timestamp: '2026-05-01T12:00:00'
    };

    service.getMempoolSummary().subscribe(data => {
      expect(data.tx_count).toBe(1000);
      expect(data.avg_fee_rate).toBe(25.5);
    });

    const req = httpMock.expectOne(request => request.url.includes('/mempool/summary'));
    expect(req.request.method).toBe('GET');
    req.flush(mockData);
  });

  it('should fetch blockchain lag', () => {
    const mockData: BlockchainLag = {
      blocks: 100000,
      headers: 100050,
      lag: 50,
      timestamp: '2026-05-01T12:00:00'
    };

    service.getBlockchainLag().subscribe(data => {
      expect(data.lag).toBe(50);
    });

    const req = httpMock.expectOne(request => request.url.includes('/blockchain/lag'));
    expect(req.request.method).toBe('GET');
    req.flush(mockData);
  });
});
