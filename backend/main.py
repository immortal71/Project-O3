"""
OncoPurpose Backend API
Production-ready FastAPI application for oncology drug repurposing platform
"""

# Copyright (c) 2025 OncoPurpose (trovesx)
# All Rights Reserved.
# For licensing info, see LICENSE or contact oncopurpose@trovesx.com

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sqlalchemy.exc import SQLAlchemyError
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.database import engine
from app.db.init_db import init_db
from app.redis_cache import redis_cache
from app.models.base import Base
from app.redis_cache import redis_cache
from image_api import router as image_router
from discovery_api import router as discovery_router

# Setup structured logging
setup_logging()
logger = logging.getLogger(__name__)

# Sentry configuration for error tracking
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
        ],
        traces_sample_rate=0.1,
        profiles_sample_rate=0.1,
    )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager"""
    # Startup
    logger.info("Starting OncoPurpose API", extra={"environment": settings.ENVIRONMENT})
    
    # Connect to Redis cache (optional)
    try:
        await redis_cache.connect()
    except Exception:
        logger.warning("Redis connection failed during startup; continuing without cache")
    
    # Initialize database tables
    async with engine.begin() as conn:
        # Create all tables (in production, use migrations)
        await conn.run_sync(Base.metadata.create_all)
    
    # Initialize database with seed data if needed
    await init_db()
    # Connect to Redis cache if available
    try:
        await redis_cache.connect()
    except Exception:
        logger.warning("Redis connect failed during startup; continuing without Redis")
    
    logger.info("Database initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down OncoPurpose API")
    try:
        await engine.dispose()
    finally:
        try:
            await redis_cache.disconnect()
        except Exception:
            logger.warning("Redis disconnect failed during shutdown")


# Create FastAPI application
app = FastAPI(
    title="OncoPurpose API",
    description="Production-ready backend API for oncology drug repurposing platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count", "X-RateLimit-Remaining", "X-RateLimit-Reset"],
)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging"""
    
    async def dispatch(self, request: Request, call_next):
        # Log incoming request
        logger.info(
            "Incoming request",
            extra={
                "method": request.method,
                "url": str(request.url),
                "user_agent": request.headers.get("user-agent"),
                "ip": request.client.host if request.client else None,
            }
        )
        
        try:
            response = await call_next(request)
            
            # Log successful response
            logger.info(
                "Request completed",
                extra={
                    "method": request.method,
                    "url": str(request.url),
                    "status_code": response.status_code,
                }
            )
            
            return response
            
        except Exception as exc:
            # Log error
            logger.error(
                "Request failed",
                extra={
                    "method": request.method,
                    "url": str(request.url),
                    "error": str(exc),
                },
                exc_info=True,
            )
            raise


# Add logging middleware
app.add_middleware(LoggingMiddleware)


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle database errors"""
    logger.error(
        "Database error occurred",
        extra={
            "method": request.method,
            "url": str(request.url),
            "error": str(exc),
        },
        exc_info=True,
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "DATABASE_ERROR",
                "message": "A database error occurred. Please try again later.",
                "details": None,
                "timestamp": request.state.request_id if hasattr(request.state, "request_id") else None,
            }
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(
        "Unhandled exception occurred",
        extra={
            "method": request.method,
            "url": str(request.url),
            "error": str(exc),
        },
        exc_info=True,
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An internal error occurred. Please try again later.",
                "details": None,
                "timestamp": request.state.request_id if hasattr(request.state, "request_id") else None,
            }
        },
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "timestamp": "2024-01-01T00:00:00Z",
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to OncoPurpose API",
        "version": "1.0.0",
        "documentation": "/docs" if settings.ENVIRONMENT == "development" else None,
        "health": "/health",
    }


# Include API routes
app.include_router(api_router, prefix="/api/v1")
app.include_router(discovery_router)  # Discovery analysis endpoints
app.include_router(image_router)  # Image generation endpoints

# Mount Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
        workers=1 if settings.ENVIRONMENT == "development" else 4,
        log_level=settings.LOG_LEVEL.lower(),
    )