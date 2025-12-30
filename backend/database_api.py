"""
Database-backed API endpoints for OncoPurpose
Uses MySQL database instead of in-memory data
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid

from db_connection import get_db
from models import Drug, HeroCase, GeneratedOutput, Mechanism, Target, DrugMechanism, DrugTarget

router = APIRouter(prefix="/api/v1", tags=["database"])


# Pydantic models for responses
class DrugResponse(BaseModel):
    id: int
    drug_name: str
    clinical_phase: Optional[str]
    mechanism_of_action: Optional[str]
    target: Optional[str]
    disease_area: Optional[str]
    indication: Optional[str]
    source: str
    
    class Config:
        from_attributes = True


class HeroCaseResponse(BaseModel):
    id: int
    drug_name: str
    original_indication: Optional[str]
    repurposed_cancer: str
    confidence_score: Optional[float]
    trial_count: int
    citations: int
    mechanism: Optional[str]
    pathways: Optional[str]
    evidence_level: Optional[str]
    
    class Config:
        from_attributes = True


class GeneratedOutputRequest(BaseModel):
    output_type: str
    drug_name: Optional[str] = None
    cancer_type: Optional[str] = None
    input_parameters: Optional[dict] = None
    output_data: Optional[dict] = None
    file_path: Optional[str] = None
    confidence_score: Optional[float] = None
    user_id: Optional[str] = None


class GeneratedOutputResponse(BaseModel):
    id: int
    output_type: str
    drug_name: Optional[str]
    cancer_type: Optional[str]
    confidence_score: Optional[float]
    file_path: Optional[str]
    status: str
    session_id: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Endpoints

@router.get("/db/search")
async def search_drugs_db(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Search drugs in database by name, mechanism, target, or indication
    """
    search_term = f"%{q}%"
    
    # Search across multiple fields
    drugs = db.query(Drug).filter(
        or_(
            Drug.drug_name.ilike(search_term),
            Drug.mechanism_of_action.ilike(search_term),
            Drug.target.ilike(search_term),
            Drug.indication.ilike(search_term),
            Drug.disease_area.ilike(search_term)
        )
    ).limit(limit).all()
    
    # Also search hero cases
    hero_cases = db.query(HeroCase).filter(
        or_(
            HeroCase.drug_name.ilike(search_term),
            HeroCase.repurposed_cancer.ilike(search_term),
            HeroCase.mechanism.ilike(search_term)
        )
    ).limit(10).all()
    
    return {
        "query": q,
        "total_results": len(drugs) + len(hero_cases),
        "drugs": [DrugResponse.from_orm(d) for d in drugs],
        "hero_cases": [HeroCaseResponse.from_orm(h) for h in hero_cases]
    }


