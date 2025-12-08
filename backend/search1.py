"""
Search and analysis schemas
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SearchFilters(BaseModel):
    """Search filters for analysis"""
    
    confidence_threshold: Optional[float] = Field(None, ge=0, le=100)
    patent_status: Optional[List[str]] = None
    clinical_phase: Optional[List[str]] = None
    market_size_min: Optional[float] = None


class AnalysisRequest(BaseModel):
    """Drug-cancer analysis request"""
    
    cancer_type: str = Field(..., description="Target cancer type")
    drug_name: Optional[str] = None
    molecular_target: Optional[str] = None
    model: str = Field(default="fast", regex="^(fast|research)$")
    filters: Optional[SearchFilters] = None


class AnalysisMatch(BaseModel):
    """Analysis result match"""
    
    drug_id: str
    drug_name: str
    drugbank_id: str
    primary_indication: str
    confidence_score: float
    evidence_strength: str
    mechanism_hypothesis: Optional[str] = None
    created_at: datetime


class AnalysisResponse(BaseModel):
    """Analysis response"""
    
    cancer_type: str
    model: str
    results_count: int
    matches: List[AnalysisMatch]
    analysis_timestamp: datetime


class SearchRequest(BaseModel):
    """General search request"""
    
    query: str
    type: str = Field(default="all", regex="^(drugs|cancers|all)$")
    limit: int = Field(default=10, ge=1, le=20)


class SearchHistoryResponse(BaseModel):
    """Search history item response"""
    
    id: str
    search_query: Dict[str, Any]
    results_count: int
    searched_at: datetime

    class Config:
        from_attributes = True