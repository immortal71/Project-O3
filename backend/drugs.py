"""
Drug-related API endpoints
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.api.dependencies import (
    get_any_authenticated_user,
    get_basic_tier_user,
    get_db,
    get_pagination_params,
)
from app.core.logging import get_struct_logger
from app.models.drug import Drug, DosingRecommendation, Patent, SafetyProfile
from app.models.prediction import DrugCancerPrediction
from app.schemas.common import PaginatedResponse
from app.schemas.drug import (
    DrugDetailResponse,
    DrugListResponse,
    DrugResponse,
    DrugSearchRequest,
)

logger = get_struct_logger(__name__)
router = APIRouter(prefix="/drugs", tags=["Drugs"])


@router.get("/", response_model=DrugListResponse)
async def list_drugs(
    search_request: DrugSearchRequest = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_any_authenticated_user),
) -> DrugListResponse:
    """List drugs with search and pagination"""
    
    # Build query
    query = select(Drug)
    
    # Apply filters
    if search_request.query:
        query = query.where(
            Drug.drug_name.ilike(f"%{search_request.query}%")
            | Drug.primary_indication.ilike(f"%{search_request.query}%")
        )
    
    if search_request.drug_name:
        query = query.where(Drug.drug_name.ilike(f"%{search_request.drug_name}%"))
    
    if search_request.drugbank_id:
        query = query.where(Drug.drugbank_id == search_request.drugbank_id)
    
    if search_request.indication:
        query = query.where(
            Drug.primary_indication.ilike(f"%{search_request.indication}%")
        )
    
    if search_request.drug_class:
        query = query.where(Drug.drug_class.ilike(f"%{search_request.drug_class}%"))
    
    if search_request.approval_status:
        query = query.where(Drug.approval_status == search_request.approval_status)
    
    # Apply sorting
    sort_column = getattr(Drug, search_request.sort_by, Drug.drug_name)
    if search_request.sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
    
    # Get total count
    count_query = select(query).with_only_columns(query.c.id)
    total_result = await db.execute(count_query)
    total = len(total_result.scalars().all())
    
    # Apply pagination
    offset = (search_request.page - 1) * search_request.size
    query = query.offset(offset).limit(search_request.size)
    
    # Execute query
    result = await db.execute(query)
    drugs = result.scalars().all()
    
    # Calculate pagination metadata
    pages = (total + search_request.size - 1) // search_request.size
    
    logger.info(
        "Drug search executed",
        extra={
            "query": search_request.query,
            "page": search_request.page,
            "size": search_request.size,
            "total": total,
            "user_id": str(current_user.id),
        },
    )
    
    return DrugListResponse(
        items=[DrugResponse.from_orm(drug) for drug in drugs],
        total=total,
        page=search_request.page,
        size=search_request.size,
        pages=pages,
    )


@router.get("/{drug_id}", response_model=DrugDetailResponse)
async def get_drug_detail(
    drug_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_any_authenticated_user),
) -> DrugDetailResponse:
    """Get detailed drug information including related data"""
    
    # Get drug with all related data
    query = (
        select(Drug)
        .where(Drug.id == drug_id)
        .options(
            selectinload(Drug.predictions),
            selectinload(Drug.safety_profiles),
            selectinload(Drug.dosing_recommendations),
            selectinload(Drug.patents),
            selectinload(Drug.clinical_trials),
        )
    )
    
    result = await db.execute(query)
    drug = result.scalar_one_or_none()
    
    if not drug:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Drug not found",
        )
    
    logger.info(
        "Drug details retrieved",
        extra={"drug_id": drug_id, "user_id": str(current_user.id)},
    )
    
    return DrugDetailResponse.from_orm(drug)


@router.get("/{drug_id}/predictions")
async def get_drug_predictions(
    drug_id: str,
    cancer_id: Optional[str] = Query(None, description="Filter by cancer type"),
    confidence_threshold: Optional[float] = Query(
        None, ge=0, le=100, description="Minimum confidence score"
    ),
    limit: int = Query(20, ge=1, le=100, description="Number of results to return"),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_basic_tier_user),
) -> List[dict]:
    """Get drug-cancer predictions for a specific drug"""
    
    # Build query
    query = (
        select(DrugCancerPrediction)
        .where(DrugCancerPrediction.drug_id == drug_id)
        .order_by(DrugCancerPrediction.confidence_score.desc())
    )
    
    # Apply filters
    if cancer_id:
        query = query.where(DrugCancerPrediction.cancer_id == cancer_id)
    
    if confidence_threshold is not None:
        query = query.where(
            DrugCancerPrediction.confidence_score >= confidence_threshold
        )
    
    # Apply limit
    query = query.limit(limit)
    
    # Execute query
    result = await db.execute(query)
    predictions = result.scalars().all()
    
    logger.info(
        "Drug predictions retrieved",
        extra={
            "drug_id": drug_id,
            "cancer_id": cancer_id,
            "confidence_threshold": confidence_threshold,
            "count": len(predictions),
            "user_id": str(current_user.id),
        },
    )
    
    return [
        {
            "id": pred.id,
            "cancer_id": pred.cancer_id,
            "confidence_score": float(pred.confidence_score),
            "evidence_strength": pred.evidence_strength,
            "mechanism_hypothesis": pred.mechanism_hypothesis,
            "predicted_efficacy": pred.predicted_efficacy,
            "safety_concerns": pred.safety_concerns,
            "created_at": pred.created_at,
        }
        for pred in predictions
    ]


@router.get("/{drug_id}/safety")
async def get_drug_safety_profile(
    drug_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_any_authenticated_user),
) -> List[dict]:
    """Get drug safety profile"""
    
    query = select(SafetyProfile).where(SafetyProfile.drug_id == drug_id)
    result = await db.execute(query)
    safety_profiles = result.scalars().all()
    
    logger.info(
        "Drug safety profile retrieved",
        extra={"drug_id": drug_id, "user_id": str(current_user.id)},
    )
    
    return [
        {
            "id": profile.id,
            "adverse_events": profile.adverse_events,
            "contraindications": profile.contraindications,
            "drug_interactions": profile.drug_interactions,
            "black_box_warnings": profile.black_box_warnings,
            "monitoring_requirements": profile.monitoring_requirements,
            "pregnancy_category": profile.pregnancy_category,
            "hepatic_impairment_guidance": profile.hepatic_impairment_guidance,
            "renal_impairment_guidance": profile.renal_impairment_guidance,
        }
        for profile in safety_profiles
    ]


@router.get("/{drug_id}/patents")
async def get_drug_patents(
    drug_id: str,
    status_filter: Optional[str] = Query(
        None, description="Filter by patent status (active, expired, pending)"
    ),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_any_authenticated_user),
) -> List[dict]:
    """Get drug patent information"""
    
    query = select(Patent).where(Patent.drug_id == drug_id)
    
    if status_filter:
        query = query.where(Patent.patent_status == status_filter)
    
    query = query.order_by(Patent.expiry_date.asc().nullslast())
    
    result = await db.execute(query)
    patents = result.scalars().all()
    
    logger.info(
        "Drug patents retrieved",
        extra={
            "drug_id": drug_id,
            "status_filter": status_filter,
            "count": len(patents),
            "user_id": str(current_user.id),
        },
    )
    
    return [
        {
            "id": patent.id,
            "patent_number": patent.patent_number,
            "patent_title": patent.patent_title,
            "filing_date": patent.filing_date,
            "grant_date": patent.grant_date,
            "expiry_date": patent.expiry_date,
            "patent_status": patent.patent_status,
            "assignee": patent.assignee,
            "claims": patent.claims,
            "patent_url": patent.patent_url,
        }
        for patent in patents
    ]


@router.get("/{drug_id}/trials")
async def get_drug_clinical_trials(
    drug_id: str,
    status: Optional[str] = Query(None, description="Filter by trial status"),
    phase: Optional[str] = Query(None, description="Filter by trial phase"),
    limit: int = Query(20, ge=1, le=100, description="Number of results to return"),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_any_authenticated_user),
) -> List[dict]:
    """Get clinical trials for a drug"""
    
    query = (
        select(Drug)
        .where(Drug.id == drug_id)
        .options(selectinload(Drug.clinical_trials))
    )
    
    result = await db.execute(query)
    drug = result.scalar_one_or_none()
    
    if not drug:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Drug not found",
        )
    
    # Filter trials
    trials = drug.clinical_trials
    
    if status:
        trials = [t for t in trials if t.status == status]
    
    if phase:
        trials = [t for t in trials if t.phase == phase]
    
    # Sort by start date (newest first)
    trials = sorted(trials, key=lambda t: t.start_date or datetime.min, reverse=True)
    
    # Apply limit
    trials = trials[:limit]
    
    logger.info(
        "Drug clinical trials retrieved",
        extra={
            "drug_id": drug_id,
            "status": status,
            "phase": phase,
            "count": len(trials),
            "user_id": str(current_user.id),
        },
    )
    
    return [
        {
            "id": trial.id,
            "nct_id": trial.nct_id,
            "title": trial.title,
            "status": trial.status,
            "phase": trial.phase,
            "sponsor": trial.sponsor,
            "start_date": trial.start_date,
            "completion_date": trial.completion_date,
            "enrollment_count": trial.enrollment_count,
            "primary_outcome": trial.primary_outcome,
            "results_summary": trial.results_summary,
            "trial_url": trial.trial_url,
        }
        for trial in trials
    ]