"""
Image Generation API Endpoints
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional

from image_generation import image_service

router = APIRouter(prefix="/api/images", tags=["images"])


class DashboardImageRequest(BaseModel):
    """Request model for dashboard image generation"""
    drug_name: str = "Metformin"
    cancer_type: str = "Breast Cancer"
    confidence: int = 87
    opportunities: int = 1183
    high_confidence: int = 89
    in_progress: int = 24
    progress_percent: int = 78


@router.post("/generate-dashboard")
async def generate_dashboard_image(request: DashboardImageRequest):
    """
    Generate a dashboard preview image for the homepage hero section
    
    This endpoint uses Google's Imagen API to create a realistic dashboard screenshot
    based on the provided parameters.
    """
    try:
        # Generate the image
        image_bytes = image_service.generate_dashboard_image(
            drug_name=request.drug_name,
            cancer_type=request.cancer_type,
            confidence=request.confidence,
            opportunities=request.opportunities,
            high_confidence=request.high_confidence,
            in_progress=request.in_progress,
            progress_percent=request.progress_percent
        )
        
        if not image_bytes:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate image. Please check API key and try again."
            )
        
        # Save the image
        output_path = image_service.save_generated_image(image_bytes)
        
        return JSONResponse(
            content={
                "success": True,
                "message": "Dashboard image generated successfully",
                "path": output_path,
                "url": "/resources/generated/dashboard-preview.png"
            },
            status_code=200
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Image generation failed: {str(e)}"
        )


@router.get("/dashboard-preview")
async def get_dashboard_preview():
    """
    Get the latest generated dashboard preview image
    """
    import os
    
    image_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "resources",
        "generated",
        "dashboard-preview.png"
    )
    
    if not os.path.exists(image_path):
        raise HTTPException(
            status_code=404,
            detail="Dashboard preview image not found. Generate it first using POST /api/images/generate-dashboard"
        )
    
    return FileResponse(image_path, media_type="image/png")


@router.post("/generate-quick")
async def generate_quick_dashboard():
    """
    Quick endpoint to generate dashboard with default parameters
    """
    try:
        # Use default parameters
        image_bytes = image_service.generate_dashboard_image()
        
        if not image_bytes:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate image. Please check API key and try again."
            )
        
        # Save the image
        output_path = image_service.save_generated_image(image_bytes)
        
        return JSONResponse(
            content={
                "success": True,
                "message": "Dashboard image generated successfully with default parameters",
                "path": output_path,
                "url": "/resources/generated/dashboard-preview.png"
            },
            status_code=200
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Image generation failed: {str(e)}"
        )
