import time
import hashlib
import json
from typing import Any, Callable, Dict, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Represents a cached value with expiration time."""
    data: Any
    expiry_time: float

class CacheLayer:
    """
    In-memory cache with TTL support.
    Provides decorator for caching method responses.
    """
    
    def __init__(self):
        self.cache: Dict[str, CacheEntry] = {}
        self.hits: int = 0
        self.misses: int = 0
    
    def cached(self, ttl_seconds: int = 10):
        """
        Decorator factory for caching method responses.
        
        Usage:
            cache = CacheLayer()
            
            @cache.cached(ttl_seconds=10)
            def expensive_method(self, param1):
                return compute_something()
        
        Args:
            ttl_seconds: Time-to-live in seconds
        """
        def decorator(func: Callable) -> Callable:
            def wrapper(*args, **kwargs) -> Any:
                # Generate cache key
                cache_key = self._make_key(func.__name__, args, kwargs)
                
                # Check if cache hit and not expired
                if cache_key in self.cache:
                    entry = self.cache[cache_key]
                    if time.time() < entry.expiry_time:
                        self.hits += 1
                        logger.debug(f"Cache hit for {func.__name__}")
                        return entry.data
                    else:
                        # Expired, remove from cache
                        del self.cache[cache_key]
                        logger.debug(f"Cache expired for {func.__name__}")
                
                # Cache miss
                self.misses += 1
                logger.debug(f"Cache miss for {func.__name__}")
                result = func(*args, **kwargs)
                
                # Store in cache with TTL
                expiry_time = time.time() + ttl_seconds
                self.cache[cache_key] = CacheEntry(data=result, expiry_time=expiry_time)
                
                return result
            
            return wrapper
        
        return decorator
    
    def _make_key(self, func_name: str, args: Tuple, kwargs: Dict) -> str:
        """
        Generate unique cache key from function name and parameters.
        
        Args:
            func_name: Function name
            args: Function args
            kwargs: Function kwargs
            
        Returns:
            Unique cache key string
        """
        # Ignore 'self' parameter (first arg in methods)
        args_to_hash = args[1:] if args and hasattr(args[0], '__dict__') else args
        
        # Convert to JSON-serializable format
        try:
            key_data = json.dumps({
                "func": func_name,
                "args": args_to_hash,
                "kwargs": kwargs
            }, sort_keys=True, default=str)
        except TypeError:
            # Fallback for non-serializable objects
            key_data = f"{func_name}_{str(args)}_{str(kwargs)}"
        
        # Create hash for shorter key
        hash_obj = hashlib.md5(key_data.encode())
        return hash_obj.hexdigest()
    
    def get_stats(self) -> Dict[str, any]:
        """
        Return cache statistics.
        
        Returns:
            Dict with hits, misses, hit_rate
        """
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        
        return {
            "hits": self.hits,
            "misses": self.misses,
            "total": total,
            "hit_rate_percent": round(hit_rate, 2),
            "cached_items": len(self.cache)
        }
    
    def clear(self):
        """Clear all cached data."""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def close(self):
        """Close cache (cleanup)."""
        self.clear()

# Global cache instance
cache_layer = CacheLayer()
