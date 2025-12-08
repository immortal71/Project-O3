"""
Test script for Google Imagen API integration
Run this to verify the image generation works
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.image_generation import image_service


def test_image_generation():
    """Test the image generation service"""
    print("🎨 Testing Google Imagen API integration...")
    print("=" * 60)
    
    # Generate dashboard image with default parameters
    print("\n📝 Generating dashboard preview image...")
    print("   Drug: Metformin")
    print("   Cancer: Breast Cancer")
    print("   Confidence: 87%")
    print("\n⏳ Calling Google Imagen API (this may take 30-60 seconds)...\n")
    
    image_bytes = image_service.generate_dashboard_image(
        drug_name="Metformin",
        cancer_type="Breast Cancer",
        confidence=87,
        opportunities=1183,
        high_confidence=89,
        in_progress=24,
        progress_percent=78
    )
    
    if image_bytes:
        print("✅ SUCCESS! Image generated successfully")
        print(f"   Image size: {len(image_bytes)} bytes")
        
        # Save the image
        output_path = image_service.save_generated_image(image_bytes)
        print(f"   Saved to: {output_path}")
        print("\n🎉 You can now use this image in your homepage!")
        print(f"   Access it at: http://localhost:8000/api/images/dashboard-preview")
        
    else:
        print("❌ FAILED! Image generation failed")
        print("\n🔍 Possible issues:")
        print("   1. Invalid API key")
        print("   2. API quota exceeded")
        print("   3. Network connectivity issues")
        print("   4. API endpoint or format changed")
        print("\n💡 Check the console output above for error details")


if __name__ == "__main__":
    test_image_generation()
