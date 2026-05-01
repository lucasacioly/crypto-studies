import pytest
import time
from layers.cache_layer import CacheLayer

class TestCacheLayer:
    @pytest.fixture
    def cache(self):
        return CacheLayer()
    
    def test_cache_hit(self, cache):
        call_count = 0
        
        @cache.cached(ttl_seconds=10)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # First call - cache miss
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count == 1
        
        # Second call - cache hit
        result2 = expensive_function(5)
        assert result2 == 10
        assert call_count == 1  # Function not called again
    
    def test_cache_miss_different_params(self, cache):
        call_count = 0
        
        @cache.cached(ttl_seconds=10)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        result1 = expensive_function(5)
        result2 = expensive_function(10)
        
        assert result1 == 10
        assert result2 == 20
        assert call_count == 2  # Function called twice (different params)
    
    def test_cache_expiration(self, cache):
        call_count = 0
        
        @cache.cached(ttl_seconds=1)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # First call
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count == 1
        
        # Immediate second call - cache hit
        result2 = expensive_function(5)
        assert call_count == 1
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Third call - cache expired, function called again
        result3 = expensive_function(5)
        assert call_count == 2
    
    def test_cache_stats(self, cache):
        @cache.cached(ttl_seconds=10)
        def test_func(x):
            return x + 1
        
        test_func(1)  # miss
        test_func(1)  # hit
        test_func(1)  # hit
        test_func(2)  # miss
        
        stats = cache.get_stats()
        assert stats['hits'] == 2
        assert stats['misses'] == 2
        assert stats['total'] == 4
        assert stats['hit_rate_percent'] == 50.0
    
    def test_cache_clear(self, cache):
        @cache.cached(ttl_seconds=10)
        def test_func(x):
            return x + 1
        
        test_func(1)
        assert len(cache.cache) > 0
        
        cache.clear()
        assert len(cache.cache) == 0
