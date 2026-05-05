"""
Event buffer layer for real-time Bitcoin event streaming.

Manages circular buffers for block and transaction events received via ZMQ.
Thread-safe using asyncio.Lock for concurrent access.
"""

import asyncio
import logging
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Deque, List, Optional
import zmq
import zmq.asyncio

logger = logging.getLogger(__name__)


@dataclass
class BlockEvent:
    """Represents a Bitcoin block event from ZMQ."""
    block_hash: str
    block_height: Optional[int] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    received_at: float = field(default_factory=lambda: datetime.utcnow().timestamp())


@dataclass
class TransactionEvent:
    """Represents a Bitcoin transaction event from ZMQ."""
    txid: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    received_at: float = field(default_factory=lambda: datetime.utcnow().timestamp())
    size_vbytes: Optional[int] = None
    fee_rate_sat_vb: Optional[float] = None


class EventBuffer:
    """
    Manages circular buffers for block and transaction events.
    Thread-safe using asyncio.Lock for concurrent access.
    
    Attributes:
        blocks: Circular buffer for block events (FIFO with max capacity)
        transactions: Circular buffer for transaction events (FIFO with max capacity)
        block_capacity: Maximum number of blocks to keep in memory
        tx_capacity: Maximum number of transactions to keep in memory
    """

    def __init__(self, block_capacity: int = 50, tx_capacity: int = 500):
        """
        Initialize event buffer with circular buffers.
        
        Args:
            block_capacity: Maximum blocks to store (default: 50)
            tx_capacity: Maximum transactions to store (default: 500)
        """
        self.block_capacity = block_capacity
        self.tx_capacity = tx_capacity
        
        # Circular buffers using deque with maxlen
        self.blocks: Deque[BlockEvent] = deque(maxlen=block_capacity)
        self.transactions: Deque[TransactionEvent] = deque(maxlen=tx_capacity)
        
        # Thread-safety lock
        self.lock = asyncio.Lock()
        
        # Statistics
        self.blocks_received = 0
        self.transactions_received = 0
        self.last_block_time: Optional[float] = None
        self.last_tx_time: Optional[float] = None

    async def add_block(self, block_event: BlockEvent) -> None:
        """
        Add block event to circular buffer (thread-safe).
        
        Automatically removes oldest block if capacity is exceeded.
        
        Args:
            block_event: BlockEvent to add
        """
        async with self.lock:
            self.blocks.append(block_event)
            self.blocks_received += 1
            self.last_block_time = datetime.utcnow().timestamp()
            logger.debug(f"Added block {block_event.block_hash[:16]}... (total: {len(self.blocks)})")

    async def add_transaction(self, tx_event: TransactionEvent) -> None:
        """
        Add transaction event to circular buffer (thread-safe).
        
        Automatically removes oldest transaction if capacity is exceeded.
        
        Args:
            tx_event: TransactionEvent to add
        """
        async with self.lock:
            self.transactions.append(tx_event)
            self.transactions_received += 1
            self.last_tx_time = datetime.utcnow().timestamp()
            logger.debug(f"Added tx {tx_event.txid[:16]}... (total: {len(self.transactions)})")

    async def get_recent_blocks(self, limit: Optional[int] = None) -> List[BlockEvent]:
        """
        Get recent blocks from buffer (thread-safe).
        
        Returns blocks in chronological order (oldest to newest).
        
        Args:
            limit: Maximum number of blocks to return (None = all)
            
        Returns:
            List of BlockEvent objects
        """
        async with self.lock:
            blocks_list = list(self.blocks)
            if limit:
                return blocks_list[-limit:]
            return blocks_list

    async def get_recent_transactions(self, limit: Optional[int] = None) -> List[TransactionEvent]:
        """
        Get recent transactions from buffer (thread-safe).
        
        Returns transactions in chronological order (oldest to newest).
        
        Args:
            limit: Maximum number of transactions to return (None = all)
            
        Returns:
            List of TransactionEvent objects
        """
        async with self.lock:
            txs_list = list(self.transactions)
            if limit:
                return txs_list[-limit:]
            return txs_list

    async def get_latest_block(self) -> Optional[BlockEvent]:
        """
        Get the most recent block event (thread-safe).
        
        Returns:
            Latest BlockEvent or None if buffer is empty
        """
        async with self.lock:
            if self.blocks:
                return self.blocks[-1]
            return None

    async def get_latest_transaction(self) -> Optional[TransactionEvent]:
        """
        Get the most recent transaction event (thread-safe).
        
        Returns:
            Latest TransactionEvent or None if buffer is empty
        """
        async with self.lock:
            if self.transactions:
                return self.transactions[-1]
            return None

    async def get_stats(self) -> dict:
        """
        Get buffer statistics.
        
        Returns:
            Dictionary with buffer stats
        """
        async with self.lock:
            return {
                "blocks_count": len(self.blocks),
                "blocks_capacity": self.block_capacity,
                "transactions_count": len(self.transactions),
                "transactions_capacity": self.tx_capacity,
                "blocks_received_total": self.blocks_received,
                "transactions_received_total": self.transactions_received,
                "last_block_time": self.last_block_time,
                "last_tx_time": self.last_tx_time,
            }

    async def get_uptime(self, start_time: Optional[float]) -> Optional[int]:
        """Calculate uptime in seconds."""
        if start_time:
            return int(datetime.utcnow().timestamp() - start_time)
        return None

    async def clear(self) -> None:
        """Clear all buffered events."""
        async with self.lock:
            self.blocks.clear()
            self.transactions.clear()
            logger.info("Event buffers cleared")


