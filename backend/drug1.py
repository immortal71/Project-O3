"""
Drug-related schemas
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class DrugBase(BaseModel):
    """Base drug schema"""
    
    drug_name: str
    drugbank_id: str
    pubchem_id: Optional[str] = None
    chemical_structure: Optional[str] = None
    molecular_weight: Optional[float] = None
    primary_indication: str
    approval_status: Optional[str] = None
    patent_expiry_date: Optional[date] = None
    manufacturer: Optional[str] = None
    mechanism_of_action: Optional[str] = None
    drug_class: Optional[str] = None


class DrugResponse(DrugBase):
    """Drug response schema"""
    
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DrugDetailResponse(DrugResponse):
    """Detailed drug response with related data"""
    
    predictions: List["DrugPredictionResponse"] = []
    safety_profiles: List["SafetyProfileResponse"] = []
    dosing_recommendations: List["DosingRecommendationResponse"] = []
    patents: List["PatentResponse"] = []
    clinical_trials: List["ClinicalTrialResponse"] = []


class DrugPredictionResponse(BaseModel):
    """Drug prediction response"""
    
    id: str
    cancer_type: str
    confidence_score: float
    evidence_strength: str
    mechanism_hypothesis: Optional[str] = None
    predicted_efficacy: Optional[str] = None
    safety_concerns: Optional[List[str]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class SafetyProfileResponse(BaseModel):
    """Safety profile response"""
    
    id: str
    adverse_events: Optional[List[Dict[str, Any]]] = None
    contraindications: Optional[List[str]] = None
    drug_interactions: Optional[List[str]] = None
    black_box_warnings: Optional[str] = None
    monitoring_requirements: Optional[List[str]] = None
    pregnancy_category: Optional[str] = None
    hepatic_impairment_guidance: Optional[str] = None
    renal_impairment_guidance: Optional[str] = None
    
    class Config:
        from_attributes = True


class DosingRecommendationResponse(BaseModel):
    """Dosing recommendation response"""
    
    id: str
    cancer_type: str
    recommended_dose: str
    dose_unit: str
    frequency: str
    route_of_administration: str
    duration_weeks: Optional[int] = None
    based_on_indication: str
    source_references: Optional[List[str]] = None
    
    class Config:
        from_attributes = True


class PatentResponse(BaseModel):
    """Patent response"""
    
    id: str
    patent_number: str
    patent_title: str
    filing_date: Optional[date] = None
    grant_date: Optional[date] = None
    expiry_date: Optional[date] = None
    patent_status: str
    assignee: str
    claims: Optional[str] = None
    patent_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class ClinicalTrialResponse(BaseModel):
    """Clinical trial response"""
    
    id: str
    nct_id: str
    title: str
    status: str
    phase: str
    sponsor: str
    start_date: Optional[date] = None
    completion_date: Optional[date] = None
    enrollment_count: Optional[int] = None
    primary_outcome: Optional[str] = None
    results_summary: Optional[str] = None
    trial_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class DrugListResponse(BaseModel):
    """Paginated drug list response"""
    
    items: List[DrugResponse]
    total: int
    page: int
    size: int
    pages: int


class DrugSearchRequest(BaseModel):
    """Drug search request"""
    
    query: Optional[str] = None
    drug_name: Optional[str] = None
    drugbank_id: Optional[str] = None
    indication: Optional[str] = None
    drug_class: Optional[str] = None
    approval_status: Optional[str] = None
    
    # Pagination
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)
    
    # Sorting
    sort_by: Optional[str] = "drug_name"
    sort_order: Optional[str] = "asc"  # asc or desc