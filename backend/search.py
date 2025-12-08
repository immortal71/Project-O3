"""
Search and analysis API endpoints
"""

# Copyright (c) 2025 OncoPurpose (trovesx)
# All Rights Reserved.
# For licensing info, see LICENSE or contact oncopurpose@trovesx.com

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.dependencies import (
    get_any_authenticated_user,
    get_basic_tier_user,
    get_db,
    get_professional_tier_user,
)
from app.core.config import settings
from app.core.logging import get_struct_logger
from app.models.cancer import Cancer
from app.models.drug import Drug
from app.models.prediction import DrugCancerPrediction
from app.models.user import User, UserSearch
from app.schemas.search import (
    AnalysisRequest,
    AnalysisResponse,
    SearchHistoryResponse,
    SearchRequest,
)

logger = get_struct_logger(__name__)
router = APIRouter(prefix="/search", tags=["Search & Analysis"])


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_drug_cancer_matches(
    request: AnalysisRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_professional_tier_user),
) -> AnalysisResponse:
    """Analyze drug-cancer matching opportunities"""
    
    # Validate input
    if not request.cancer_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cancer type is required",
        )
    
    # Get cancer ID
    cancer_result = await db.execute(
        select(Cancer).where(Cancer.cancer_type.ilike(f"%{request.cancer_type}%"))
    )
    cancer = cancer_result.scalar_one_or_none()
    
    if not cancer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cancer type not found",
        )
    
    # Build query for predictions
    query = select(DrugCancerPrediction).where(
        DrugCancerPrediction.cancer_id == cancer.id
    )
    
    # Apply confidence threshold
    if request.filters and request.filters.confidence_threshold:
        query = query.where(
            DrugCancerPrediction.confidence_score
            >= request.filters.confidence_threshold
        )
    
    # Apply patent status filter
    if request.filters and request.filters.patent_status:
        # This would require joining with patents table
        # For now, we'll skip this filter
        pass
    
    # Apply clinical phase filter
    if request.filters and request.filters.clinical_phase:
        # This would require joining with clinical trials table
        # For now, we'll skip this filter
        pass
    
    # Apply market size filter
    if request.filters and request.filters.market_size_min:
        # This would require joining with market analysis table
        # For now, we'll skip this filter
        pass
    
    # Order by confidence score
    query = query.order_by(DrugCancerPrediction.confidence_score.desc())
    
    # Execute query
    result = await db.execute(query)
    predictions = result.scalars().all()
    
    # Get drug information for each prediction
    drug_ids = [pred.drug_id for pred in predictions]
    drug_result = await db.execute(
        select(Drug).where(Drug.id.in_(drug_ids))
    )
    drugs = {drug.id: drug for drug in drug_result.scalars().all()}
    
    # Build response
    matches = []
    for prediction in predictions:
        drug = drugs.get(prediction.drug_id)
        if drug:
            matches.append(
                {
                    "drug_id": prediction.drug_id,
                    "drug_name": drug.drug_name,
                    "drugbank_id": drug.drugbank_id,
                    "primary_indication": drug.primary_indication,
                    "confidence_score": float(prediction.confidence_score),
                    "evidence_strength": prediction.evidence_strength,
                    "mechanism_hypothesis": prediction.mechanism_hypothesis,
                    "created_at": prediction.created_at,
                }
            )
    
    # Save search to history
    search_record = UserSearch(
        user_id=current_user.id,
        search_query={
            "cancer_type": request.cancer_type,
            "drug_name": request.drug_name,
            "molecular_target": request.molecular_target,
            "model": request.model,
            "filters": request.filters.dict() if request.filters else None,
        },
        results_count=len(matches),
    )
    db.add(search_record)
    await db.commit()
    
    logger.info(
        "Drug-cancer analysis completed",
        extra={
            "cancer_type": request.cancer_type,
            "drug_name": request.drug_name,
            "model": request.model,
            "results_count": len(matches),
            "user_id": str(current_user.id),
        },
    )
    
    return AnalysisResponse(
        cancer_type=request.cancer_type,
        model=request.model,
        results_count=len(matches),
        matches=matches,
        analysis_timestamp=datetime.utcnow(),
    )


@router.get("/history", response_model=List[SearchHistoryResponse])
async def get_search_history(
    limit: int = Query(20, ge=1, le=100, description="Number of results to return"),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_any_authenticated_user),
) -> List[SearchHistoryResponse]:
    """Get user's search history"""
    
    query = (
        select(UserSearch)
        .where(UserSearch.user_id == current_user.id)
        .order_by(UserSearch.searched_at.desc())
        .limit(limit)
    )
    
    result = await db.execute(query)
    searches = result.scalars().all()
    
    logger.info(
        "Search history retrieved",
        extra={
            "user_id": str(current_user.id),
            "count": len(searches),
        },
    )
    
    return [
        SearchHistoryResponse(
            id=search.id,
            search_query=search.search_query,
            results_count=search.results_count,
            searched_at=search.searched_at,
        )
        for search in searches
    ]


@router.delete("/history/{search_id}")
async def delete_search_history_item(
    search_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_any_authenticated_user),
) -> dict:
    """Delete a search history item"""
    
    query = select(UserSearch).where(
        UserSearch.id == search_id,
        UserSearch.user_id == current_user.id,
    )
    
    result = await db.execute(query)
    search = result.scalar_one_or_none()
    
    if not search:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Search history item not found",
        )
    
    await db.delete(search)
    await db.commit()
    
    logger.info(
        "Search history item deleted",
        extra={
            "search_id": search_id,
            "user_id": str(current_user.id),
        },
    )
    
    return {"message": "Search history item deleted successfully"}


@router.get("/suggestions")
async def get_search_suggestions(
    query: str = Query(..., min_length=2, description="Search query"),
    type: str = Query("all", description="Suggestion type: drugs, cancers, or all"),
    limit: int = Query(10, ge=1, le=20, description="Number of suggestions"),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_any_authenticated_user),
) -> List[str]:
    """Get search suggestions based on query"""
    
    suggestions = []
    
    if type in ["drugs", "all"]:
        # Get drug name suggestions
        drug_query = (
            select(Drug.drug_name)
            .where(Drug.drug_name.ilike(f"%{query}%"))
            .limit(limit // 2 if type == "all" else limit)
        )
        
        drug_result = await db.execute(drug_query)
        drug_suggestions = drug_result.scalars().all()
        suggestions.extend(drug_suggestions)
    
    if type in ["cancers", "all"]:
        # Get cancer type suggestions
        cancer_query = (
            select(Cancer.cancer_type)
            .where(Cancer.cancer_type.ilike(f"%{query}%"))
            .limit(limit // 2 if type == "all" else limit)
        )
        
        cancer_result = await db.execute(cancer_query)
        cancer_suggestions = cancer_result.scalars().all()
        suggestions.extend(cancer_suggestions)
    
    # Remove duplicates and limit results
    suggestions = list(set(suggestions))[:limit]
    
    logger.info(
        "Search suggestions retrieved",
        extra={
            "query": query,
            "type": type,
            "count": len(suggestions),
            "user_id": str(current_user.id),
        },
    )
    
    return suggestions