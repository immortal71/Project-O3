"""
Logging and monitoring configuration for OncoPurpose API
Implements structured logging with structlog and monitoring integration
"""

import json
import sys
import time
from datetime import datetime
from typing import Any, Dict, Optional

import structlog
from fastapi import Request
from prometheus_client import Counter, Histogram, Gauge, Info
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings


# Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code', 'user_tier']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint', 'status_code']
)

ACTIVE_REQUESTS = Gauge(
    'http_requests_active',
    'Number of active HTTP requests'
)

ERROR_COUNT = Counter(
    'http_errors_total',
    'Total HTTP errors',
    ['method', 'endpoint', 'error_code', 'status_code']
)

BUSINESS_METRICS = Counter(
    'business_events_total',
    'Business events counter',
    ['event_type', 'user_tier', 'outcome']
)

# System info
SYSTEM_INFO = Info('onc-purpose_system', 'System information')
SYSTEM_INFO.info({
    'version': '1.0.0',
    'environment': settings.ENVIRONMENT,
    'python_version': sys.version.split()[0]
})


class LoggingConfig:
    """Logging configuration"""
    
    @staticmethod
    def configure_logging():
        """Configure structured logging"""
        
        # Configure structlog
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        
        # Configure standard library logging
        import logging
        
        # Set up handlers
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        )
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
        root_logger.addHandler(handler)
        
        # Configure specific loggers
        loggers = [
            'uvicorn',
            'uvicorn.access',
            'fastapi',
            'sqlalchemy.engine',
            'app'
        ]
        
        for logger_name in loggers:
            logger = logging.getLogger(logger_name)
            logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
        
        return structlog.get_logger()


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for collecting Prometheus metrics"""
    
    async def dispatch(self, request: Request, call_next):
        # Increment active requests
        ACTIVE_REQUESTS.inc()
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Get user tier if available
            user_tier = "anonymous"
            if hasattr(request.state, 'user') and request.state.user:
                user_tier = request.state.user.subscription_tier
            
            # Record metrics
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                status_code=response.status_code,
                user_tier=user_tier
            ).inc()
            
            duration = time.time() - start_time
            REQUEST_DURATION.labels(
                method=request.method,
                endpoint=request.url.path,
                status_code=response.status_code
            ).observe(duration)
            
            # Record errors
            if response.status_code >= 400:
                ERROR_COUNT.labels(
                    method=request.method,
                    endpoint=request.url.path,
                    error_code=getattr(response, 'error_code', 'UNKNOWN'),
                    status_code=response.status_code
                ).inc()
            
            return response
            
        finally:
            # Decrement active requests
            ACTIVE_REQUESTS.dec()


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging"""
    
    def __init__(self, app, logger):
        super().__init__(app)
        self.logger = logger
    
    async def dispatch(self, request: Request, call_next):
        # Log incoming request
        self.logger.info(
            "Incoming request",
            method=request.method,
            path=request.url.path,
            query_params=dict(request.query_params),
            client_ip=request.client.host,
            user_agent=request.headers.get("user-agent", "unknown")
        )
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Log successful response
            duration = time.time() - start_time
            self.logger.info(
                "Request completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration=duration,
                content_length=response.headers.get("content-length")
            )
            
            return response
            
        except Exception as exc:
            # Log error
            duration = time.time() - start_time
            self.logger.error(
                "Request failed",
                method=request.method,
                path=request.url.path,
                error=str(exc),
                error_type=type(exc).__name__,
                duration=duration,
                traceback=traceback.format_exc() if settings.DEBUG else None
            )
            
            raise


