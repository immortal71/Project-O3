"""
Integrated Demo API - Uses REAL DATA from Broad Hub + Hero Cases

Endpoints powered by:
- 6,798 drugs from Broad Institute Drug Repurposing Hub
- 15 gold-standard hero cases (Metformin, Aspirin, etc.)
- 235 oncology-focused compounds
- Real mechanisms, targets, and clinical phases
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from data_loader import get_data_loader
from confidence_scorer import ConfidenceScorer
import time

router = APIRouter(prefix="/api/v1", tags=["repurposing"])

# Initialize components
scorer = ConfidenceScorer()


# Response Models
class DrugMatch(BaseModel):
    """Drug match from search"""
    source: str  # "hero_case" or "broad_hub"
    drug_name: str
    clinical_phase: Optional[str]
    mechanism: Optional[str]
    confidence_score: Optional[float] = None
    cancer_types: Optional[List[str]] = None
    targets: Optional[List[str]] = None
    disease_area: Optional[str] = None


class SearchResponse(BaseModel):
    """Search results"""
    query: str
    total_results: int
    hero_cases_found: int
    broad_hub_matches: int
    execution_time_ms: float
    results: List[DrugMatch]


# ============================================================================
# SEARCH ENDPOINT - Main search across all data
# ============================================================================

@router.get("/search", response_model=SearchResponse)
async def search_repurposing(
    q: str = Query(..., min_length=2, description="Search query: drug name, cancer type, mechanism, or target"),
    limit: int = Query(50, ge=1, le=200, description="Maximum results"),
    oncology_only: bool = Query(False, description="Only return oncology-related compounds")
):
    """
    🔍 Search 6,800+ compounds for repurposing opportunities
    
    Query examples:
    - Drug names: "metformin", "aspirin", "itraconazole"
    - Cancer types: "breast", "lung", "colorectal"
    - Mechanisms: "mtor", "cox inhibitor", "hdac"
    - Targets: "EGFR", "VEGF", "CDK"
    
    Returns hero cases (high confidence) + Broad Hub matches
    """
    
    start_time = time.time()
    loader = get_data_loader()
    
    # Search hero cases (always high priority)
    hero_matches = []
    query_lower = q.lower()
    
    for case in loader.get_hero_cases():
        if (query_lower in case["drug_name"].lower() or
            any(query_lower in str(cancer).lower() for cancer in case.get("repurposed_cancer", [])) or
            query_lower in case.get("mechanism", "").lower() or
            any(query_lower in p.lower() for p in case.get("pathways", []))):
            
            hero_matches.append(DrugMatch(
                source="hero_case",
                drug_name=case["drug_name"],
                clinical_phase=case["phase"],
                mechanism=case["mechanism"],
                confidence_score=case["confidence_score"],
                cancer_types=case["repurposed_cancer"] if isinstance(case["repurposed_cancer"], list) else [case["repurposed_cancer"]]
            ))
    
    # Search Broad Hub
    broad_matches = []
    
    if oncology_only:
        # Search oncology subset
        search_pool = loader.get_oncology_drugs(limit=500)
        search_results = [d for d in search_pool if query_lower in str(d).lower()]
    else:
        # Search all drugs
        search_results = loader.search_drugs(q, limit=limit * 2)
    
    for drug in search_results[:limit]:
        targets = drug.get("target", "").split("|") if drug.get("target") else []
        
        broad_matches.append(DrugMatch(
            source="broad_hub",
            drug_name=drug.get("pert_iname", "Unknown"),
            clinical_phase=drug.get("clinical_phase"),
            mechanism=drug.get("moa"),
            targets=targets[:5],  # Limit to 5 targets
            disease_area=drug.get("disease_area")
        ))
    
    # Combine (hero cases first)
    all_matches = hero_matches + broad_matches
    
    execution_time = (time.time() - start_time) * 1000
    
    return SearchResponse(
        query=q,
        total_results=len(all_matches),
        hero_cases_found=len(hero_matches),
        broad_hub_matches=len(broad_matches),
        execution_time_ms=round(execution_time, 2),
        results=all_matches[:limit]
    )


# ============================================================================
# DRUG ANALYSIS - Detailed info for specific drug
# ============================================================================

@router.get("/drug/{drug_name}")
async def get_drug_details(drug_name: str):
    """
    📊 Get complete details for a specific drug
    
    Returns:
    - Hero case data (if available) with high confidence scores
    - Broad Hub data with mechanism, targets, phase
    - All available cancer associations
    """
    
    loader = get_data_loader()
    
    # Check hero cases
    hero_case = loader.get_hero_case(drug_name)
    
    # Check Broad Hub
    broad_drug = loader.get_drug_by_name(drug_name)
    
    # If not found, try searching
    if not hero_case and not broad_drug:
        search_results = loader.search_drugs(drug_name, limit=5)
        if search_results:
            broad_drug = search_results[0]
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Drug '{drug_name}' not found in database. Try searching first."
            )
    
    response = {
        "drug_name": drug_name,
        "found_in_hero_cases": hero_case is not None,
        "found_in_broad_hub": broad_drug is not None
    }
    
    if hero_case:
        response["hero_data"] = {
            "confidence_score": hero_case["confidence_score"],
            "cancer_types": hero_case["repurposed_cancer"],
            "original_indication": hero_case["original_indication"],
            "mechanism": hero_case["mechanism"],
            "clinical_phase": hero_case["phase"],
            "trials": hero_case["trial_count"],
            "citations": hero_case["citations"],
            "pathways": hero_case["pathways"],
            "evidence_level": hero_case["evidence_level"],
            "why_high_confidence": hero_case.get("why_high_confidence", "")
        }
    
    if broad_drug:
        targets = broad_drug.get("target", "").split("|") if broad_drug.get("target") else []
        
        response["broad_data"] = {
            "name": broad_drug.get("pert_iname"),
            "clinical_phase": broad_drug.get("clinical_phase"),
            "mechanism": broad_drug.get("moa"),
            "targets": targets,
            "disease_area": broad_drug.get("disease_area"),
            "indication": broad_drug.get("indication")
        }
    
    return response


# ============================================================================
# STATISTICS - System-wide stats
# ============================================================================

@router.get("/stats")
async def get_system_stats():
    """
    📈 Get overall system statistics
    
    Perfect for pitch deck: "Our platform has 6,800+ compounds..."
    """
    
    loader = get_data_loader()
    stats = loader.get_stats()
    
    # Hero case stats
    hero_cases = loader.get_hero_cases()
    if hero_cases:
        avg_hero_confidence = sum(c["confidence_score"] for c in hero_cases) / len(hero_cases)
        total_trials = sum(c["trial_count"] for c in hero_cases)
        total_citations = sum(c["citations"] for c in hero_cases)
        high_conf_cases = len([c for c in hero_cases if c["confidence_score"] >= 0.85])
    else:
        avg_hero_confidence = 0
        total_trials = 0
        total_citations = 0
        high_conf_cases = 0
    
    # Phase distribution (sample)
    phase_dist = {}
    for drug in loader.broad_drugs[:1000]:
        phase = drug.get('clinical_phase', 'Unknown')
        phase_dist[phase] = phase_dist.get(phase, 0) + 1
    
    return {
        "total_compounds": stats['total_drugs'],
        "oncology_compounds": stats['oncology_compounds'],
        "hero_cases": {
            "total": stats['hero_cases'],
            "average_confidence": round(avg_hero_confidence, 2),
            "high_confidence_count": high_conf_cases,
            "total_trials": total_trials,
            "total_citations": total_citations
        },
        "mechanisms_of_action": stats['mechanisms'],
        "unique_targets": stats['targets'],
        "phase_distribution_sample": phase_dist,
        "data_sources": [
            "Broad Institute Drug Repurposing Hub (6,798 compounds)",
            "Hero Cases (15 gold-standard examples)",
            "Clinical Trials Data (700+ trials)",
            "Scientific Literature (4,000+ citations)"
        ]
    }


# ============================================================================
# HERO CASES - Get gold-standard examples
# ============================================================================

@router.get("/hero-cases")
async def get_hero_cases(
    min_confidence: float = Query(0.0, ge=0.0, le=1.0, description="Minimum confidence score")
):
    """
    🌟 Get gold-standard hero cases (Metformin, Aspirin, etc.)
    
    These are well-documented repurposing successes with high confidence
    Perfect for showing "known positives" in demo
    """
    
    loader = get_data_loader()
    cases = loader.get_hero_cases()
    
    # Filter by confidence
    filtered = [c for c in cases if c["confidence_score"] >= min_confidence]
    
    # Sort by confidence
    filtered.sort(key=lambda x: x["confidence_score"], reverse=True)
    
    return {
        "total_hero_cases": len(filtered),
        "average_confidence": round(sum(c["confidence_score"] for c in filtered) / len(filtered), 2) if filtered else 0,
        "cases": filtered
    }


# ============================================================================
# ONCOLOGY - Get cancer-specific compounds
# ============================================================================

@router.get("/oncology")
async def get_oncology_compounds(
    limit: int = Query(100, ge=1, le=500, description="Maximum results")
):
    """
    🎯 Get oncology-specific compounds from Broad Hub
    
    Returns 235 cancer-related compounds with mechanisms and targets
    """
    
    loader = get_data_loader()
    compounds = loader.get_oncology_drugs(limit=limit)
    
    formatted = []
    for drug in compounds:
        formatted.append({
            "drug_name": drug.get("pert_iname"),
            "clinical_phase": drug.get("clinical_phase"),
            "mechanism": drug.get("moa"),
            "targets": drug.get("target", "").split("|")[:5] if drug.get("target") else [],
            "disease_area": drug.get("disease_area"),
            "indication": drug.get("indication")
        })
    
    return {
        "total_oncology_compounds": len(formatted),
        "compounds": formatted
    }


# ============================================================================
# MECHANISM SEARCH - Find drugs by MOA
# ============================================================================

@router.get("/mechanism/{moa}")
async def get_drugs_by_mechanism(
    moa: str,
    limit: int = Query(50, ge=1, le=200)
):
    """
    🔬 Find all drugs with a specific mechanism of action
    
    Examples:
    - /mechanism/CDK inhibitor
    - /mechanism/EGFR inhibitor
    - /mechanism/mTOR inhibitor
    """
    
    loader = get_data_loader()
    drugs = loader.get_drugs_by_mechanism(moa)
    
    if not drugs:
        raise HTTPException(
            status_code=404,
            detail=f"No drugs found with mechanism: {moa}"
        )
    
    formatted = []
    for drug in drugs[:limit]:
        formatted.append({
            "drug_name": drug.get("pert_iname"),
            "clinical_phase": drug.get("clinical_phase"),
            "targets": drug.get("target", "").split("|")[:5] if drug.get("target") else [],
            "disease_area": drug.get("disease_area")
        })
    
    return {
        "mechanism": moa,
        "total_drugs": len(formatted),
        "drugs": formatted
    }
