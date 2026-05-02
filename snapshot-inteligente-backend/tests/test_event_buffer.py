"""
Tests for EventBuffer and ZMQListener.
"""

import pytest
import asyncio
from datetime import datetime
from layers.event_buffer import EventBuffer, BlockEvent, TransactionEvent, ZMQListener


class TestEventBuffer:
    """Test cases for EventBuffer."""

    @pytest.fixture
    async def event_buffer(self):
        """Create an EventBuffer instance."""
        return EventBuffer(block_capacity=10, tx_capacity=20)

    @pytest.mark.asyncio
    async def test_add_block(self):
        """Test adding a block event."""
        buffer = EventBuffer()
        
        block = BlockEvent(
            block_hash="abc123",
            block_height=100,
        )
        
        await buffer.add_block(block)
        
        blocks = await buffer.get_recent_blocks()
        assert len(blocks) == 1
        assert blocks[0].block_hash == "abc123"

    @pytest.mark.asyncio
    async def test_add_multiple_blocks(self):
        """Test adding multiple block events."""
        buffer = EventBuffer(block_capacity=5)
        
        for i in range(3):
            block = BlockEvent(block_hash=f"hash{i}", block_height=100 + i)
            await buffer.add_block(block)
        
        blocks = await buffer.get_recent_blocks()
        assert len(blocks) == 3

    @pytest.mark.asyncio
    async def test_block_capacity_overflow(self):
        """Test that oldest blocks are removed when capacity exceeded."""
        buffer = EventBuffer(block_capacity=3)
        
        # Add 5 blocks (capacity is 3)
        for i in range(5):
            block = BlockEvent(block_hash=f"hash{i}", block_height=100 + i)
            await buffer.add_block(block)
        
        blocks = await buffer.get_recent_blocks()
        assert len(blocks) == 3
        # Should have last 3 blocks (indices 2, 3, 4)
        assert blocks[0].block_hash == "hash2"
        assert blocks[2].block_hash == "hash4"

    @pytest.mark.asyncio
    async def test_add_transaction(self):
        """Test adding a transaction event."""
        buffer = EventBuffer()
        
        tx = TransactionEvent(
            txid="tx123",
        )
        
        await buffer.add_transaction(tx)
        
        txs = await buffer.get_recent_transactions()
        assert len(txs) == 1
        assert txs[0].txid == "tx123"

    @pytest.mark.asyncio
    async def test_add_multiple_transactions(self):
        """Test adding multiple transaction events."""
        buffer = EventBuffer()
        
        for i in range(5):
            tx = TransactionEvent(txid=f"tx{i}")
            await buffer.add_transaction(tx)
        
        txs = await buffer.get_recent_transactions()
        assert len(txs) == 5

    @pytest.mark.asyncio
    async def test_get_recent_blocks_with_limit(self):
        """Test getting limited number of recent blocks."""
        buffer = EventBuffer()
        
        for i in range(10):
            block = BlockEvent(block_hash=f"hash{i}", block_height=100 + i)
            await buffer.add_block(block)
        
        # Get last 3 blocks
        recent_blocks = await buffer.get_recent_blocks(limit=3)
        assert len(recent_blocks) == 3
        assert recent_blocks[0].block_hash == "hash7"
        assert recent_blocks[2].block_hash == "hash9"

    @pytest.mark.asyncio
    async def test_get_recent_transactions_with_limit(self):
        """Test getting limited number of recent transactions."""
        buffer = EventBuffer()
        
        for i in range(20):
            tx = TransactionEvent(txid=f"tx{i}")
            await buffer.add_transaction(tx)
        
        # Get last 5 transactions
        recent_txs = await buffer.get_recent_transactions(limit=5)
        assert len(recent_txs) == 5
        assert recent_txs[0].txid == "tx15"
        assert recent_txs[4].txid == "tx19"

    @pytest.mark.asyncio
    async def test_get_latest_block(self):
        """Test getting the latest block."""
        buffer = EventBuffer()
        
        blocks = []
        for i in range(5):
            block = BlockEvent(block_hash=f"hash{i}", block_height=100 + i)
            blocks.append(block)
            await buffer.add_block(block)
        
        latest = await buffer.get_latest_block()
        assert latest.block_hash == "hash4"

    @pytest.mark.asyncio
    async def test_get_latest_block_empty_buffer(self):
        """Test getting latest block from empty buffer."""
        buffer = EventBuffer()
        
        latest = await buffer.get_latest_block()
        assert latest is None

    @pytest.mark.asyncio
    async def test_get_stats(self):
        """Test getting buffer statistics."""
        buffer = EventBuffer(block_capacity=50, tx_capacity=100)
        
        # Add some events
        for i in range(5):
            block = BlockEvent(block_hash=f"hash{i}", block_height=100 + i)
            await buffer.add_block(block)
        
        for i in range(10):
            tx = TransactionEvent(txid=f"tx{i}")
            await buffer.add_transaction(tx)
        
        stats = await buffer.get_stats()
        
        assert stats["blocks_count"] == 5
        assert stats["blocks_capacity"] == 50
        assert stats["transactions_count"] == 10
        assert stats["transactions_capacity"] == 100
        assert stats["blocks_received_total"] == 5
        assert stats["transactions_received_total"] == 10

    @pytest.mark.asyncio
    async def test_clear_buffer(self):
        """Test clearing the buffer."""
        buffer = EventBuffer()
        
        # Add events
        for i in range(5):
            await buffer.add_block(BlockEvent(block_hash=f"hash{i}"))
            await buffer.add_transaction(TransactionEvent(txid=f"tx{i}"))
        
        # Clear
        await buffer.clear()
        
        # Verify cleared
        blocks = await buffer.get_recent_blocks()
        txs = await buffer.get_recent_transactions()
        
        assert len(blocks) == 0
        assert len(txs) == 0

    @pytest.mark.asyncio
    async def test_concurrent_access(self):
        """Test concurrent read/write access (thread-safety)."""
        buffer = EventBuffer()
        
        async def writer():
            """Write events."""
            for i in range(10):
                block = BlockEvent(block_hash=f"hash{i}", block_height=100 + i)
                await buffer.add_block(block)
                await asyncio.sleep(0.001)
        
        async def reader():
            """Read events."""
            for _ in range(10):
                await buffer.get_recent_blocks()
                await asyncio.sleep(0.001)
        
        # Run concurrent operations
        await asyncio.gather(writer(), reader(), reader())
        
        # Verify all writes completed
        blocks = await buffer.get_recent_blocks()
        assert len(blocks) == 10

    @pytest.mark.asyncio
    async def test_block_event_timestamps(self):
        """Test that block events have correct timestamps."""
        buffer = EventBuffer()
        
        before = datetime.utcnow().timestamp()
        block = BlockEvent(block_hash="abc123")
        await buffer.add_block(block)
        after = datetime.utcnow().timestamp()
        
        retrieved = await buffer.get_recent_blocks()
        assert len(retrieved) == 1
        
        # Verify timestamp is within reasonable range
        assert retrieved[0].received_at >= before
        assert retrieved[0].received_at <= after + 1  # Allow 1 second margin


