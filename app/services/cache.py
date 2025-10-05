import redis
import json
from typing import Optional, Any
from datetime import timedelta
from ..config import settings

class CacheService:
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        self.default_ttl = 24 * 60 * 60  # 24 hours in seconds
    
    def get(self, key: str) -> Optional[dict]:
        """Get cached data by key"""
        try:
            cached_data = self.redis_client.get(key)
            if cached_data:
                return json.loads(cached_data)
            return None
        except Exception as e:
            print(f"Cache get error for key {key}: {e}")
            return None
    
    def set(self, key: str, data: Any, ttl: Optional[int] = None) -> bool:
        """Set cache data with TTL"""
        try:
            ttl = ttl or self.default_ttl
            serialized_data = json.dumps(data, default=str)
            self.redis_client.setex(key, ttl, serialized_data)
            return True
        except Exception as e:
            print(f"Cache set error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete specific cache key"""
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error for key {key}: {e}")
            return False
    
    def clear_all(self) -> bool:
        """Clear all cache"""
        try:
            self.redis_client.flushdb()
            return True
        except Exception as e:
            print(f"Cache clear all error: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            print(f"Cache clear pattern error for {pattern}: {e}")
            return 0

# Global cache instance
cache = CacheService()