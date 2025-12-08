"""
Rate limiting middleware for OncoPurpose API
Implements tier-based rate limiting with Redis backing
"""

# Copyright (c) 2025 OncoPurpose (trovesx)
# All Rights Reserved.
# For licensing info, see LICENSE or contact oncopurpose@trovesx.com

import time
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

import structlog
from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import settings
from app.services.cache.redis_cache import RedisCache

logger = structlog.get_logger()


class RateLimitTier(str, Enum):
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


@dataclass
class RateLimitConfig:
    tier: RateLimitTier
    requests_per_hour: int
    burst_limit: int  # Allow short bursts
    window_size: int = 3600  # 1 hour in seconds


# Rate limit configurations by tier
RATE_LIMITS = {
    RateLimitTier.BASIC: RateLimitConfig(
        tier=RateLimitTier.BASIC,
        requests_per_hour=100,
        burst_limit=20,
        window_size=3600
    ),
    RateLimitTier.PROFESSIONAL: RateLimitConfig(
        tier=RateLimitTier.PROFESSIONAL,
        requests_per_hour=1000,
        burst_limit=100,
        window_size=3600
    ),
    RateLimitTier.ENTERPRISE: RateLimitConfig(
        tier=RateLimitTier.ENTERPRISE,
        requests_per_hour=0,  # 0 means unlimited
        burst_limit=0,
        window_size=3600
    )
}


class RateLimiter:
    """Redis-backed rate limiter with sliding window algorithm"""
    
    def __init__(self, redis_cache: RedisCache):
        self.redis = redis_cache
        self.scripts = {}
        
    async def _load_scripts(self):
        """Load Lua scripts for atomic operations"""
        # Lua script for atomic rate limit check and increment
        self.scripts['check_rate_limit'] = await self.redis.redis.script_load("""
        local key = KEYS[1]
        local window = tonumber(ARGV[1])
        local limit = tonumber(ARGV[2])
        local current_time = tonumber(ARGV[3])
        
        -- Remove old entries outside the window
        redis.call('ZREMRANGEBYSCORE', key, '-inf', current_time - window)
        
        -- Count current requests in window
        local current_count = redis.call('ZCARD', key)
        
        if limit > 0 and current_count >= limit then
            return {0, current_count} -- Rate limit exceeded
        end
        
        -- Add current request
        redis.call('ZADD', key, current_time, current_time)
        redis.call('EXPIRE', key, window)
        
        return {1, current_count + 1} -- Request allowed
        """)
    
    def _get_rate_limit_key(self, identifier: str, tier: RateLimitTier) -> str:
        """Generate rate limit key for user/IP and tier"""
        return f"rate_limit:{tier.value}:{identifier}"
    
    async def check_rate_limit(self, identifier: str, tier: RateLimitTier) -> Tuple[bool, Dict]:
        """
        Check if request is within rate limit
        Returns: (is_allowed, rate_limit_info)
        """
        try:
            config = RATE_LIMITS.get(tier, RATE_LIMITS[RateLimitTier.BASIC])
            
            # Enterprise tier has no limits
            if config.requests_per_hour == 0:
                return True, {
                    "limit": 0,
                    "current": 0,
                    "remaining": "unlimited",
                    "reset": None
                }
            
            key = self._get_rate_limit_key(identifier, tier)
            current_time = int(time.time())
            
            # Use Lua script for atomic operation
            if not self.scripts:
                await self._load_scripts()
            
            result = await self.redis.redis.evalsha(
                self.scripts['check_rate_limit'],
                1,  # Number of keys
                key,
                config.window_size,
                config.requests_per_hour,
                current_time
            )
            
            is_allowed = bool(result[0])
            current_count = result[1]
            
            rate_limit_info = {
                "limit": config.requests_per_hour,
                "current": current_count,
                "remaining": max(0, config.requests_per_hour - current_count),
                "reset": current_time + config.window_size
            }
            
            return is_allowed, rate_limit_info
            
        except Exception as e:
            logger.error("Rate limit check failed", error=str(e), identifier=identifier, tier=tier)
            # Fail open - allow request if rate limiter fails
            return True, {
                "limit": 0,
                "current": 0,
                "remaining": "unknown",
                "reset": None
            }


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to apply rate limiting to requests"""
    
    def __init__(self, app, rate_limiter: RateLimiter):
        super().__init__(app)
        self.rate_limiter = rate_limiter
        
        # Skip rate limiting for these paths
        self.skip_paths = {
            "/health",
            "/docs",
            "/openapi.json",
            "/redoc",
        }
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for certain paths
        if any(request.url.path.startswith(path) for path in self.skip_paths):
            return await call_next(request)
        
        # Get user identifier (user ID from token or IP address)
        identifier = await self._get_identifier(request)
        
        # Get user's subscription tier
        tier = await self._get_user_tier(request)
        
        # Check rate limit
        is_allowed, rate_limit_info = await self.rate_limiter.check_rate_limit(identifier, tier)
        
        if not is_allowed:
            # Rate limit exceeded
            headers = {
                "X-RateLimit-Limit": str(rate_limit_info["limit"]),
                "X-RateLimit-Remaining": str(rate_limit_info["remaining"]),
                "X-RateLimit-Reset": str(rate_limit_info["reset"]),
                "Retry-After": str(rate_limit_info["reset"] - int(time.time())),
            }
            
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded",
                    "error_code": "RATE_LIMIT_EXCEEDED",
                    "retry_after": rate_limit_info["reset"] - int(time.time())
                },
                headers=headers
            )
        
        # Proceed with request and add rate limit headers to response
        response = await call_next(request)
        
        # Add rate limit headers to successful responses
        response.headers.update({
            "X-RateLimit-Limit": str(rate_limit_info["limit"]),
            "X-RateLimit-Remaining": str(rate_limit_info["remaining"]),
            "X-RateLimit-Reset": str(rate_limit_info["reset"]),
        })
        
        return response
    
    async def _get_identifier(self, request: Request) -> str:
        """Get unique identifier for rate limiting (user ID or IP)"""
        # Try to get user ID from authenticated request
        if hasattr(request.state, 'user') and request.state.user:
            return str(request.state.user.id)
        
        # Fallback to IP address
        # Handle proxy headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host
    
    async def _get_user_tier(self, request: Request) -> RateLimitTier:
        """Determine user's subscription tier for rate limiting"""
        if hasattr(request.state, 'user') and request.state.user:
            user = request.state.user
            return RateLimitTier(user.subscription_tier)
        
        # Default to basic tier for unauthenticated requests
        return RateLimitTier.BASIC


# Convenience function to create rate limiter instance
async def create_rate_limiter(redis_cache: RedisCache) -> RateLimiter:
    """Create and initialize rate limiter"""
    rate_limiter = RateLimiter(redis_cache)
    return rate_limiter