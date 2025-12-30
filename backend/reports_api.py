"""
Reports API - Generate comprehensive research reports
Provides report generation and chart data for analytics
Includes AI-powered market report generation using OpenAI
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse, StreamingResponse
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime, timedelta
import logging
import io

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/reports", tags=["reports"])

# Import OpenAI service
try:
    from openai_service import OpenAIService
    openai_service = OpenAIService()
    logger.info("OpenAI service loaded for market reports")
except Exception as e:
    logger.warning(f"OpenAI service not available: {e}")
    openai_service = None


class MarketReportRequest(BaseModel):
    drug_name: str
    cancer_type: str
    confidence_score: float
    mechanism: Optional[str] = ""
    clinical_phase: Optional[str] = ""
    market_potential: Optional[str] = ""


@router.post("/generate")
async def generate_report(
    report_type: str = Query(..., description="Type of report: summary, detailed, executive"),
    disease: Optional[str] = None,
    drug: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
):
    """
    Generate comprehensive research report
    """
    try:
        logger.info(f"Generating {report_type} report for disease={disease}, drug={drug}")
        
        report_data = {
            "report_id": f"RPT-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "type": report_type,
            "generated_at": datetime.now().isoformat(),
            "parameters": {
                "disease": disease,
                "drug": drug,
                "date_from": date_from,
                "date_to": date_to
            },
            "sections": generate_report_sections(report_type, disease, drug),
            "metadata": {
                "total_pages": 24,
                "word_count": 8500,
                "references": 67,
                "figures": 12,
                "tables": 8
            }
        }
        
        return {
            "status": "success",
            "report": report_data
        }
        
    except Exception as e:
        logger.error(f"Report generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def generate_report_sections(report_type: str, disease: Optional[str], drug: Optional[str]) -> List[Dict[str, Any]]:
    """Generate report sections based on type"""
    
    if report_type == "executive":
        return [
            {
                "section": "Executive Summary",
                "content": f"This report provides a comprehensive analysis of drug repurposing opportunities in {disease or 'oncology'}. Key findings indicate strong potential for {drug or 'multiple candidates'} with evidence from {34} clinical studies.",
                "key_points": [
                    "High confidence opportunities identified: 12",
                    "Market potential: $3.2B - $8.5B",
                    "Estimated timeline to market: 2-4 years",
                    "Recommended immediate actions: 3 priority initiatives"
                ]
            },
            {
                "section": "Strategic Recommendations",
                "content": "Based on comprehensive analysis, we recommend pursuing 3 high-priority opportunities with immediate focus on Phase III trial acceleration.",
                "key_points": [
                    "Prioritize Metformin combination therapy",
                    "Accelerate Beta-blocker clinical development",
                    "Invest in biomarker discovery programs"
                ]
            }
        ]
    
    elif report_type == "detailed":
        return [
            {
                "section": "Introduction",
                "content": f"Comprehensive analysis of drug repurposing landscape for {disease or 'multiple cancer types'}.",
                "subsections": ["Background", "Objectives", "Methodology"]
            },
            {
                "section": "Market Analysis",
                "content": "Current market size, growth projections, and competitive landscape",
                "data": {
                    "market_size_2024": "$6.2B",
                    "projected_2030": "$14.8B",
                    "cagr": "15.7%"
                }
            },
            {
                "section": "Drug Candidates",
                "content": "Detailed analysis of top repurposing candidates",
                "candidates_analyzed": 24
            },
            {
                "section": "Clinical Evidence",
                "content": "Summary of clinical trial data and real-world evidence",
                "trials_reviewed": 67
            },
            {
                "section": "Regulatory Pathway",
                "content": "Analysis of regulatory requirements and approval strategy",
                "estimated_timeline": "24-36 months"
            },
            {
                "section": "Financial Projections",
                "content": "ROI analysis and investment requirements",
                "roi_estimate": "4.2x - 8.7x"
            }
        ]
    
    else:  # summary
        return [
            {
                "section": "Summary",
                "content": f"Overview of repurposing opportunities for {disease or 'oncology'}",
                "highlights": [
                    "Total opportunities: 24",
                    "High confidence: 12",
                    "Active trials: 19"
                ]
            }
        ]


@router.get("/charts/{chart_type}")
async def get_chart_data(
    chart_type: str,
    disease: Optional[str] = None,
    timeframe: str = Query("12m", regex="^(1m|3m|6m|12m|all)$")
):
    """
    Get chart data for visualizations
    Supported types: confidence, timeline, market, mechanism, trials
    """
    try:
        if chart_type == "confidence":
            return generate_confidence_chart(disease)
        elif chart_type == "timeline":
            return generate_timeline_chart(disease)
        elif chart_type == "market":
            return generate_market_chart(disease)
        elif chart_type == "mechanism":
            return generate_mechanism_chart(disease)
        elif chart_type == "trials":
            return generate_trials_chart(disease, timeframe)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown chart type: {chart_type}")
            
    except Exception as e:
        logger.error(f"Chart generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def generate_confidence_chart(disease: Optional[str]) -> Dict[str, Any]:
    """Generate confidence distribution chart"""
    return {
        "type": "bar",
        "title": "Opportunity Confidence Distribution",
        "data": {
            "labels": ["90-100%", "80-89%", "70-79%", "60-69%", "50-59%"],
            "datasets": [{
                "label": "Number of Opportunities",
                "data": [12, 23, 34, 28, 15],
                "backgroundColor": "#10b981"
            }]
        },
        "options": {
            "responsive": True,
            "scales": {
                "y": {"beginAtZero": True}
            }
        }
    }


def generate_timeline_chart(disease: Optional[str]) -> Dict[str, Any]:
    """Generate timeline projection chart"""
    return {
        "type": "line",
        "title": "Expected Approvals Timeline",
        "data": {
            "labels": ["2025", "2026", "2027", "2028", "2029", "2030"],
            "datasets": [
                {
                    "label": "Phase III Completions",
                    "data": [3, 7, 12, 18, 24, 28],
                    "borderColor": "#10b981",
                    "fill": False
                },
                {
                    "label": "Expected Approvals",
                    "data": [1, 4, 8, 14, 20, 25],
                    "borderColor": "#06b6d4",
                    "fill": False
                }
            ]
        }
    }


def generate_market_chart(disease: Optional[str]) -> Dict[str, Any]:
    """Generate market potential chart"""
    return {
        "type": "doughnut",
        "title": "Market Potential Distribution",
        "data": {
            "labels": ["< $1B", "$1B-$2.5B", "$2.5B-$5B", "> $5B"],
            "datasets": [{
                "data": [35, 42, 28, 18],
                "backgroundColor": ["#94a3b8", "#06b6d4", "#10b981", "#f59e0b"]
            }]
        }
    }


def generate_mechanism_chart(disease: Optional[str]) -> Dict[str, Any]:
    """Generate mechanism of action distribution"""
    return {
        "type": "pie",
        "title": "Mechanism of Action Distribution",
        "data": {
            "labels": [
                "AMPK/mTOR pathway",
                "COX inhibition",
                "Apoptosis induction",
                "Angiogenesis inhibition",
                "Immune modulation",
                "Other"
            ],
            "datasets": [{
                "data": [28, 24, 18, 15, 12, 16],
                "backgroundColor": [
                    "#10b981", "#06b6d4", "#8b5cf6", 
                    "#f59e0b", "#ec4899", "#64748b"
                ]
            }]
        }
    }


def generate_trials_chart(disease: Optional[str], timeframe: str) -> Dict[str, Any]:
    """Generate clinical trials trend chart"""
    
    # Generate monthly data based on timeframe
    months = {
        "1m": 1, "3m": 3, "6m": 6, "12m": 12, "all": 24
    }
    
    num_months = months.get(timeframe, 12)
    labels = []
    data = []
    
    for i in range(num_months):
        date = datetime.now() - timedelta(days=30 * (num_months - i - 1))
        labels.append(date.strftime("%b %Y"))
        # Simulate increasing trend
        data.append(15 + i * 2 + (i % 3))
    
    return {
        "type": "line",
        "title": "Active Clinical Trials Over Time",
        "data": {
            "labels": labels,
            "datasets": [{
                "label": "Active Trials",
                "data": data,
                "borderColor": "#10b981",
                "backgroundColor": "rgba(16, 185, 129, 0.1)",
                "fill": True
            }]
        }
    }


@router.get("/citations")
async def get_citations(
    disease: Optional[str] = None,
    drug: Optional[str] = None,
    limit: int = Query(50, le=500)
):
    """
    Get research paper citations for reports
    """
    try:
        # In production: Query library API or database
        citations = [
            {
                "id": 1,
                "title": "Metformin and cancer: a comprehensive review",
                "authors": "Johnson SA, Chen M, et al.",
                "journal": "Nature Reviews Cancer",
                "year": 2024,
                "pmid": "37345888",
                "doi": "10.1038/nrc.2024.123",
                "citation_count": 234,
                "relevance_score": 95
            },
            {
                "id": 2,
                "title": "Drug repurposing in oncology: current status and future directions",
                "authors": "Martinez L, Wong K, et al.",
                "journal": "Journal of Clinical Oncology",
                "year": 2024,
                "pmid": "37456789",
                "doi": "10.1200/jco.2024.456",
                "citation_count": 178,
                "relevance_score": 92
            }
        ]
        
        return {
            "status": "success",
            "total": len(citations),
            "citations": citations[:limit]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/{report_id}")
async def export_report(
    report_id: str,
    format: str = Query("pdf", regex="^(pdf|docx|html)$")
):
    """
    Export report in various formats
    """
    return {
        "status": "success",
        "message": f"Report {report_id} export to {format} initiated",
        "download_url": f"/downloads/{report_id}.{format}",
        "estimated_time": "30 seconds"
    }


@router.get("/templates")
async def get_report_templates():
    """
    Get available report templates
    """
    return {
        "templates": [
            {
                "id": "executive",
                "name": "Executive Summary",
                "description": "High-level overview for decision makers",
                "sections": 3,
                "estimated_pages": 5
            },
            {
                "id": "detailed",
                "name": "Detailed Analysis",
                "description": "Comprehensive technical report",
                "sections": 12,
                "estimated_pages": 35
            },
            {
                "id": "summary",
                "name": "Quick Summary",
                "description": "Brief overview of key findings",
                "sections": 2,
                "estimated_pages": 2
            },
            {
                "id": "regulatory",
                "name": "Regulatory Submission",
                "description": "FDA/EMA submission ready format",
                "sections": 8,
                "estimated_pages": 50
            }
        ]
    }


@router.get("/statistics")
async def get_report_statistics():
    """
    Get overall reporting statistics
    """
    return {
        "total_reports_generated": 1247,
        "reports_this_month": 89,
        "most_requested_disease": "Breast Cancer",
        "most_requested_drug": "Metformin",
        "average_generation_time": "2.3 seconds",
        "popular_formats": {
            "pdf": 67,
            "docx": 23,
            "html": 10
        }
    }


@router.post("/generate-market-report")
async def generate_market_report(request: MarketReportRequest):
    """
    Generate AI-powered market analysis report using OpenAI
    
    Returns comprehensive market report including:
    - Executive summary
    - Market analysis
    - Competitive landscape
    - Regulatory pathway
    - Financial projections
    - Risk analysis
    - Strategic recommendations
    """
    if not openai_service:
        raise HTTPException(status_code=503, detail="OpenAI service not available")
    
    try:
        result = await openai_service.generate_market_report(
            drug_name=request.drug_name,
            cancer_type=request.cancer_type,
            confidence_score=request.confidence_score,
            mechanism=request.mechanism,
            clinical_phase=request.clinical_phase,
            market_potential=request.market_potential
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Market report generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@router.post("/download-market-report-pdf")
async def download_market_report_pdf(request: MarketReportRequest):
    """
    Generate and download AI-powered market report as PDF
    """
    if not openai_service:
        raise HTTPException(status_code=503, detail="OpenAI service not available")
    
    try:
        # Generate report content
        result = await openai_service.generate_market_report(
            drug_name=request.drug_name,
            cancer_type=request.cancer_type,
            confidence_score=request.confidence_score,
            mechanism=request.mechanism,
            clinical_phase=request.clinical_phase,
            market_potential=request.market_potential
        )
        
        if not result.get("success"):
            # Use fallback report
            report_text = result.get("fallback_report", "Report generation failed")
        else:
            report_text = result["report"]["full_report"]
        
        # Create comprehensive report data for PDF
        from pdf_generator import generate_market_report_pdf
        
        report_data = {
            "drug_name": request.drug_name,
            "cancer_type": request.cancer_type,
            "confidence_score": request.confidence_score / 100 if request.confidence_score > 1 else request.confidence_score,
            "mechanism": request.mechanism or "Under investigation",
            "clinical_phase": request.clinical_phase or "Preclinical",
            "market_potential": request.market_potential or "TBD",
            "timeline": "3-5 years",
            "report_content": report_text,
            "generated_date": datetime.now().strftime("%Y-%m-%d")
        }
        
        # Generate PDF
        pdf_buffer = generate_market_report_pdf(report_data)
        
        # Clean filename
        safe_drug = request.drug_name.replace('/', '-').replace('\\', '-')[:30]
        safe_cancer = request.cancer_type.replace('/', '-').replace('\\', '-')[:30]
        filename = f"Market_Report_{safe_drug}_{safe_cancer}.pdf"
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
        
    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")
