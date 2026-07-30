"""
Caching Module for Bible Digital Twin

Production-grade caching with Redis support, LRU cache,
and cache invalidation strategies.
"""

import asyncio
import hashlib
import json
import time
from typing import Optional, Any, Dict, List, Callable
from functools import wraps
from collections import OrderedDict

from config.settings import settings


try:
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    try:
        import aioredis
        REDIS_AVAILABLE = True
    except ImportError:
        REDIS_AVAILABLE = False


class LRUCache:
    """In-memory LRU cache with TTL support."""
    
    def __init__(self, max_size: int = 1000):
        self.cache: OrderedDict = OrderedDict()
        self.max_size = max_size
        self.ttl_map: Dict[str, float] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key not in self.cache:
            return None
        
        # Check TTL
        if key in self.ttl_map and time.time() > self.ttl_map[key]:
            self.delete(key)
            return None
        
        # Move to end (most recently used)
        self.cache.move_to_end(key)
        return self.cache[key]
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with optional TTL."""
        if key in self.cache:
            self.cache.move_to_end(key)
        else:
            if len(self.cache) >= self.max_size:
                # Remove oldest item
                oldest_key = next(iter(self.cache))
                self.delete(oldest_key)
        
        self.cache[key] = value
        if ttl:
            self.ttl_map[key] = time.time() + ttl
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if key in self.cache:
            del self.cache[key]
            self.ttl_map.pop(key, None)
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
        self.ttl_map.clear()
    
    def size(self) -> int:
        """Get current cache size."""
        return len(self.cache)


class RedisCache:
    """Redis-backed cache with async support."""
    
    def __init__(self, redis_url: str = settings.REDIS_URL):
        self.redis_url = redis_url
        self.redis: Optional[aioredis.Redis] = None
        self._connected = False
    
    async def connect(self) -> None:
        """Connect to Redis."""
        if not REDIS_AVAILABLE:
            raise RuntimeError("Redis client not available. Install redis or aioredis.")
        
        self.redis = await aioredis.from_url(
            self.redis_url,
            encoding="utf-8",
            decode_responses=True
        )
        self._connected = True
    
    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self.redis:
            await self.redis.close()
            self._connected = False
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache."""
        if not self._connected:
            await self.connect()
        
        value = await self.redis.get(key)
        if value:
            return json.loads(value)
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in Redis cache with optional TTL."""
        if not self._connected:
            await self.connect()
        
        serialized = json.dumps(value)
        if ttl:
            await self.redis.setex(key, ttl, serialized)
        else:
            await self.redis.set(key, serialized)
    
    async def delete(self, key: str) -> bool:
        """Delete key from Redis cache."""
        if not self._connected:
            await self.connect()
        
        result = await self.redis.delete(key)
        return result > 0
    
    async def clear_pattern(self, pattern: str) -> None:
        """Clear all keys matching a pattern."""
        if not self._connected:
            await self.connect()
        
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)


class CacheManager:
    """Unified cache manager with fallback strategy."""
    
    def __init__(self):
        self.memory_cache = LRUCache(max_size=1000)
        self.redis_cache: Optional[RedisCache] = None
        self.enabled = settings.ENABLE_CACHE
        
        if settings.ENABLE_CACHE and REDIS_AVAILABLE:
            try:
                self.redis_cache = RedisCache()
            except Exception:
                pass
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from arguments."""
        key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache (Redis first, then memory)."""
        if not self.enabled:
            return None
        
        # Try Redis first
        if self.redis_cache:
            try:
                value = await self.redis_cache.get(key)
                if value is not None:
                    return value
            except Exception:
                pass
        
        # Fallback to memory cache
        return self.memory_cache.get(key)
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in both caches."""
        if not self.enabled:
            return
        
        ttl = ttl or settings.CACHE_TTL
        
        # Set in memory cache
        self.memory_cache.set(key, value, ttl=ttl)
        
        # Set in Redis if available
        if self.redis_cache:
            try:
                await self.redis_cache.set(key, value, ttl=ttl)
            except Exception:
                pass
    
    async def delete(self, key: str) -> None:
        """Delete key from all caches."""
        self.memory_cache.delete(key)
        if self.redis_cache:
            try:
                await self.redis_cache.delete(key)
            except Exception:
                pass
    
    async def invalidate_pattern(self, prefix: str) -> None:
        """Invalidate all keys with a given prefix."""
        if self.redis_cache:
            try:
                await self.redis_cache.clear_pattern(f"{prefix}*")
            except Exception:
                pass
        self.memory_cache.clear()
    
    def cached(self, prefix: str = "default", ttl: Optional[int] = None):
        """Decorator for caching function results."""
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                key = self._generate_key(prefix, func.__name__, *args, **kwargs)
                
                # Try cache first
                cached_value = await self.get(key)
                if cached_value is not None:
                    return cached_value
                
                # Call function
                result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
                
                # Cache result
                await self.set(key, result, ttl=ttl)
                
                return result
            return wrapper
        return decorator


# Global cache instance
cache_manager = CacheManager()
