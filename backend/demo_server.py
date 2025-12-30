"""
🎯 MINIMAL DEMO SERVER - For Founders Fest Live Presentation
No dependencies on main.py infrastructure - just the demo!

Run with: python demo_server.py
Then open: http://localhost:8000/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import demo endpoints
try:
    from demo_api import router as demo_router
    demo_available = True
except ImportError as e:
    print(f"⚠️  Demo API import failed: {e}")
    print("Make sure demo_api.py, demo_dataset.py, and confidence_scorer.py are in the same directory")
    demo_available = False


# Create minimal app
app = FastAPI(
    title="OncoPurpose Demo API - Founders Fest Edition",
    description="Fast, pre-computed drug repurposing insights for live demo",
    version="1.0.0-demo",
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "🚀 OncoPurpose Demo API - Ready for Founders Fest!",
        "status": "operational",
        "demo_endpoints": "/api/v1/demo/*",
        "documentation": "/docs",
        "quick_tests": [
            "/api/v1/demo/search?q=metformin",
            "/api/v1/demo/search?q=breast",
            "/api/v1/demo/analyze/drug/aspirin",
            "/api/v1/demo/stats"
        ]
    }


@app.get("/health", tags=["Health"])
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "demo_ready": demo_available
    }


# Include demo router
if demo_available:
    app.include_router(demo_router)
    print("✅ Demo API endpoints loaded successfully!")
else:
    print("❌ Demo API not loaded - check imports")
    

@app.on_event("startup")
async def startup():
    """Startup message"""
    print("="*70)
    print("🚀 ONCOPURPOSE DEMO SERVER STARTED")
    print("="*70)
    print("\n📍 API Documentation: http://localhost:8000/docs")
    print("\n🎯 Quick Test URLs:")
    print("   • http://localhost:8000/api/v1/demo/search?q=metformin")
    print("   • http://localhost:8000/api/v1/demo/search?q=breast")
    print("   • http://localhost:8000/api/v1/demo/analyze/drug/aspirin")
    print("   • http://localhost:8000/api/v1/demo/stats")
    print("\n💡 Ready for live demo!")
    print("="*70)


if __name__ == "__main__":
    # Run server
    uvicorn.run(
        "demo_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload for development
        log_level="info"
    )
