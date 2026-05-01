import pytest
from unittest.mock import patch, MagicMock
from layers.rpc_client import RPCClient
from models.errors import RPCConnectionError, RPCMethodError

@pytest.fixture
def rpc_client():
    return RPCClient(
        host="localhost",
        port=8332,
        user="test",
        password="test",
        timeout=5
    )

def test_rpc_client_init(rpc_client):
    assert rpc_client.host == "localhost"
    assert rpc_client.port == 8332
    assert rpc_client.user == "test"
    assert rpc_client.password == "test"
    assert rpc_client.timeout == 5
    assert rpc_client.url == "http://localhost:8332"

@patch('requests.Session.post')
def test_rpc_call_success(mock_post, rpc_client):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "jsonrpc": "2.0",
        "result": {"blocks": 100},
        "id": 1
    }
    mock_post.return_value = mock_response
    
    result = rpc_client.call('getblockchaininfo')
    assert result == {"blocks": 100}
    mock_post.assert_called_once()

@patch('requests.Session.post')
def test_rpc_call_with_params(mock_post, rpc_client):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "jsonrpc": "2.0",
        "result": "abc123",
        "id": 1
    }
    mock_post.return_value = mock_response
    
    result = rpc_client.call('getblockhash', [0])
    assert result == "abc123"
    call_args = mock_post.call_args
    assert call_args[1]['json']['params'] == [0]

@patch('requests.Session.post')
def test_rpc_call_connection_error(mock_post, rpc_client):
    import requests
    mock_post.side_effect = requests.exceptions.ConnectionError("Connection refused")
    
    with pytest.raises(RPCConnectionError):
        rpc_client.call('getblockchaininfo')

@patch('requests.Session.post')
def test_rpc_call_timeout(mock_post, rpc_client):
    import requests
    mock_post.side_effect = requests.exceptions.Timeout("Request timed out")
    
    with pytest.raises(RPCConnectionError):
        rpc_client.call('getblockchaininfo')

@patch('requests.Session.post')
def test_rpc_call_rpc_error(mock_post, rpc_client):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "jsonrpc": "2.0",
        "error": {"code": -32601, "message": "Method not found"},
        "id": 1
    }
    mock_post.return_value = mock_response
    
    with pytest.raises(RPCMethodError) as exc_info:
        rpc_client.call('nonexistentmethod')
    
    assert exc_info.value.error_code == -32601
    assert "Method not found" in str(exc_info.value)

@patch('requests.Session.post')
def test_rpc_call_invalid_json(mock_post, rpc_client):
    mock_response = MagicMock()
    mock_response.json.side_effect = ValueError("Invalid JSON")
    
    with pytest.raises(RPCConnectionError):
        rpc_client.call('getblockchaininfo')

@patch('requests.Session.post')
def test_rpc_call_invalid_response_format(mock_post, rpc_client):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "jsonrpc": "2.0",
        "id": 1
    }
    mock_post.return_value = mock_response
    
    with pytest.raises(RPCConnectionError):
        rpc_client.call('getblockchaininfo')
