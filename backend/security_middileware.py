"""
Security middleware for OncoPurpose API
Implements CORS, security headers, and other security measures
"""

from typing import List, Optional

import structlog
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.config import settings

logger = structlog.get_logger()


class CORSMiddleware(BaseHTTPMiddleware):
    """CORS middleware with configurable origins"""
    
    def __init__(self, app, allowed_origins: List[str], allowed_methods: List[str] = None):
        super().__init__(app)
        self.allowed_origins = allowed_origins
        self.allowed_methods = allowed_methods or [
            "GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"
        ]
        self.allowed_headers = [
            "Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With",
            "X-CSRF-Token", "X-API-Key", "Cache-Control", "Pragma"
        ]
        self.exposed_headers = [
            "X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset",
            "X-Total-Count", "X-Page-Count", "X-Current-Page"
        ]
    
    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin")
        
        # Handle preflight OPTIONS request
        if request.method == "OPTIONS":
            response = Response(status_code=200)
            
            # Set CORS headers
            if origin and self._is_origin_allowed(origin):
                response.headers["Access-Control-Allow-Origin"] = origin
            else:
                response.headers["Access-Control-Allow-Origin"] = "*"
            
            response.headers["Access-Control-Allow-Methods"] = ", ".join(self.allowed_methods)
            response.headers["Access-Control-Allow-Headers"] = ", ".join(self.allowed_headers)
            response.headers["Access-Control-Expose-Headers"] = ", ".join(self.exposed_headers)
            response.headers["Access-Control-Max-Age"] = "86400"  # 24 hours
            response.headers["Access-Control-Allow-Credentials"] = "true"
            
            return response
        
        # Handle actual request
        response = await call_next(request)
        
        # Set CORS headers for response
        if origin and self._is_origin_allowed(origin):
            response.headers["Access-Control-Allow-Origin"] = origin
        else:
            response.headers["Access-Control-Allow-Origin"] = "*"
        
        response.headers["Access-Control-Expose-Headers"] = ", ".join(self.exposed_headers)
        response.headers["Access-Control-Allow-Credentials"] = "true"
        
        return response
    
    def _is_origin_allowed(self, origin: str) -> bool:
        """Check if origin is allowed"""
        if "*" in self.allowed_origins:
            return True
        
        return origin in self.allowed_origins


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    def __init__(self, app):
        super().__init__(app)
        self.security_headers = {
            # Prevent clickjacking attacks
            "X-Frame-Options": "DENY",
            
            # Prevent MIME type sniffing
            "X-Content-Type-Options": "nosniff",
            
            # Enable XSS protection (legacy browsers)
            "X-XSS-Protection": "1; mode=block",
            
            # Enforce HTTPS
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
            
            # Content Security Policy
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self'; media-src 'self'; object-src 'none'; child-src 'none'; frame-ancestors 'none'; base-uri 'self'; form-action 'self';",
            
            # Referrer policy
            "Referrer-Policy": "strict-origin-when-cross-origin",
            
            # Feature policy (legacy)
            "Feature-Policy": "camera 'none'; microphone 'none'; geolocation 'none';",
            
            # Permissions policy (modern)
            "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=(), usb=(), magnetometer=(), gyroscope=(), accelerometer=()",
        }
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        for header, value in self.security_headers.items():
            response.headers[header] = value
        
        return response


class RequestSizeMiddleware(BaseHTTPMiddleware):
    """Limit request body size"""
    
    def __init__(self, app, max_size: int = 10 * 1024 * 1024):  # 10MB default
        super().__init__(app)
        self.max_size = max_size
    
    async def dispatch(self, request: Request, call_next):
        # Skip size check for GET and HEAD requests
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return await call_next(request)
        
        # Check content-length header
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
                if size > self.max_size:
                    from fastapi import HTTPException
                    raise HTTPException(
                        status_code=413,
                        detail=f"Request body too large. Maximum size: {self.max_size} bytes"
                    )
            except ValueError:
                pass  # Invalid content-length header
        
        return await call_next(request)