class ZMQListener:
    """
    Listens to Bitcoin Core ZMQ events (hashblock, rawtx).
    Pushes events into EventBuffer for storage and retrieval.
    
    Requires Bitcoin Core compiled with ZMQ support:
        zmqpubhashblock=tcp://127.0.0.1:28332
        zmqpubrawtx=tcp://127.0.0.1:28332
    """

    def __init__(
        self,
        event_buffer: EventBuffer,
        zmq_host: str = "localhost",
        zmq_port: int = 28332,
    ):
        """
        Initialize ZMQ listener.
        
        Args:
            event_buffer: EventBuffer instance to push events to
            zmq_host: Bitcoin Core ZMQ host (default: localhost)
            zmq_port: Bitcoin Core ZMQ port (default: 28332)
        """
        self.event_buffer = event_buffer
        self.zmq_host = zmq_host
        self.zmq_port = zmq_port
        self.zmq_url = f"tcp://{zmq_host}:{zmq_port}"
        
        self.running = False
        self.context: Optional[zmq.asyncio.Context] = None
        self.socket: Optional[zmq.asyncio.Socket] = None
        self.start_time: Optional[float] = None
        
        logger.info(f"ZMQListener initialized for {self.zmq_url}")

    async def start(self) -> None:
        """
        Start listening for ZMQ events in a background task.
        
        Listens to:
        - hashblock: New blocks (topic: b"hashblock")
        - rawtx: New transactions (topic: b"rawtx")
        
        Raises:
            zmq.error.ZMQError: If ZMQ connection fails
        """
        try:
            self.running = True
            self.start_time = datetime.utcnow().timestamp()
            logger.info(f"Starting ZMQ listener on {self.zmq_url}")
            
            # Create async ZMQ context
            self.context = zmq.asyncio.Context()
            self.socket = self.context.socket(zmq.SUB)
            
            # Subscribe to topics
            self.socket.subscribe(b"hashblock")
            self.socket.subscribe(b"rawtx")
            
            # Connect to Bitcoin Core ZMQ endpoint
            self.socket.connect(self.zmq_url)
            logger.info(f"Connected to ZMQ at {self.zmq_url}")
            
            # Listen loop
            while self.running:
                try:
                    # Receive message (topic, data, sequence_number)
                    parts = await self.socket.recv_multipart()
                    topic = parts[0]
                    data = parts[1]
                    # sequence_number = parts[2] if len(parts) > 2 else None
                    
                    if topic == b"hashblock":
                        await self._handle_block_event(data)
                    elif topic == b"rawtx":
                        await self._handle_transaction_event(data)
                        
                except asyncio.CancelledError:
                    logger.info("ZMQ listener cancelled")
                    break
                except Exception as e:
                    logger.error(f"Error processing ZMQ message: {e}")
                    
        except zmq.error.ZMQError as e:
            logger.error(f"ZMQ connection error: {e}")
            self.running = False
            raise
        except Exception as e:
            logger.error(f"Unexpected error in ZMQ listener: {e}")
            self.running = False
            raise

    async def stop(self) -> None:
        """Stop the ZMQ listener."""
        logger.info("Stopping ZMQ listener")
        self.running = False
        
        if self.socket:
            self.socket.close()
        if self.context:
            self.context.term()
        
        logger.info("ZMQ listener stopped")

    async def _handle_block_event(self, data: bytes) -> None:
        """
        Handle hashblock event from ZMQ.
        
        Args:
            data: Raw block hash bytes (32 bytes)
        """
        try:
            # Block hash is 32 bytes, convert to hex
            block_hash = data[:32].hex()
            
            # Create BlockEvent
            block_event = BlockEvent(
                block_hash=block_hash,
                timestamp=datetime.utcnow().isoformat(),
                received_at=datetime.utcnow().timestamp(),
            )
            
            # Add to buffer
            await self.event_buffer.add_block(block_event)
            logger.info(f"Block event received: {block_hash[:16]}...")
            
        except Exception as e:
            logger.error(f"Error handling block event: {e}")

    async def _handle_transaction_event(self, data: bytes) -> None:
        """
        Handle rawtx event from ZMQ.
        
        Args:
            data: Raw transaction data (variable length)
        """
        try:
            # Parse raw transaction to extract txid
            # For now, we'll store a placeholder
            # In production, this would deserialize the full tx
            
            # Calculate txid from raw tx data (double SHA256)
            import hashlib
            txid = hashlib.sha256(hashlib.sha256(data).digest()).digest()[::-1].hex()
            
            # Create TransactionEvent
            tx_event = TransactionEvent(
                txid=txid,
                timestamp=datetime.utcnow().isoformat(),
                received_at=datetime.utcnow().timestamp(),
            )
            
            # Add to buffer
            await self.event_buffer.add_transaction(tx_event)
            logger.debug(f"Transaction event received: {txid[:16]}...")
            
        except Exception as e:
            logger.error(f"Error handling transaction event: {e}")

    def is_connected(self) -> bool:
        """Check if ZMQ listener is currently connected."""
        return self.running and self.socket is not None
