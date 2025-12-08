"""
Authentication API endpoints
"""

# Copyright (c) 2025 OncoPurpose (trovesx)
# All Rights Reserved.
# For licensing info, see LICENSE or contact oncopurpose@trovesx.com

from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.dependencies import get_current_user
from app.core.config import settings
from app.core.logging import get_struct_logger
from app.core.security import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
)
from app.db.database import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RegisterRequest,
    RegisterResponse,
    UserProfileResponse,
)
from app.schemas.common import ErrorResponse

logger = get_struct_logger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=RegisterResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad request"},
        409: {"model": ErrorResponse, "description": "User already exists"},
    },
)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> RegisterResponse:
    """Register a new user"""
    
    from sqlalchemy.future import select
    from sqlalchemy.exc import IntegrityError
    
    try:
        # Check if user already exists
        existing_user = await db.execute(
            select(User).where(User.email == request.email)
        )
        if existing_user.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists",
            )
        
        # Create new user
        user = User(
            email=request.email,
            password_hash=get_password_hash(request.password),
            full_name=request.full_name,
            company_name=request.company_name,
            role=request.role or "researcher",
            subscription_tier=request.subscription_tier or "basic",
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        logger.info(
            "User registered successfully",
            extra={"user_id": str(user.id), "email": user.email},
        )
        
        return RegisterResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            company_name=user.company_name,
            role=user.role,
            subscription_tier=user.subscription_tier,
            created_at=user.created_at,
        )
        
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )
    except Exception as e:
        await db.rollback()
        logger.error("Registration error", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed",
        )


@router.post(
    "/login",
    response_model=LoginResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid credentials"},
    },
)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    """Login user and return access tokens"""
    
    # Authenticate user
    user = await authenticate_user(db, request.email, request.password)
    if not user:
        logger.warning(
            "Failed login attempt",
            extra={"email": request.email},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    from datetime import datetime
    
    user.last_login = datetime.utcnow()
    db.add(user)
    await db.commit()
    
    # Create tokens with jti for revocation support
    import uuid

    jti = str(uuid.uuid4())
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
        "subscription_tier": user.subscription_tier,
        "jti": jti,
    }

    access_token = create_access_token(token_data)
    refresh_token = await create_refresh_token(token_data)

    # Store refresh token metadata in Redis for revocation and rotation
    try:
        from app.redis_cache import redis_cache

        if await redis_cache.connect():
            # Use a simple key: refresh:{jti} -> user_id
            await redis_cache.set(f"refresh:{jti}", {"user_id": str(user.id)}, ttl=60 * 60 * 24 * settings.REFRESH_TOKEN_EXPIRE_DAYS)
    except Exception:
        # Log but do not fail authentication if Redis is unavailable
        logger.warning("Failed to store refresh token metadata in Redis")
    
    logger.info(
        "User logged in successfully",
        extra={"user_id": str(user.id), "email": user.email},
    )
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserProfileResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            company_name=user.company_name,
            role=user.role,
            subscription_tier=user.subscription_tier,
            created_at=user.created_at,
            last_login=user.last_login,
        ),
    )


@router.post(
    "/token",
    response_model=LoginResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid credentials"},
    },
)
async def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    """OAuth2 compatible token login"""
    
    login_request = LoginRequest(
        email=form_data.username,
        password=form_data.password,
    )
    
    return await login(login_request, db)


@router.post(
    "/refresh",
    response_model=LoginResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid refresh token"},
    },
)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    """Refresh access token using refresh token"""
    
    # Decode refresh token and check revocation via Redis
    payload = decode_token(request.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user
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
    
    # Check refresh token jti against Redis revocation list
    jti = payload.get("jti")
    try:
        from app.redis_cache import redis_cache

        if await redis_cache.connect():
            exists = await redis_cache.get(f"refresh:{jti}")
            if not exists:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Refresh token revoked or not found",
                )
            # Rotate: delete old jti and create a new one
            await redis_cache.delete(f"refresh:{jti}")
            import uuid
            new_jti = str(uuid.uuid4())
            token_data = {
                "sub": str(user.id),
                "email": user.email,
                "role": user.role,
                "subscription_tier": user.subscription_tier,
                "jti": new_jti,
            }
            access_token = create_access_token(token_data)
            refresh_token = await create_refresh_token(token_data)
            await redis_cache.set(f"refresh:{new_jti}", {"user_id": str(user.id)}, ttl=60 * 60 * 24 * settings.REFRESH_TOKEN_EXPIRE_DAYS)
    except HTTPException:
        raise
    except Exception:
        # If Redis is unavailable, allow refresh but log warning
        logger.warning("Redis unavailable during refresh token check; allowing refresh")
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
            "subscription_tier": user.subscription_tier,
        }
        access_token = create_access_token(token_data)
        refresh_token = await create_refresh_token(token_data)
    
    logger.info(
        "Token refreshed successfully",
        extra={"user_id": str(user.id), "email": user.email},
    )
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserProfileResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            company_name=user.company_name,
            role=user.role,
            subscription_tier=user.subscription_tier,
            created_at=user.created_at,
            last_login=user.last_login,
        ),
    )


@router.post("/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    """Logout user (client-side token invalidation)"""
    
    logger.info(
        "User logged out",
        extra={"user_id": str(current_user.id), "email": current_user.email},
    )
    # Attempt to revoke refresh token by deleting JTI from Redis
    try:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]
            payload = decode_token(token)
            jti = payload.get("jti") if payload else None
            if jti:
                from app.redis_cache import redis_cache
                if await redis_cache.connect():
                    await redis_cache.delete(f"refresh:{jti}")
    except Exception:
        logger.warning("Failed to revoke refresh token on logout")

    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserProfileResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
) -> UserProfileResponse:
    """Get current user profile"""
    
    return UserProfileResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        company_name=current_user.company_name,
        role=current_user.role,
        subscription_tier=current_user.subscription_tier,
        created_at=current_user.created_at,
        last_login=current_user.last_login,
    )