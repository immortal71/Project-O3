"""
Research Library API - Simple sync version for frontend
Serves research papers without complex dependencies
"""

from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
import json
from pathlib import Path

router = APIRouter(prefix="/api/v1/library", tags=["library"])

# Global cache
_papers_cache = None


def load_papers():
    """Load research papers from JSON file"""
    global _papers_cache
    
    if _papers_cache is not None:
        return _papers_cache
    
    try:
        papers_file = Path(__file__).parent.parent / 'data' / 'research_papers' / 'pubmed_papers.json'
        
        if not papers_file.exists():
            _papers_cache = {'papers': []}
            return _papers_cache
        
        with open(papers_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            _papers_cache = data
            print(f"✅ Loaded {len(data.get('papers', []))} research papers")
            return data
    
    except Exception as e:
        print(f"❌ Error loading research papers: {e}")
        _papers_cache = {'papers': []}
        return _papers_cache


@router.get("/papers")
async def get_papers(
    query: Optional[str] = None,
    cancer_type: Optional[str] = None,
    study_type: Optional[str] = None,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """Get research papers with filtering"""
    data = load_papers()
    papers = data.get('papers', [])
    
    filtered = papers
    
    if query:
        query_lower = query.lower()
        filtered = [
            p for p in filtered 
            if query_lower in p.get('title', '').lower() 
            or query_lower in p.get('abstract', '').lower()
        ]
    
    if cancer_type:
        filtered = [p for p in filtered if cancer_type in p.get('cancer_types', [])]
    
    if study_type:
        filtered = [p for p in filtered if p.get('study_type') == study_type]
    
    if year_from:
        filtered = [p for p in filtered if p.get('year', 0) >= year_from]
    
    if year_to:
        filtered = [p for p in filtered if p.get('year', 9999) <= year_to]
    
    total = len(filtered)
    paginated = filtered[offset:offset + limit]
    
    return {
        'total': total,
        'offset': offset,
        'limit': limit,
        'papers': paginated
    }


@router.get("/papers/{pmid}")
async def get_paper_details(pmid: str):
    """Get detailed information for a specific paper"""
    data = load_papers()
    papers = data.get('papers', [])
    
    paper = next((p for p in papers if p.get('pmid') == pmid), None)
    
    if not paper:
        raise HTTPException(status_code=404, detail=f"Paper {pmid} not found")
    
    return paper


@router.get("/stats")
async def get_library_stats():
    """Get statistics about the research library"""
    data = load_papers()
    papers = data.get('papers', [])
    
    if not papers:
        return {
            'total_papers': 0,
            'cancer_types': {},
            'study_types': {},
            'year_distribution': {}
        }
    
    cancer_type_counts = {}
    study_type_counts = {}
    year_counts = {}
    
    for paper in papers:
        for cancer in paper.get('cancer_types', []):
            cancer_type_counts[cancer] = cancer_type_counts.get(cancer, 0) + 1
        
        study_type = paper.get('study_type', 'Unknown')
        study_type_counts[study_type] = study_type_counts.get(study_type, 0) + 1
        
        year = paper.get('year', 2024)
        year_counts[year] = year_counts.get(year, 0) + 1
    
    return {
        'total_papers': len(papers),
        'cancer_types': cancer_type_counts,
        'study_types': study_type_counts,
        'year_distribution': year_counts
    }


@router.get("/drug/{drug_name}")
async def search_by_drug(
    drug_name: str,
    limit: int = Query(20, ge=1, le=100)
):
    """Search papers mentioning a specific drug"""
    data = load_papers()
    papers = data.get('papers', [])
    
    drug_lower = drug_name.lower()
    
    matching = [
        p for p in papers
        if drug_lower in p.get('title', '').lower()
        or drug_lower in p.get('abstract', '').lower()
    ]
    
    return {
        'drug': drug_name,
        'total': len(matching),
        'papers': matching[:limit]
    }


@router.get("/download-pdf/{pmid}")
async def download_paper_pdf(pmid: str):
    """Generate and download PDF for a paper"""
    from fastapi.responses import StreamingResponse
    from pdf_generator import generate_paper_pdf
    
    # Find paper by PMID
    data = load_papers()
    papers = data.get('papers', [])
    
    paper = next((p for p in papers if str(p.get('pmid')) == pmid), None)
    
    if not paper:
        raise HTTPException(status_code=404, detail=f"Paper with PMID {pmid} not found")
    
    # Generate PDF
    pdf_buffer = generate_paper_pdf(paper)
    
    # Clean filename
    safe_title = paper.get('title', 'paper')[:50].replace('/', '-').replace('\\', '-')
    filename = f"{pmid}_{safe_title}.pdf"
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
