"""
Common schemas used across the API
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standard error response format"""
    
    error: "ErrorDetail"


class ErrorDetail(BaseModel):
    """Error detail structure"""
    
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None


class PaginationParams(BaseModel):
    """Pagination parameters"""
    
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)


class PaginatedResponse(BaseModel):
    """Paginated response wrapper"""
    
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int


class SearchFilters(BaseModel):
    """Common search filters"""
    
    query: Optional[str] = None
    sort_by: Optional[str] = "created_at"
    sort_order: Optional[str] = "desc"  # asc or desc
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


class HealthCheck(BaseModel):
    """Health check response"""
    
    status: str
    version: str
    environment: str
    timestamp: datetime
    database: Optional[str] = None
    cache: Optional[str] = None