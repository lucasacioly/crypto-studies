from layers.rpc_client import RPCClient
from layers.cache_layer import CacheLayer
from layers.bitcoin_service import BitcoinService

# Initialize services (singletons)
rpc_client = RPCClient()
cache_layer = CacheLayer()
bitcoin_service = BitcoinService(rpc_client, cache_layer)

# Dependency injection functions
def get_rpc_client():
    return rpc_client

def get_cache_layer():
    return cache_layer

def get_bitcoin_service():
    return bitcoin_service
