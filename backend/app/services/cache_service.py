import redis
import json
from typing import Optional, Any
from loguru import logger
from app.config import settings


class CacheService:
    """Redis cache service using Upstash"""

    def __init__(self):
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Redis cache connected successfully")
        except Exception as e:
            logger.warning(f"Redis connection failed: {str(e)}")
            self.redis_client = None

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.redis_client:
            return None

        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error: {str(e)}")
            return None

    def set(self, key: str, value: Any, expire: int = 3600):
        """
        Set value in cache

        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            expire: Expiration time in seconds (default 1 hour)
        """
        if not self.redis_client:
            return False

        try:
            serialized = json.dumps(value)
            self.redis_client.setex(key, expire, serialized)
            return True
        except Exception as e:
            logger.error(f"Cache set error: {str(e)}")
            return False

    def delete(self, key: str):
        """Delete key from cache"""
        if not self.redis_client:
            return False

        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {str(e)}")
            return False

    def clear_pattern(self, pattern: str):
        """Delete all keys matching pattern"""
        if not self.redis_client:
            return False

        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
            return True
        except Exception as e:
            logger.error(f"Cache clear error: {str(e)}")
            return False


# Singleton instance
cache_service = CacheService()
