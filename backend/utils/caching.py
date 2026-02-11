from typing import Any, Optional
import time
import hashlib
import asyncio
from functools import wraps


class SimpleCache:
    """
    A simple in-memory cache with TTL (Time To Live)
    """

    def __init__(self):
        self._cache = {}

    def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache if it exists and hasn't expired"""
        if key in self._cache:
            value, expiry = self._cache[key]
            if time.time() < expiry:
                return value
            else:
                # Remove expired entry
                del self._cache[key]
        return None

    def set(
        self, key: str, value: Any, ttl: int = 300
    ) -> None:  # Default TTL: 5 minutes
        """Set a value in the cache with a TTL"""
        expiry = time.time() + ttl
        self._cache[key] = (value, expiry)

    def delete(self, key: str) -> None:
        """Delete a value from the cache"""
        if key in self._cache:
            del self._cache[key]

    def clear(self) -> None:
        """Clear all values from the cache"""
        self._cache.clear()


# Global cache instance
cache = SimpleCache()


def cached(ttl: int = 300):
    """
    Decorator to cache function results
    """

    def decorator(func):
        if asyncio.iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                # Create a cache key based on function name and arguments
                key_args = str(args) + str(sorted(kwargs.items()))
                key = hashlib.md5(f"{func.__name__}:{key_args}".encode()).hexdigest()

                # Try to get from cache
                result = cache.get(key)
                if result is not None:
                    return result

                # Execute function and cache result
                result = await func(*args, **kwargs)
                cache.set(key, result, ttl)
                return result

            return async_wrapper
        else:

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                # Create a cache key based on function name and arguments
                key_args = str(args) + str(sorted(kwargs.items()))
                key = hashlib.md5(f"{func.__name__}:{key_args}".encode()).hexdigest()

                # Try to get from cache
                result = cache.get(key)
                if result is not None:
                    return result

                # Execute function and cache result
                result = func(*args, **kwargs)
                cache.set(key, result, ttl)
                return result

            return sync_wrapper

    return decorator
