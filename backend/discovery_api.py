"""
Discovery API Endpoints
Handles drug repurposing analysis requests
"""

# Copyright (c) 2025 OncoPurpose (trovesx)
# All Rights Reserved.
# For licensing info, see LICENSE or contact oncopurpose@trovesx.com

import logging
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field, validator

from config import Settings, get_settings
from openai_service import get_openai_service, OpenAIService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/discovery", tags=["Discovery"])


# Request/Response Models
class AnalysisFilters(BaseModel):
    """Advanced analysis filters"""
    clinical_trials: bool = True
    preclinical_studies: bool = True
    mechanism_based: bool = True
    safety_data: bool = True


class AnalysisRequest(BaseModel):
    """Drug repurposing analysis request"""
    cancer_type: str = Field(..., description="Type of cancer")
    drug_name: str = Field(..., description="Name of drug to analyze")
    molecular_target: Optional[str] = Field(None, description="Molecular target")
    current_indication: Optional[str] = Field(None, description="Current indication")
    analysis_mode: str = Field(default="fast", description="Analysis mode: fast or deep")
    confidence_threshold: float = Field(default=70, ge=0, le=100)
    filters: Optional[AnalysisFilters] = None
    
    @validator("cancer_type", "drug_name")
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()
    
    @validator("analysis_mode")
    def valid_mode(cls, v):
        if v.lower() not in ["fast", "deep"]:
            raise ValueError("Analysis mode must be 'fast' or 'deep'")
        return v.lower()


class OpportunityResult(BaseModel):
    """Single repurposing opportunity"""
    drug_name: str
    cancer_type: str
    confidence_score: float
    mechanism_of_action: str
    evidence_summary: str
    safety_profile: str
    market_opportunity: Optional[str] = None
    recommendation: str
    key_findings: List[str] = []


class AnalysisResponse(BaseModel):
    """Analysis response"""
    success: bool
    analysis_mode: str
    model_used: str
    tokens_used: int
    result: Dict[str, Any]
    message: Optional[str] = None


class DrugSummaryRequest(BaseModel):
    """Request for drug summary"""
    drug_name: str = Field(..., description="Name of the drug")


class DrugSummaryResponse(BaseModel):
    """Drug summary response"""
    drug_name: str
    drug_class: str
    mechanism: str
    indications: List[str]
    side_effects: List[str]


# Dependency
def get_openai_service_dep(
    settings: Settings = Depends(get_settings)
) -> OpenAIService:
    """Dependency to get OpenAI service"""
    return get_openai_service(settings)


# Endpoints
@router.post("/analyze", response_model=AnalysisResponse, status_code=status.HTTP_200_OK)
async def analyze_drug_repurposing(
    request: AnalysisRequest,
    openai_service: OpenAIService = Depends(get_openai_service_dep)
) -> AnalysisResponse:
    """
    Analyze drug repurposing potential
    
    Uses OpenAI to analyze the potential of repurposing a specific drug
    for a given cancer type. Returns confidence scores, mechanisms,
    evidence summary, and recommendations.
    
    - **cancer_type**: Type of cancer to target
    - **drug_name**: Name of the drug to analyze
    - **molecular_target**: Optional molecular target
    - **current_indication**: Current approved indication
    - **analysis_mode**: 'fast' for quick analysis, 'deep' for comprehensive
    - **confidence_threshold**: Minimum confidence score filter (0-100)
    """
    try:
        logger.info(
            f"Received analysis request",
            extra={
                "drug_name": request.drug_name,
                "cancer_type": request.cancer_type,
                "analysis_mode": request.analysis_mode
            }
        )
        
        # Call OpenAI service
        result = await openai_service.analyze_drug_repurposing(
            drug_name=request.drug_name,
            cancer_type=request.cancer_type,
            molecular_target=request.molecular_target,
            current_indication=request.current_indication,
            analysis_mode=request.analysis_mode
        )
        
        # Check confidence threshold
        confidence = result.get("confidence_score", 0)
        if confidence < request.confidence_threshold:
            logger.info(
                f"Analysis confidence {confidence} below threshold {request.confidence_threshold}"
            )
            return AnalysisResponse(
                success=True,
                analysis_mode=request.analysis_mode,
                model_used=result.get("model_used", "gpt-4"),
                tokens_used=result.get("tokens_used", 0),
                result=result,
                message=f"Confidence score ({confidence}%) is below threshold ({request.confidence_threshold}%). Consider reviewing parameters."
            )
        
        logger.info(
            f"Analysis completed successfully",
            extra={
                "drug_name": request.drug_name,
                "confidence_score": confidence
            }
        )
        
        return AnalysisResponse(
            success=True,
            analysis_mode=request.analysis_mode,
            model_used=result.get("model_used", "gpt-4"),
            tokens_used=result.get("tokens_used", 0),
            result=result,
            message="Analysis completed successfully"
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "VALIDATION_ERROR",
                "message": str(e)
            }
        )
    
    except Exception as e:
        logger.error(f"Error analyzing drug repurposing: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "ANALYSIS_ERROR",
                "message": "Failed to analyze drug repurposing. Please try again."
            }
        )


@router.post("/drug-summary", response_model=DrugSummaryResponse)
async def get_drug_summary(
    request: DrugSummaryRequest,
    openai_service: OpenAIService = Depends(get_openai_service_dep)
) -> DrugSummaryResponse:
    """
    Get a brief summary of a drug
    
    Returns basic information about a drug including class, mechanism,
    approved indications, and common side effects.
    """
    try:
        result = await openai_service.generate_drug_summary(request.drug_name)
        
        return DrugSummaryResponse(**result)
        
    except Exception as e:
        logger.error(f"Error generating drug summary: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "SUMMARY_ERROR",
                "message": "Failed to generate drug summary. Please try again."
            }
        )


@router.get("/health")
async def discovery_health():
    """Discovery API health check"""
    return {
        "status": "healthy",
        "service": "discovery",
        "endpoints": ["/analyze", "/drug-summary"]
    }
