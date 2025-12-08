"""
API dependencies for authentication, database, and other services
"""

from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import get_struct_logger
from app.core.security import (
    admin_or_researcher,
    all_users,
    basic_tier_required,
    decode_token,
    enterprise_tier_required,
    professional_tier_required,
)
from app.db.database import get_db
from app.models.user import User

logger = get_struct_logger(__name__)

# HTTP Bearer for token authentication
security = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get current authenticated user from JWT token"""
    
    # Check if authentication is required
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Decode token
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    
    from sqlalchemy.future import select
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    
    # Store user in request state for logging
    request.state.user = user
    request.state.user_id = user.id
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Ensure current user is active"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return current_user


class RoleDependency:
    """Dependency for role-based access control"""
    
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles
    
    async def __call__(self, user: User = Depends(get_current_active_user)) -> User:
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user


class SubscriptionDependency:
    """Dependency for subscription-based access control"""
    
    def __init__(self, required_tier: str):
        self.required_tier = required_tier
        self.tier_priority = {
            "basic": 1,
            "professional": 2,
            "enterprise": 3,
        }
    
    async def __call__(self, user: User = Depends(get_current_active_user)) -> User:
        user_priority = self.tier_priority.get(user.subscription_tier, 0)
        required_priority = self.tier_priority.get(self.required_tier, 0)
        
        if user_priority < required_priority:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"{self.required_tier.title()} subscription required",
            )
        return user


# Common dependencies
get_admin_user = RoleDependency(["admin"])
get_researcher_or_admin = RoleDependency(["admin", "researcher"])
get_any_authenticated_user = RoleDependency(["admin", "researcher", "viewer"])

get_basic_tier_user = SubscriptionDependency("basic")
get_professional_tier_user = SubscriptionDependency("professional")
get_enterprise_tier_user = SubscriptionDependency("enterprise")


class RateLimitDependency:
    """Rate limiting dependency"""
    
    def __init__(self, requests_per_minute: int = None):
        self.requests_per_minute = requests_per_minute or settings.RATE_LIMIT_PER_MINUTE
    
    async def __call__(self, request: Request) -> None:
        # This would typically use Redis for distributed rate limiting
        # For now, we'll implement a simple in-memory rate limiter
        
        client_ip = request.client.host if request.client else "unknown"
        
        # In a production environment, you would:
        # 1. Check Redis for rate limit counter
        # 2. Increment counter with TTL
        # 3. Check if limit exceeded
        
        # For this implementation, we'll just log the rate limit check
        logger.debug(
            "Rate limit check",
            extra={
                "client_ip": client_ip,
                "endpoint": request.url.path,
                "method": request.method,
            },
        )
        
        # TODO: Implement actual rate limiting with Redis
        pass


rate_limit = RateLimitDependency()


async def get_pagination_params(
    page: int = 1,
    size: int = settings.DEFAULT_PAGE_SIZE,
) -> dict:
    """Get pagination parameters"""
    
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Page must be greater than 0",
        )
    
    if size < 1 or size > settings.MAX_PAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Size must be between 1 and {settings.MAX_PAGE_SIZE}",
        )
    
    offset = (page - 1) * size
    
    return {
        "page": page,
        "size": size,
        "offset": offset,
    }


class CacheDependency:
    """Cache dependency for Redis caching"""
    
    def __init__(self, ttl: int = 3600):
        self.ttl = ttl
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        # This would use Redis in production
        # For now, return None to indicate cache miss
        return None
    
    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        """Set value in cache"""
        # This would use Redis in production
        pass
    
    async def delete(self, key: str) -> None:
        """Delete value from cache"""
        # This would use Redis in production
        pass


# Common cache dependencies
cache_short = CacheDependency(ttl=300)  # 5 minutes
cache_medium = CacheDependency(ttl=3600)  # 1 hour
cache_long = CacheDependency(ttl=86400)  # 24 hours