class TimingAttackProtectionMiddleware(BaseHTTPMiddleware):
    """Protect against timing attacks by adding constant time delays"""
    
    def __init__(self, app, min_response_time: float = 0.1):  # 100ms minimum
        super().__init__(app)
        self.min_response_time = min_response_time
    
    async def dispatch(self, request: Request, call_next):
        import time
        import asyncio
        
        start_time = time.time()
        response = await call_next(request)
        end_time = time.time()
        
        actual_time = end_time - start_time
        
        # Add delay if response was too fast
        if actual_time < self.min_response_time:
            delay = self.min_response_time - actual_time
            await asyncio.sleep(delay)
        
        return response


class IPWhitelistMiddleware(BaseHTTPMiddleware):
    """IP whitelist middleware for admin endpoints"""
    
    def __init__(self, app, allowed_ips: List[str], admin_paths: List[str]):
        super().__init__(app)
        self.allowed_ips = set(allowed_ips)
        self.admin_paths = admin_paths
    
    async def dispatch(self, request: Request, call_next):
        # Check if this is an admin path
        is_admin_path = any(request.url.path.startswith(path) for path in self.admin_paths)
        
        if is_admin_path:
            # Get client IP
            client_ip = request.client.host
            forwarded_for = request.headers.get("X-Forwarded-For")
            if forwarded_for:
                client_ip = forwarded_for.split(",")[0].strip()
            
            # Check if IP is allowed
            if client_ip not in self.allowed_ips:
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=403,
                    detail="Access denied from this IP address"
                )
        
        return await call_next(request)


class APIKeyMiddleware(BaseHTTPMiddleware):
    """API key validation middleware"""
    
    def __init__(self, app, api_key_header: str = "X-API-Key", protected_paths: List[str] = None):
        super().__init__(app)
        self.api_key_header = api_key_header
        self.protected_paths = protected_paths or []
    
    async def dispatch(self, request: Request, call_next):
        # Check if this path requires API key
        requires_api_key = any(request.url.path.startswith(path) for path in self.protected_paths)
        
        if requires_api_key:
            api_key = request.headers.get(self.api_key_header)
            
            if not api_key:
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=401,
                    detail="API key required"
                )
            
            # Validate API key (in production, check against database)
            if not self._validate_api_key(api_key):
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=401,
                    detail="Invalid API key"
                )
            
            # Store validated API key in request state
            request.state.api_key = api_key
        
        return await call_next(request)
    
    def _validate_api_key(self, api_key: str) -> bool:
        """Validate API key (implement actual validation logic)"""
        # In production, this would check against a database
        # For now, just check against a hardcoded value
        return api_key == settings.API_KEY_SECRET


def create_security_middleware_stack(app, config):
    """Create and configure all security middleware"""
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allowed_origins=config.ALLOWED_ORIGINS,
        allowed_methods=config.ALLOWED_METHODS
    )
    
    # Security headers
    app.add_middleware(SecurityHeadersMiddleware)
    
    # Request size limiting
    app.add_middleware(RequestSizeMiddleware, max_size=config.MAX_REQUEST_SIZE)
    
    # Timing attack protection
    app.add_middleware(TimingAttackProtectionMiddleware, min_response_time=config.MIN_RESPONSE_TIME)
    
    # IP whitelist for admin endpoints (if configured)
    if config.ADMIN_IP_WHITELIST:
        app.add_middleware(
            IPWhitelistMiddleware,
            allowed_ips=config.ADMIN_IP_WHITELIST,
            admin_paths=["/admin", "/api/v1/admin"]
        )
    
    # API key protection (if configured)
    if config.API_KEY_PROTECTED_PATHS:
        app.add_middleware(
            APIKeyMiddleware,
            protected_paths=config.API_KEY_PROTECTED_PATHS
        )
    
    return app