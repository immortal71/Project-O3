"""
Image Generation Service using Google's Imagen API
"""

import os
import base64
import requests
from typing import Optional

# Google API Configuration  
GOOGLE_API_KEY = "AIzaSyBUkCwt3sZDicU_-_MUsqjWlaiO7Uo7TAQ"
# Try the image generation endpoint (Note: This API key might be for Gemini text, not Imagen)
# Alternative: Use a simpler image generation service or create a mockup
IMAGEN_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"


class ImageGenerationService:
    """Service for generating images using Google Imagen API"""
    
    def __init__(self):
        self.api_key = GOOGLE_API_KEY
        
    def generate_dashboard_image(
        self,
        drug_name: str = "Metformin",
        cancer_type: str = "Breast Cancer",
        confidence: int = 87,
        opportunities: int = 1183,
        high_confidence: int = 89,
        in_progress: int = 24,
        progress_percent: int = 78
    ) -> Optional[bytes]:
        """
        Generate a dashboard preview image for the hero section
        
        Args:
            drug_name: Name of the drug being analyzed
            cancer_type: Type of cancer
            confidence: Confidence percentage
            opportunities: Number of opportunities
            high_confidence: High confidence count
            in_progress: In progress count
            progress_percent: Progress percentage
            
        Returns:
            Image bytes or None if generation fails
        """
        
        # Detailed prompt for dashboard image
        prompt = f"""
        Design a clean, modern SaaS dashboard card for an AI oncology platform called OncoPurpose.
        
        The card should show:
        - Header: "ACTIVE ANALYSIS" with a "● Live" green status badge on the right
        - Main content: "{drug_name} → {cancer_type}" with {confidence}% confidence displayed prominently
        - Three stat boxes side by side showing:
          * {opportunities} Opportunities
          * {high_confidence} High Confidence
          * {in_progress} In Progress
        - A progress bar at {progress_percent}% labeled "Analysis Progress"
        - Below the main card, two small sections:
          * "Recent Searches" with 2 items (Metformin+Breast Cancer 2h ago, Statins+Prostate 1d ago)
          * "Trending Opportunities" with 2 items (Aspirin→Lung Cancer 92%, Ibuprofen→Colorectal 81%)
        
        Style requirements:
        - Light background (#ffffff or #f8fafc)
        - Teal/turquoise accent colors (#14b8a6, #0d9488) for highlights and progress bars
        - Clean sans-serif typography (Inter or similar)
        - Medical/clinical aesthetic with professional spacing
        - Subtle shadows and borders
        - Dashboard-style layout with clear visual hierarchy
        - Modern UI with rounded corners
        - Professional pharmaceutical/biotech look
        
        The image should look like a real, functional dashboard screenshot - not a mockup or illustration.
        Landscape orientation, approximately 1200x800px.
        """
        
        try:
            # Prepare the API request
            headers = {
                "Content-Type": "application/json"
            }
            
            payload = {
                "instances": [
                    {
                        "prompt": prompt
                    }
                ],
                "parameters": {
                    "sampleCount": 1,
                    "aspectRatio": "3:2",  # Landscape for dashboard
                    "safetyFilterLevel": "block_only_high",
                    "personGeneration": "dont_allow"
                }
            }
            
            # Make the API request
            response = requests.post(
                f"{IMAGEN_API_URL}?key={self.api_key}",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract the generated image
                if "predictions" in result and len(result["predictions"]) > 0:
                    prediction = result["predictions"][0]
                    
                    # The image might be in different formats depending on the API response
                    if "bytesBase64Encoded" in prediction:
                        image_data = base64.b64decode(prediction["bytesBase64Encoded"])
                        return image_data
                    elif "image" in prediction and "bytesBase64Encoded" in prediction["image"]:
                        image_data = base64.b64decode(prediction["image"]["bytesBase64Encoded"])
                        return image_data
                        
            else:
                print(f"API Error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Image generation failed: {str(e)}")
            return None
    
    def save_generated_image(self, image_bytes: bytes, filename: str = "dashboard-preview.png") -> str:
        """
        Save generated image to static assets directory
        
        Args:
            image_bytes: Image data in bytes
            filename: Filename to save as
            
        Returns:
            Path to saved image
        """
        # Define the path to save (in the parent directory's resources)
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "generated")
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, filename)
        
        with open(output_path, "wb") as f:
            f.write(image_bytes)
            
        return output_path


# Singleton instance
image_service = ImageGenerationService()
