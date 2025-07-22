"""Simple in-memory cache for occupation data with TTL support."""

import time
from typing import Dict, Optional, Any
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class SimpleCache:
    """Simple in-memory cache with TTL support."""

    def __init__(self):
        self._cache: Dict[str, tuple[Any, float]] = {}

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        if key in self._cache:
            value, expiry = self._cache[key]
            if time.time() < expiry:
                return value
            else:
                # Remove expired entry
                del self._cache[key]
        return None

    def set(self, key: str, value: Any, ttl_seconds: int):
        """Set value in cache with TTL."""
        expiry = time.time() + ttl_seconds
        self._cache[key] = (value, expiry)

    def clear(self):
        """Clear all cache entries."""
        self._cache.clear()


# Global cache instance
_cache = SimpleCache()


def cache_with_ttl(ttl_seconds: int = 86400):  # Default 24 hours
    """Decorator to cache function results with TTL."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"

            # Check cache first
            cached_value = _cache.get(cache_key)
            if cached_value is not None:
                logger.info(f"Cache hit for {func.__name__}")
                return cached_value

            # Call function and cache result
            logger.info(f"Cache miss for {func.__name__}, calling function")
            result = func(*args, **kwargs)
            _cache.set(cache_key, result, ttl_seconds)

            return result

        return wrapper

    return decorator
