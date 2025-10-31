from typing import Optional, Any
import json
import redis
from functools import wraps
from app.core.config import settings
import hashlib


class RedisCache:
    """Redis cache manager"""

    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True,
        )

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            print(f"Cache get error: {e}")
        return None

    def set(self, key: str, value: Any, ttl: int = settings.CACHE_TTL) -> bool:
        """Set value in cache"""
        try:
            serialized = json.dumps(value)
            return self.redis_client.setex(key, ttl, serialized)
        except Exception as e:
            print(f"Cache set error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False

    def clear_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
        except Exception as e:
            print(f"Cache clear error: {e}")
        return 0

    @staticmethod
    def generate_cache_key(*args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_parts = [str(arg) for arg in args]
        key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
        key_string = ":".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()


cache = RedisCache()


def cached(ttl: int = settings.CACHE_TTL, prefix: str = ""):
    """Decorator for caching function results"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not settings.DIAGNOSIS_CACHE_ENABLED:
                return func(*args, **kwargs)

            # Generate cache key
            cache_key = f"{prefix}:{cache.generate_cache_key(*args, **kwargs)}"

            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result

        return wrapper

    return decorator