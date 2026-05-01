import pytest
from unittest.mock import MagicMock, patch
from layers.bitcoin_service import BitcoinService
from layers.rpc_client import RPCClient
from layers.cache_layer import CacheLayer
from models.responses import MempoolSummary, BlockchainLag
from models.errors import RPCConnectionError, RPCMethodError

@pytest.fixture
def mock_rpc():
    return MagicMock(spec=RPCClient)

@pytest.fixture
def cache():
    return CacheLayer()

@pytest.fixture
def service(mock_rpc, cache):
    return BitcoinService(mock_rpc, cache)

def test_classify_fee_low(service):
    assert service._classify_fee(5.0) == 'low'
    assert service._classify_fee(9.9) == 'low'

def test_classify_fee_medium(service):
    assert service._classify_fee(10.0) == 'medium'
    assert service._classify_fee(25.0) == 'medium'
    assert service._classify_fee(50.0) == 'medium'

def test_classify_fee_high(service):
    assert service._classify_fee(50.1) == 'high'
    assert service._classify_fee(100.0) == 'high'

def test_get_mempool_summary_success(mock_rpc, service):
    # Mock RPC responses
    mock_rpc.call.side_effect = [
        # getmempoolinfo response
        {
            'size': 3,
            'bytes': 1000,
            'total_vsize': 900,
            'usage': 50000,
        },
        # getrawmempool(true) response
        {
            'tx1': {
                'fees': {'base': 0.0001},
                'vsize': 200
            },
            'tx2': {
                'fees': {'base': 0.0005},
                'vsize': 300
            },
            'tx3': {
                'fees': {'base': 0.003},
                'vsize': 400
            }
        }
    ]
    
    result = service.get_mempool_summary()
    
    assert isinstance(result, MempoolSummary)
    assert result.tx_count == 3
    assert result.total_vsize == 900
    assert result.fee_distribution['low'] >= 0
    assert result.fee_distribution['medium'] >= 0
    assert result.fee_distribution['high'] >= 0
    assert result.timestamp is not None

def test_get_mempool_summary_empty(mock_rpc, service):
    mock_rpc.call.side_effect = [
        {'size': 0, 'bytes': 0, 'total_vsize': 0},
        {}  # Empty mempool
    ]
    
    result = service.get_mempool_summary()
    
    assert result.tx_count == 0
    assert result.avg_fee_rate == 0.0
    assert result.fee_distribution == {'low': 0, 'medium': 0, 'high': 0}

def test_get_blockchain_lag_synced(mock_rpc, service):
    mock_rpc.call.return_value = {
        'blocks': 100000,
        'headers': 100000,
        'difficulty': 1234567.89,
    }
    
    result = service.get_blockchain_lag()
    
    assert isinstance(result, BlockchainLag)
    assert result.blocks == 100000
    assert result.headers == 100000
    assert result.lag == 0

def test_get_blockchain_lag_lagging(mock_rpc, service):
    mock_rpc.call.return_value = {
        'blocks': 100000,
        'headers': 100050,
        'difficulty': 1234567.89,
    }
    
    result = service.get_blockchain_lag()
    
    assert result.blocks == 100000
    assert result.headers == 100050
    assert result.lag == 50

def test_get_mempool_summary_rpc_error(mock_rpc, service):
    mock_rpc.call.side_effect = RPCConnectionError("Connection failed")
    
    with pytest.raises(RPCConnectionError):
        service.get_mempool_summary()

def test_get_blockchain_lag_rpc_error(mock_rpc, service):
    mock_rpc.call.side_effect = RPCMethodError("getblockchaininfo", -32600, "Invalid request")
    
    with pytest.raises(RPCMethodError):
        service.get_blockchain_lag()
