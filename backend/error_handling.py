"""
Comprehensive error handling system for OncoPurpose API
Provides structured error responses and exception handling
"""

import traceback
from typing import Any, Dict, Optional, Type, Union
from enum import Enum

import structlog
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings

logger = structlog.get_logger()


class ErrorCode(str, Enum):
    """Standardized error codes"""
    # Authentication/Authorization
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    AUTHORIZATION_FAILED = "AUTHORIZATION_FAILED"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    TOKEN_INVALID = "TOKEN_INVALID"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    SUBSCRIPTION_REQUIRED = "SUBSCRIPTION_REQUIRED"
    
    # Validation
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    INVALID_FORMAT = "INVALID_FORMAT"
    
    # Business Logic
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_ALREADY_EXISTS = "RESOURCE_ALREADY_EXISTS"
    OPERATION_NOT_ALLOWED = "OPERATION_NOT_ALLOWED"
    
    # External Services
    EXTERNAL_API_ERROR = "EXTERNAL_API_ERROR"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    
    # Database
    DATABASE_ERROR = "DATABASE_ERROR"
    DUPLICATE_ENTRY = "DUPLICATE_ENTRY"
    
    # ML/Processing
    ML_MODEL_ERROR = "ML_MODEL_ERROR"
    INVALID_MOLECULE = "INVALID_MOLECULE"
    PREDICTION_FAILED = "PREDICTION_FAILED"
    
    # Generic
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    BAD_REQUEST = "BAD_REQUEST"
    NOT_FOUND = "NOT_FOUND"
    METHOD_NOT_ALLOWED = "METHOD_NOT_ALLOWED"


class ErrorDetail(BaseModel):
    """Structured error detail"""
    code: ErrorCode
    message: str
    details: Optional[Dict[str, Any]] = None
    field: Optional[str] = None
    help: Optional[str] = None