class TestZMQListener:
    """Test cases for ZMQListener."""

    @pytest.fixture
    async def zmq_listener(self):
        """Create a ZMQListener instance with mock buffer."""
        buffer = EventBuffer()
        listener = ZMQListener(buffer, zmq_host="localhost", zmq_port=28332)
        yield listener
        # Cleanup
        try:
            await listener.stop()
        except:
            pass

    def test_listener_init(self):
        """Test ZMQListener initialization."""
        buffer = EventBuffer()
        listener = ZMQListener(buffer, zmq_host="192.168.1.1", zmq_port=29999)
        
        assert listener.zmq_host == "192.168.1.1"
        assert listener.zmq_port == 29999
        assert listener.zmq_url == "tcp://192.168.1.1:29999"
        assert listener.running is False

    def test_listener_defaults(self):
        """Test ZMQListener with default values."""
        buffer = EventBuffer()
        listener = ZMQListener(buffer)
        
        assert listener.zmq_host == "localhost"
        assert listener.zmq_port == 28332
        assert listener.zmq_url == "tcp://localhost:28332"

    @pytest.mark.asyncio
    async def test_listener_is_connected_initial(self):
        """Test is_connected returns False initially."""
        buffer = EventBuffer()
        listener = ZMQListener(buffer)
        
        assert listener.is_connected() is False

    @pytest.mark.asyncio
    async def test_listener_stop_when_not_running(self):
        """Test stopping listener that's not running."""
        buffer = EventBuffer()
        listener = ZMQListener(buffer)
        
        # Should not raise
        await listener.stop()
        assert listener.running is False
