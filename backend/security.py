"""
Security utilities for authentication and authorization
"""

# Copyright (c) 2025 OncoPurpose (trovesx)
# All Rights Reserved.
# For licensing info, see LICENSE or contact oncopurpose@trovesx.com

from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from uuid import uuid4
import asyncio
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import settings
from app.core.logging import get_struct_logger
from app.models.user import User

logger = get_struct_logger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({"exp": expire, "type": "access"})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    
    return encoded_jwt


async def create_refresh_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create JWT refresh token with `jti` and store it in Redis for revocation/rotation.

    Returns the encoded JWT string.
    """
    to_encode = data.copy()
    jti = uuid4().hex
    to_encode.update({"jti": jti})

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

    to_encode.update({"exp": expire, "type": "refresh"})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    # Attempt to persist the refresh token jti in Redis for revocation.
    try:
        # Import lazily (app shim maps to backend.redis_cache)
        from app.redis_cache import redis_cache

        ttl_seconds = int((expire - datetime.utcnow()).total_seconds())
        if redis_cache and redis_cache.is_connected:
            # Store mapping refresh:<jti> -> sub (user id)
            # Use set with TTL
            # redis_cache.set is async
            await redis_cache.set(f"refresh:{jti}", str(data.get("sub")), ttl=ttl_seconds)
    except Exception:
        # If Redis is not available or storage fails, continue — tokens still issued
        pass

    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """Decode JWT token and return payload"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return payload
    except JWTError as e:
        logger.warning("Invalid token", extra={"error": str(e)})
        return None


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Get user by email address"""
    try:
        result = await db.execute(
            select(User).where(User.email == email, User.is_active == True)
        )
        return result.scalar_one_or_none()
    except Exception as e:
        logger.error("Error getting user by email", extra={"error": str(e)})
        return None


async def authenticate_user(
    db: AsyncSession,
    email: str,
    password: str,
) -> Optional[User]:
    """Authenticate user with email and password"""
    user = await get_user_by_email(db, email)
    if not user:
        return None
    
    if not verify_password(password, user.password_hash):
        return None
    
    return user


class RoleChecker:
    """Role-based access control"""
    
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles
    
    def __call__(self, user: User) -> bool:
        """Check if user has required role"""
        return user.role in self.allowed_roles


# Role checkers for common permissions
admin_only = RoleChecker(["admin"])
admin_or_researcher = RoleChecker(["admin", "researcher"])
all_users = RoleChecker(["admin", "researcher", "viewer"])


class SubscriptionChecker:
    """Subscription-based access control"""
    
    def __init__(self, required_tier: str):
        self.required_tier = required_tier
        self.tier_priority = {
            "basic": 1,
            "professional": 2,
            "enterprise": 3,
        }
    
    def __call__(self, user: User) -> bool:
        """Check if user has required subscription tier"""
        user_priority = self.tier_priority.get(user.subscription_tier, 0)
        required_priority = self.tier_priority.get(self.required_tier, 0)
        return user_priority >= required_priority


# Subscription checkers
basic_tier_required = SubscriptionChecker("basic")
professional_tier_required = SubscriptionChecker("professional")
enterprise_tier_required = SubscriptionChecker("enterprise")