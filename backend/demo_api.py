"""
Demo API Endpoints - Fast, Pre-computed Results
Perfect for live demos at Founders Fest!

These endpoints return instant results from our curated demo dataset.
NO database queries, NO ML inference - just blazing fast responses.
"""

from typing import Dict, List, Optional
import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from demo_dataset import DEMO_REPURPOSING_CASES
from confidence_scorer import ConfidenceScorer

router = APIRouter(prefix="/api/v1/demo", tags=["demo"])

# Initialize scorer
scorer = ConfidenceScorer()


# Response Models
class RepurposingMatch(BaseModel):
    """Single drug repurposing match"""
    id: str
    drug_name: str
    original_indication: str
    cancer_type: str
    confidence_score: float
    confidence_tier: str
    status: str
    evidence: Dict
    market_potential: Dict


class SearchResponse(BaseModel):
    """Search results response"""
    query: str
    total_results: int
    matches: List[RepurposingMatch]
    execution_time_ms: float
    data_sources: List[str]


class DrugAnalysisResponse(BaseModel):
    """Detailed drug analysis"""
    drug_name: str
    cancer_matches: List[RepurposingMatch]
    total_matches: int
    avg_confidence: float
    strongest_match: Optional[RepurposingMatch]


class CancerAnalysisResponse(BaseModel):
    """Detailed cancer type analysis"""
    cancer_type: str
    drug_matches: List[RepurposingMatch]
    total_matches: int
    avg_confidence: float
    top_drugs: List[str]


# Helper Functions
def search_by_drug(drug_name: str) -> List[Dict]:
    """Search demo dataset by drug name"""
    drug_lower = drug_name.lower()
    return [
        case for case in DEMO_REPURPOSING_CASES
        if drug_lower in case['drug_name'].lower()
    ]


def search_by_cancer(cancer_type: str) -> List[Dict]:
    """Search demo dataset by cancer type"""
    cancer_lower = cancer_type.lower()
    return [
        case for case in DEMO_REPURPOSING_CASES
        if cancer_lower in case['cancer_type'].lower()
    ]


def search_by_keyword(keyword: str) -> List[Dict]:
    """Search demo dataset by any keyword"""
    keyword_lower = keyword.lower()
    results = []
    
    for case in DEMO_REPURPOSING_CASES:
        # Search in multiple fields
        searchable = f"{case['drug_name']} {case['cancer_type']} {case['original_indication']} {case['status']}".lower()
        
        if keyword_lower in searchable:
            results.append(case)
    
    return results


def format_match(case: Dict) -> RepurposingMatch:
    """Format demo case as API response"""
    return RepurposingMatch(
        id=case['id'],
        drug_name=case['drug_name'],
        original_indication=case['original_indication'],
        cancer_type=case['cancer_type'],
        confidence_score=case['confidence_score'],
        confidence_tier=scorer.get_confidence_tier(case['confidence_score']),
        status=case['status'],
        evidence=case['evidence'],
        market_potential=case['market_potential']
    )


