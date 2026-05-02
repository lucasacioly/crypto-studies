from layers.rpc_client import RPCClient
from layers.cache_layer import CacheLayer
from layers.bitcoin_service import BitcoinService
from layers.event_buffer import EventBuffer, ZMQListener
from config import config

# Initialize services (singletons)
rpc_client = RPCClient()
cache_layer = CacheLayer()
bitcoin_service = BitcoinService(rpc_client, cache_layer)

# Initialize event streaming (Task 2)
event_buffer = EventBuffer(
    block_capacity=config.EVENT_BUFFER_BLOCKS,
    tx_capacity=config.EVENT_BUFFER_TRANSACTIONS
)
zmq_listener = ZMQListener(
    event_buffer=event_buffer,
    zmq_host=config.ZMQ_HOST,
    zmq_port=config.ZMQ_PORT
)

# Dependency injection functions
def get_rpc_client():
    return rpc_client

def get_cache_layer():
    return cache_layer

def get_bitcoin_service():
    return bitcoin_service

def get_event_buffer():
    return event_buffer

def get_zmq_listener():
    return zmq_listener
