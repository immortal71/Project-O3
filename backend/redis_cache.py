"""
Redis caching service
"""

# Copyright (c) 2025 OncoPurpose (trovesx)
# All Rights Reserved.
# For licensing info, see LICENSE or contact oncopurpose@trovesx.com

import json
from datetime import timedelta
from typing import Any, Optional, Union

import aioredis
from aioredis import Redis

from app.core.config import settings
from app.core.logging import get_struct_logger

logger = get_struct_logger(__name__)


class RedisCache:
    """Redis-based caching service"""
    
    def __init__(self):
        self.redis: Optional[Redis] = None
        self._connected = False
    
    async def connect(self) -> bool:
        """Connect to Redis"""
        try:
            self.redis = await aioredis.create_redis_pool(
                settings.REDIS_URL,
                maxsize=settings.REDIS_POOL_SIZE,
                encoding="utf-8",
            )
            self._connected = True
            logger.info("Connected to Redis")
            return True
            
        except Exception as e:
            logger.error("Failed to connect to Redis", extra={"error": str(e)})
            self._connected = False
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from Redis"""
        if self.redis:
            self.redis.close()
            await self.redis.wait_closed()
            self._connected = False
            logger.info("Disconnected from Redis")
    
    @property
    def is_connected(self) -> bool:
        """Check if connected to Redis"""
        return self._connected and self.redis is not None
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        
        if not self.is_connected:
            return None
        
        try:
            value = await self.redis.get(key)
            
            if value is None:
                return None
            
            # Try to deserialize JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
                
        except Exception as e:
            logger.error(
                "Error getting value from cache",
                extra={"error": str(e), "key": key},
            )
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """Set value in cache"""
        
        if not self.is_connected:
            return False
        
        try:
            # Serialize value
            if isinstance(value, (dict, list)):
                serialized_value = json.dumps(value)
            else:
                serialized_value = str(value)
            
            # Set with TTL if provided
            if ttl:
                await self.redis.setex(key, ttl, serialized_value)
            else:
                await self.redis.set(key, serialized_value)
            
            return True
            
        except Exception as e:
            logger.error(
                "Error setting value in cache",
                extra={"error": str(e), "key": key},
            )
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        
        if not self.is_connected:
            return False
        
        try:
            result = await self.redis.delete(key)
            return result > 0
            
        except Exception as e:
            logger.error(
                "Error deleting value from cache",
                extra={"error": str(e), "key": key},
            )
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        
        if not self.is_connected:
            return False
        
        try:
            return await self.redis.exists(key)
            
        except Exception as e:
            logger.error(
                "Error checking key existence",
                extra={"error": str(e), "key": key},
            )
            return False
    
    async def ttl(self, key: str) -> int:
        """Get TTL for key"""
        
        if not self.is_connected:
            return -2  # Key doesn't exist
        
        try:
            return await self.redis.ttl(key)
            
        except Exception as e:
            logger.error(
                "Error getting TTL",
                extra={"error": str(e), "key": key},
            )
            return -2
    
    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment counter"""
        
        if not self.is_connected:
            return None
        
        try:
            return await self.redis.incr(key, amount)
            
        except Exception as e:
            logger.error(
                "Error incrementing counter",
                extra={"error": str(e), "key": key},
            )
            return None
    
    async def get_keys(self, pattern: str) -> List[str]:
        """Get keys matching pattern"""
        
        if not self.is_connected:
            return []
        
        try:
            return await self.redis.keys(pattern)
            
        except Exception as e:
            logger.error(
                "Error getting keys",
                extra={"error": str(e), "pattern": pattern},
            )
            return []
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        
        if not self.is_connected:
            return 0
        
        try:
            keys = await self.get_keys(pattern)
            if keys:
                return await self.redis.delete(*keys)
            return 0
            
        except Exception as e:
            logger.error(
                "Error clearing pattern",
                extra={"error": str(e), "pattern": pattern},
            )
            return 0
    
    async def health_check(self) -> bool:
        """Check Redis health"""
        
        if not self.is_connected:
            return False
        
        try:
            await self.redis.ping()
            return True
            
        except Exception as e:
            logger.error("Redis health check failed", extra={"error": str(e)})
            return False


class CacheManager:
    """Cache manager with predefined TTLs"""
    
    def __init__(self, redis_cache: RedisCache):
        self.cache = redis_cache
        
        # Define TTLs in seconds
        self.ttls = {
            "very_short": 60,      # 1 minute
            "short": 300,          # 5 minutes
            "medium": 3600,        # 1 hour
            "long": 86400,         # 24 hours
            "very_long": 604800,   # 7 days
            "month": 2592000,      # 30 days
        }
    
    def get_ttl(self, ttl_type: str) -> int:
        """Get TTL in seconds"""
        return self.ttls.get(ttl_type, self.ttls["medium"])
    
    # Cache key generators
    @staticmethod
    def user_key(user_id: str) -> str:
        return f"user:{user_id}"
    
    @staticmethod
    def drug_key(drug_id: str) -> str:
        return f"drug:{drug_id}"
    
    @staticmethod
    def drug_predictions_key(drug_id: str) -> str:
        return f"drug:{drug_id}:predictions"
    
    @staticmethod
    def cancer_key(cancer_id: str) -> str:
        return f"cancer:{cancer_id}"
    
    @staticmethod
    def search_results_key(search_hash: str) -> str:
        return f"search:{search_hash}"
    
    @staticmethod
    def paper_summary_key(paper_id: str) -> str:
        return f"paper:{paper_id}:summary"
    
    @staticmethod
    def market_analysis_key(drug_id: str, cancer_id: str) -> str:
        return f"analysis:market:{drug_id}:{cancer_id}"
    
    @staticmethod
    def api_rate_limit_key(user_id: str, endpoint: str) -> str:
        return f"ratelimit:{user_id}:{endpoint}"


# Global cache instances
redis_cache = RedisCache()
cache_manager = CacheManager(redis_cache)