# API Endpoints
@router.get("/search", response_model=SearchResponse)
async def search_repurposing(
    q: str = Query(..., description="Search query (drug name, cancer type, or keyword)"),
    min_confidence: float = Query(0.0, ge=0.0, le=1.0, description="Minimum confidence score"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results to return")
):
    """
    🚀 DEMO SEARCH - Instant results for live presentation
    
    Search our curated repurposing dataset by:
    - Drug name (e.g., "metformin", "aspirin")
    - Cancer type (e.g., "breast", "lung", "colorectal")
    - Keywords (e.g., "diabetes", "pain")
    
    Returns pre-computed, high-quality matches instantly!
    """
    
    import time
    start_time = time.time()
    
    # Try different search strategies
    results = search_by_drug(q)
    
    if not results:
        results = search_by_cancer(q)
    
    if not results:
        results = search_by_keyword(q)
    
    # Filter by confidence
    results = [r for r in results if r['confidence_score'] >= min_confidence]
    
    # Sort by confidence (descending) and demo priority
    results.sort(key=lambda x: (x['confidence_score'], -x['demo_priority']), reverse=True)
    
    # Limit results
    results = results[:limit]
    
    # Format matches
    matches = [format_match(case) for case in results]
    
    # Collect unique data sources
    all_sources = set()
    for case in results:
        all_sources.update(case['evidence']['sources'])
    
    execution_time = (time.time() - start_time) * 1000  # Convert to ms
    
    return SearchResponse(
        query=q,
        total_results=len(matches),
        matches=matches,
        execution_time_ms=round(execution_time, 2),
        data_sources=sorted(all_sources)
    )


@router.get("/analyze/drug/{drug_name}", response_model=DrugAnalysisResponse)
async def analyze_drug(drug_name: str):
    """
    📊 DRUG ANALYSIS - All cancer matches for a specific drug
    
    Perfect for showing investors "what cancers can this drug treat?"
    
    Examples:
    - /analyze/drug/metformin
    - /analyze/drug/aspirin
    - /analyze/drug/atorvastatin
    """
    
    matches = search_by_drug(drug_name)
    
    if not matches:
        raise HTTPException(
            status_code=404,
            detail=f"No repurposing data found for drug: {drug_name}"
        )
    
    # Sort by confidence
    matches.sort(key=lambda x: x['confidence_score'], reverse=True)
    
    formatted_matches = [format_match(case) for case in matches]
    
    # Calculate stats
    avg_confidence = sum(m.confidence_score for m in formatted_matches) / len(formatted_matches)
    
    return DrugAnalysisResponse(
        drug_name=drug_name,
        cancer_matches=formatted_matches,
        total_matches=len(formatted_matches),
        avg_confidence=round(avg_confidence, 2),
        strongest_match=formatted_matches[0] if formatted_matches else None
    )


@router.get("/analyze/cancer/{cancer_type}", response_model=CancerAnalysisResponse)
async def analyze_cancer(cancer_type: str):
    """
    🎯 CANCER ANALYSIS - All drug candidates for a cancer type
    
    Perfect for showing "what repurposed drugs can treat breast cancer?"
    
    Examples:
    - /analyze/cancer/breast
    - /analyze/cancer/colorectal
    - /analyze/cancer/lung
    """
    
    matches = search_by_cancer(cancer_type)
    
    if not matches:
        raise HTTPException(
            status_code=404,
            detail=f"No repurposing data found for cancer type: {cancer_type}"
        )
    
    # Sort by confidence
    matches.sort(key=lambda x: x['confidence_score'], reverse=True)
    
    formatted_matches = [format_match(case) for case in matches]
    
    # Calculate stats
    avg_confidence = sum(m.confidence_score for m in formatted_matches) / len(formatted_matches)
    top_drugs = [m.drug_name for m in formatted_matches[:5]]
    
    return CancerAnalysisResponse(
        cancer_type=cancer_type,
        drug_matches=formatted_matches,
        total_matches=len(formatted_matches),
        avg_confidence=round(avg_confidence, 2),
        top_drugs=top_drugs
    )


@router.get("/priority-cases", response_model=List[RepurposingMatch])
async def get_priority_cases(priority: int = Query(1, ge=1, le=3, description="Demo priority level")):
    """
    ⭐ PRIORITY CASES - Your best demo examples
    
    Priority 1: Best for live demo (metformin, aspirin, thalidomide)
    Priority 2: Good backup examples
    Priority 3: Additional examples
    """
    
    cases = [case for case in DEMO_REPURPOSING_CASES if case['demo_priority'] == priority]
    cases.sort(key=lambda x: x['confidence_score'], reverse=True)
    
    return [format_match(case) for case in cases]


@router.get("/stats", response_model=Dict)
async def get_demo_stats():
    """
    📈 DEMO STATISTICS - For your pitch deck
    
    Returns impressive numbers for slides:
    - Total cases in dataset
    - Average confidence
    - Coverage by cancer type
    - Data source diversity
    """
    
    # Cancer type distribution
    cancer_types = {}
    for case in DEMO_REPURPOSING_CASES:
        cancer = case['cancer_type']
        cancer_types[cancer] = cancer_types.get(cancer, 0) + 1
    
    # Drug distribution
    drugs = {}
    for case in DEMO_REPURPOSING_CASES:
        drug = case['drug_name']
        drugs[drug] = drugs.get(drug, 0) + 1
    
    # Clinical phase distribution
    phases = {}
    for case in DEMO_REPURPOSING_CASES:
        status = case['status']
        phases[status] = phases.get(status, 0) + 1
    
    # Average confidence
    avg_confidence = sum(c['confidence_score'] for c in DEMO_REPURPOSING_CASES) / len(DEMO_REPURPOSING_CASES)
    
    # Total trials
    total_trials = sum(c['evidence']['clinical_trials'] for c in DEMO_REPURPOSING_CASES)
    
    # Total citations
    total_citations = sum(c['evidence']['pubmed_citations'] for c in DEMO_REPURPOSING_CASES)
    
    # All data sources
    all_sources = set()
    for case in DEMO_REPURPOSING_CASES:
        all_sources.update(case['evidence']['sources'])
    
    return {
        'total_cases': len(DEMO_REPURPOSING_CASES),
        'unique_drugs': len(drugs),
        'unique_cancer_types': len(cancer_types),
        'avg_confidence_score': round(avg_confidence, 2),
        'total_clinical_trials': total_trials,
        'total_pubmed_citations': total_citations,
        'data_sources': sorted(all_sources),
        'cancer_type_distribution': cancer_types,
        'clinical_phase_distribution': phases,
        'high_confidence_cases': len([c for c in DEMO_REPURPOSING_CASES if c['confidence_score'] >= 0.75])
    }


@router.get("/confidence/explain")
async def explain_confidence_scoring():
    """
    📚 EXPLAIN SCORING - For investor questions
    
    Transparent explanation of how we calculate confidence scores.
    Shows you're data-driven and methodical.
    """
    
    return {
        'method': 'Rule-based scoring using multiple evidence factors',
        'factors': {
            'clinical_phase': {
                'weight': '40%',
                'description': 'FDA approval status and clinical trial phase',
                'scale': {
                    'Approved': 1.0,
                    'Phase 3': 0.85,
                    'Phase 2': 0.65,
                    'Phase 1': 0.45,
                    'Preclinical': 0.25
                }
            },
            'trial_count': {
                'weight': '20%',
                'description': 'Number of clinical trials investigating this repurposing',
                'scale': '100+ trials = 1.0, scaled logarithmically'
            },
            'citations': {
                'weight': '15%',
                'description': 'PubMed publication citations',
                'scale': '300+ citations = 1.0, scaled logarithmically'
            },
            'data_sources': {
                'weight': '15%',
                'description': 'Quality and diversity of evidence sources',
                'sources': {
                    'FDA': 1.0,
                    'repoDB': 0.95,
                    'ClinicalTrials.gov': 0.90,
                    'ReDO_DB': 0.85,
                    'Broad Hub': 0.80
                }
            },
            'mechanism': {
                'weight': '10%',
                'description': 'Clarity of mechanism of action (number of pathways)',
                'scale': '4+ pathways = 1.0'
            }
        },
        'tiers': {
            'Very High': '≥ 0.85',
            'High': '0.70 - 0.84',
            'Moderate': '0.55 - 0.69',
            'Low': '0.40 - 0.54',
            'Very Low': '< 0.40'
        },
        'transparency': 'All scores are explainable and based on publicly verifiable data'
    }