@router.get("/db/drug/{drug_name}")
async def get_drug_details_db(
    drug_name: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific drug from database
    """
    # Search in drugs table
    drug = db.query(Drug).filter(Drug.drug_name.ilike(drug_name)).first()
    
    # Search in hero cases
    hero_case = db.query(HeroCase).filter(HeroCase.drug_name.ilike(drug_name)).first()
    
    if not drug and not hero_case:
        raise HTTPException(status_code=404, detail=f"Drug '{drug_name}' not found")
    
    result = {}
    
    if drug:
        result["drug_data"] = DrugResponse.from_orm(drug)
    
    if hero_case:
        result["hero_case"] = HeroCaseResponse.from_orm(hero_case)
    
    return result


@router.get("/db/stats")
async def get_stats_db(db: Session = Depends(get_db)):
    """
    Get database statistics
    """
    total_drugs = db.query(func.count(Drug.id)).scalar()
    total_hero_cases = db.query(func.count(HeroCase.id)).scalar()
    total_mechanisms = db.query(func.count(Mechanism.id)).scalar()
    total_targets = db.query(func.count(Target.id)).scalar()
    total_outputs = db.query(func.count(GeneratedOutput.id)).scalar()
    
    # Count by clinical phase
    phase_counts = db.query(
        Drug.clinical_phase, 
        func.count(Drug.id)
    ).group_by(Drug.clinical_phase).all()
    
    # Top mechanisms
    top_mechanisms = db.query(
        Mechanism.mechanism_name,
        Mechanism.drug_count
    ).order_by(Mechanism.drug_count.desc()).limit(10).all()
    
    return {
        "total_drugs": total_drugs,
        "total_hero_cases": total_hero_cases,
        "total_mechanisms": total_mechanisms,
        "total_targets": total_targets,
        "total_generated_outputs": total_outputs,
        "clinical_phases": {phase: count for phase, count in phase_counts if phase},
        "top_mechanisms": [
            {"mechanism": name, "drug_count": count} 
            for name, count in top_mechanisms
        ]
    }


@router.get("/db/hero-cases", response_model=List[HeroCaseResponse])
async def get_hero_cases_db(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get hero repurposing cases from database, sorted by confidence score
    """
    cases = db.query(HeroCase).order_by(
        HeroCase.confidence_score.desc()
    ).limit(limit).all()
    
    return cases


@router.get("/db/mechanism/{mechanism_name}")
async def get_drugs_by_mechanism_db(
    mechanism_name: str,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Find drugs by mechanism of action in database
    """
    # Find mechanism
    mechanism = db.query(Mechanism).filter(
        Mechanism.mechanism_name.ilike(f"%{mechanism_name}%")
    ).first()
    
    if not mechanism:
        raise HTTPException(status_code=404, detail=f"Mechanism '{mechanism_name}' not found")
    
    # Get drugs with this mechanism
    drug_ids = db.query(DrugMechanism.drug_id).filter(
        DrugMechanism.mechanism_id == mechanism.id
    ).all()
    
    drugs = db.query(Drug).filter(
        Drug.id.in_([d[0] for d in drug_ids])
    ).limit(limit).all()
    
    return {
        "mechanism": mechanism.mechanism_name,
        "drug_count": mechanism.drug_count,
        "drugs": [DrugResponse.from_orm(d) for d in drugs]
    }


@router.get("/db/oncology")
async def get_oncology_drugs_db(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """
    Get oncology-specific drugs from database
    """
    drugs = db.query(Drug).filter(
        or_(
            Drug.disease_area.ilike("%oncology%"),
            Drug.disease_area.ilike("%cancer%"),
            Drug.indication.ilike("%cancer%"),
            Drug.indication.ilike("%tumor%"),
            Drug.indication.ilike("%leukemia%"),
            Drug.indication.ilike("%lymphoma%")
        )
    ).limit(limit).all()
    
    return {
        "total": len(drugs),
        "drugs": [DrugResponse.from_orm(d) for d in drugs]
    }


@router.post("/db/output", response_model=GeneratedOutputResponse)
async def save_generated_output(
    output: GeneratedOutputRequest,
    db: Session = Depends(get_db)
):
    """
    Save generated output (prediction, analysis, image, etc.) to database
    """
    # Generate session ID if not provided
    session_id = str(uuid.uuid4())
    
    new_output = GeneratedOutput(
        output_type=output.output_type,
        drug_name=output.drug_name,
        cancer_type=output.cancer_type,
        input_parameters=output.input_parameters,
        output_data=output.output_data,
        file_path=output.file_path,
        confidence_score=output.confidence_score,
        status='completed',
        user_id=output.user_id,
        session_id=session_id
    )
    
    db.add(new_output)
    db.commit()
    db.refresh(new_output)
    
    return new_output


@router.get("/db/outputs", response_model=List[GeneratedOutputResponse])
async def get_generated_outputs(
    output_type: Optional[str] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """
    Get generated outputs from database with optional filters
    """
    query = db.query(GeneratedOutput)
    
    if output_type:
        query = query.filter(GeneratedOutput.output_type == output_type)
    
    if user_id:
        query = query.filter(GeneratedOutput.user_id == user_id)
    
    if session_id:
        query = query.filter(GeneratedOutput.session_id == session_id)
    
    outputs = query.order_by(
        GeneratedOutput.created_at.desc()
    ).limit(limit).all()
    
    return outputs


@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint with database verification
    """
    try:
        # Test database connection
        db.execute("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