class APIException(HTTPException):
    """Custom API exception with structured error details"""
    
    def __init__(
        self,
        status_code: int,
        error_code: ErrorCode,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        field: Optional[str] = None,
        help: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        self.field = field
        self.help = help
        
        # Create structured error response
        error_detail = ErrorDetail(
            code=error_code,
            message=message,
            details=details,
            field=field,
            help=help
        )
        
        super().__init__(status_code=status_code, detail=error_detail.dict(), headers=headers)


class ValidationException(APIException):
    """Validation error exception"""
    
    def __init__(
        self,
        message: str = "Validation failed",
        field: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code=ErrorCode.VALIDATION_ERROR,
            message=message,
            field=field,
            details=details,
            help="Please check your input data and try again"
        )


class AuthenticationException(APIException):
    """Authentication error exception"""
    
    def __init__(
        self,
        message: str = "Authentication failed",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code=ErrorCode.AUTHENTICATION_FAILED,
            message=message,
            details=details,
            help="Please check your credentials and try again",
            headers={"WWW-Authenticate": "Bearer"}
        )


class AuthorizationException(APIException):
    """Authorization error exception"""
    
    def __init__(
        self,
        message: str = "Access denied",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            error_code=ErrorCode.AUTHORIZATION_FAILED,
            message=message,
            details=details,
            help="You don't have permission to access this resource"
        )


class NotFoundException(APIException):
    """Resource not found exception"""
    
    def __init__(
        self,
        resource: str,
        identifier: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        message = f"{resource} not found"
        if identifier:
            message += f": {identifier}"
        
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=ErrorCode.RESOURCE_NOT_FOUND,
            message=message,
            details=details,
            help="The requested resource could not be found"
        )


class ConflictException(APIException):
    """Resource conflict exception"""
    
    def __init__(
        self,
        resource: str,
        identifier: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        message = f"{resource} already exists"
        if identifier:
            message += f": {identifier}"
        
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            error_code=ErrorCode.RESOURCE_ALREADY_EXISTS,
            message=message,
            details=details,
            help="This resource already exists. Please use a different identifier"
        )


class ExternalAPIException(APIException):
    """External API error exception"""
    
    def __init__(
        self,
        service: str,
        message: str = "External service error",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code=ErrorCode.EXTERNAL_API_ERROR,
            message=f"{service} service error: {message}",
            details=details,
            help="Please try again later or contact support if the issue persists"
        )


class DatabaseException(APIException):
    """Database error exception"""
    
    def __init__(
        self,
        message: str = "Database operation failed",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=ErrorCode.DATABASE_ERROR,
            message=message,
            details=details,
            help="A database error occurred. Please try again later"
        )


class RateLimitException(APIException):
    """Rate limit exceeded exception"""
    
    def __init__(
        self,
        limit: int,
        reset_time: int,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code=ErrorCode.RATE_LIMIT_EXCEEDED,
            message="Rate limit exceeded",
            details=details,
            help=f"Please wait until {reset_time} before making more requests",
            headers={"Retry-After": str(reset_time)}
        )


class ErrorHandler:
    """Centralized error handling"""
    
    def __init__(self):
        self.error_mapping = {
            # SQLAlchemy errors
            "IntegrityError": self._handle_integrity_error,
            "DataError": self._handle_data_error,
            "DatabaseError": self._handle_database_error,
            "InvalidRequestError": self._handle_invalid_request_error,
            
            # FastAPI/Starlette errors
            "HTTPException": self._handle_http_exception,
            "RequestValidationError": self._handle_validation_error,
            
            # Custom API exceptions
            "APIException": self._handle_api_exception,
        }
    
    async def __call__(self, request: Request, call_next):
        """Middleware entry point"""
        try:
            return await call_next(request)
        except Exception as exc:
            return await self.handle_exception(exc, request)
    
    async def handle_exception(self, exc: Exception, request: Request) -> JSONResponse:
        """Handle any exception and return appropriate response"""
        
        # Log the exception
        logger.error(
            "Unhandled exception",
            error=str(exc),
            error_type=type(exc).__name__,
            path=request.url.path,
            method=request.method,
            traceback=traceback.format_exc() if settings.DEBUG else None
        )
        
        # Handle specific exception types
        handler = self.error_mapping.get(type(exc).__name__)
        if handler:
            return await handler(exc, request)
        
        # Default handler for unknown exceptions
        return await self._handle_generic_error(exc, request)
    
    async def _handle_api_exception(self, exc: APIException, request: Request) -> JSONResponse:
        """Handle custom API exceptions"""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.error_code.value,
                "message": exc.message,
                "details": exc.details,
                "field": exc.field,
                "help": exc.help
            },
            headers=exc.headers
        )
    
    async def _handle_http_exception(self, exc: HTTPException, request: Request) -> JSONResponse:
        """Handle FastAPI HTTP exceptions"""
        # Convert to our standard format
        error_code = self._map_status_code_to_error_code(exc.status_code)
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": error_code.value,
                "message": exc.detail,
                "details": None,
                "field": None,
                "help": self._get_help_message(error_code)
            }
        )
    
    async def _handle_validation_error(self, exc, request: Request) -> JSONResponse:
        """Handle Pydantic validation errors"""
        # Extract field errors
        field_errors = {}
        for error in exc.errors():
            field = " -> ".join(str(loc) for loc in error["loc"])
            field_errors[field] = error["msg"]
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": ErrorCode.VALIDATION_ERROR.value,
                "message": "Request validation failed",
                "details": {"fields": field_errors},
                "field": None,
                "help": "Please check your input data and try again"
            }
        )
    
    async def _handle_integrity_error(self, exc: SQLAlchemyError, request: Request) -> JSONResponse:
        """Handle database integrity errors (duplicates, constraints)"""
        error_msg = str(exc)
        
        if "duplicate" in error_msg.lower() or "unique" in error_msg.lower():
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content={
                    "error": ErrorCode.DUPLICATE_ENTRY.value,
                    "message": "Duplicate entry detected",
                    "details": {"database_error": error_msg},
                    "field": None,
                    "help": "This record already exists. Please use a different identifier"
                }
            )
        
        return await self._handle_database_error(exc, request)
    
    async def _handle_data_error(self, exc: SQLAlchemyError, request: Request) -> JSONResponse:
        """Handle database data errors"""
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": ErrorCode.INVALID_INPUT.value,
                "message": "Invalid data provided",
                "details": {"database_error": str(exc)},
                "field": None,
                "help": "Please check your input data and try again"
            }
        )
    
    async def _handle_database_error(self, exc: SQLAlchemyError, request: Request) -> JSONResponse:
        """Handle generic database errors"""
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": ErrorCode.DATABASE_ERROR.value,
                "message": "Database operation failed",
                "details": {"database_error": str(exc) if settings.DEBUG else None},
                "field": None,
                "help": "A database error occurred. Please try again later"
            }
        )
    
    async def _handle_invalid_request_error(self, exc: SQLAlchemyError, request: Request) -> JSONResponse:
        """Handle invalid database request errors"""
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": ErrorCode.BAD_REQUEST.value,
                "message": "Invalid request",
                "details": {"database_error": str(exc)},
                "field": None,
                "help": "Please check your request and try again"
            }
        )
    
    async def _handle_generic_error(self, exc: Exception, request: Request) -> JSONResponse:
        """Handle generic/unexpected errors"""
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": ErrorCode.INTERNAL_SERVER_ERROR.value,
                "message": "An internal server error occurred",
                "details": {
                    "error_type": type(exc).__name__,
                    "error_message": str(exc) if settings.DEBUG else None
                },
                "field": None,
                "help": "Please try again later or contact support if the issue persists"
            }
        )
    
    def _map_status_code_to_error_code(self, status_code: int) -> ErrorCode:
        """Map HTTP status codes to error codes"""
        mapping = {
            400: ErrorCode.BAD_REQUEST,
            401: ErrorCode.AUTHENTICATION_FAILED,
            403: ErrorCode.AUTHORIZATION_FAILED,
            404: ErrorCode.NOT_FOUND,
            405: ErrorCode.METHOD_NOT_ALLOWED,
            409: ErrorCode.RESOURCE_ALREADY_EXISTS,
            422: ErrorCode.VALIDATION_ERROR,
            429: ErrorCode.RATE_LIMIT_EXCEEDED,
            500: ErrorCode.INTERNAL_SERVER_ERROR,
            503: ErrorCode.SERVICE_UNAVAILABLE,
        }
        
        return mapping.get(status_code, ErrorCode.INTERNAL_SERVER_ERROR)
    
    def _get_help_message(self, error_code: ErrorCode) -> str:
        """Get help message for error code"""
        help_messages = {
            ErrorCode.AUTHENTICATION_FAILED: "Please check your credentials and try again",
            ErrorCode.AUTHORIZATION_FAILED: "You don't have permission to access this resource",
            ErrorCode.VALIDATION_ERROR: "Please check your input data and try again",
            ErrorCode.RESOURCE_NOT_FOUND: "The requested resource could not be found",
            ErrorCode.RESOURCE_ALREADY_EXISTS: "This resource already exists. Please use a different identifier",
            ErrorCode.RATE_LIMIT_EXCEEDED: "Please wait before making more requests",
            ErrorCode.INTERNAL_SERVER_ERROR: "Please try again later or contact support if the issue persists",
        }
        
        return help_messages.get(error_code, "Please try again or contact support")


# Global error handler instance
error_handler = ErrorHandler()