class BusinessMetrics:
    """Track business-specific metrics"""
    
    @staticmethod
    def track_event(
        event_type: str,
        user_tier: str = "anonymous",
        outcome: str = "success",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Track a business event"""
        BUSINESS_METRICS.labels(
            event_type=event_type,
            user_tier=user_tier,
            outcome=outcome
        ).inc()
        
        # Log the event
        logger.info(
            "Business event tracked",
            event_type=event_type,
            user_tier=user_tier,
            outcome=outcome,
            metadata=metadata or {}
        )
    
    @staticmethod
    def track_prediction(
        user_tier: str,
        prediction_type: str,
        success: bool,
        duration: Optional[float] = None
    ):
        """Track ML prediction metrics"""
        outcome = "success" if success else "failure"
        BusinessMetrics.track_event(
            event_type=f"prediction_{prediction_type}",
            user_tier=user_tier,
            outcome=outcome,
            metadata={"duration": duration} if duration else None
        )
    
    @staticmethod
    def track_search(
        user_tier: str,
        search_type: str,
        result_count: int,
        success: bool
    ):
        """Track search metrics"""
        outcome = "success" if success else "failure"
        BusinessMetrics.track_event(
            event_type=f"search_{search_type}",
            user_tier=user_tier,
            outcome=outcome,
            metadata={"result_count": result_count}
        )
    
    @staticmethod
    def track_external_api_call(
        service: str,
        user_tier: str,
        success: bool,
        duration: Optional[float] = None
    ):
        """Track external API calls"""
        outcome = "success" if success else "failure"
        BusinessMetrics.track_event(
            event_type=f"api_call_{service}",
            user_tier=user_tier,
            outcome=outcome,
            metadata={"duration": duration} if duration else None
        )


class HealthCheckLogger:
    """Health check logging utilities"""
    
    @staticmethod
    def log_health_check(
        status: str,
        checks: Dict[str, Any],
        duration: float
    ):
        """Log health check results"""
        logger.info(
            "Health check completed",
            status=status,
            checks=checks,
            duration=duration
        )
        
        # Track health check metrics
        BusinessMetrics.track_event(
            event_type="health_check",
            outcome=status,
            metadata={
                "duration": duration,
                "checks": checks
            }
        )


class PerformanceProfiler:
    """Performance profiling utilities"""
    
    def __init__(self, logger, threshold: float = 1.0):
        self.logger = logger
        self.threshold = threshold  # Log operations slower than this (seconds)
    
    def profile_operation(self, operation_name: str):
        """Context manager for profiling operations"""
        return OperationProfiler(self.logger, operation_name, self.threshold)


class OperationProfiler:
    """Context manager for profiling individual operations"""
    
    def __init__(self, logger, operation_name: str, threshold: float):
        self.logger = logger
        self.operation_name = operation_name
        self.threshold = threshold
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        
        if duration > self.threshold or exc_type is not None:
            self.logger.warning(
                "Slow operation detected",
                operation=self.operation_name,
                duration=duration,
                error=str(exc_val) if exc_val else None
            )
        
        # Log all operations in debug mode
        if settings.DEBUG:
            self.logger.debug(
                "Operation completed",
                operation=self.operation_name,
                duration=duration
            )


# Initialize logging
logger = LoggingConfig.configure_logging()


# Convenience functions
def get_logger(name: str = None):
    """Get a structured logger"""
    if name:
        return structlog.get_logger(name)
    return logger


def log_api_call(
    endpoint: str,
    method: str,
    user_id: Optional[str] = None,
    duration: Optional[float] = None,
    status_code: Optional[int] = None,
    error: Optional[str] = None
):
    """Log API call details"""
    logger.info(
        "API call",
        endpoint=endpoint,
        method=method,
        user_id=user_id,
        duration=duration,
        status_code=status_code,
        error=error
    )


def log_security_event(
    event_type: str,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
):
    """Log security-related events"""
    logger.warning(
        "Security event",
        event_type=event_type,
        user_id=user_id,
        ip_address=ip_address,
        details=details or {}
    )


def log_ml_event(
    event_type: str,
    model_name: Optional[str] = None,
    duration: Optional[float] = None,
    success: bool = True,
    metadata: Optional[Dict[str, Any]] = None
):
    """Log ML-related events"""
    logger.info(
        "ML event",
        event_type=event_type,
        model_name=model_name,
        duration=duration,
        success=success,
        metadata=metadata or {}
    )