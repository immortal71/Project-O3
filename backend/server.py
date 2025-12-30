"""
OncoРurpose Production Server - Founders Fest 2025
REAL DATA Backend with 6,800+ Compounds + MySQL Database

Run: python server.py
Access: http://localhost:8000/docs
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import uvicorn
import logging
import os
from pathlib import Path
from dotenv import load_dotenv
from contextlib import asynccontextmanager

# Load environment
load_dotenv()

# Import APIs
from integrated_api import router as api_router
from database_api import router as db_router
from library_api import router as library_router
from discovery_api import router as discovery_router
from dashboard_api import router as dashboard_router
from reports_api import router as reports_router

# Configure logging
log_level = os.getenv('LOG_LEVEL', 'INFO')
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("🚀 Starting OncoPurpose server...")
    
    # Load in-memory data
    from data_loader import get_data_loader
    loader = get_data_loader()
    stats = loader.get_stats()
    
    # Test SQLite database connection
    from sqlite_connection import test_connection
    db_stats = test_connection()
    
    if db_stats:
        logger.info("✅ SQLite database connected")
    else:
        logger.warning("⚠️  Database not found - using in-memory data only")
    
    print("\n" + "=" * 70)
    print("🚀 ONCOPURPOSE - PRODUCTION SERVER")
    print("=" * 70)
    print(f"\n📊 IN-MEMORY DATA:")
    print(f"   ✅ Broad Hub: {stats['total_drugs']:,} drugs")
    print(f"   ✅ Oncology: {stats['oncology_compounds']} compounds")
    print(f"   ✅ Hero Cases: {stats['hero_cases']} (gold standard)")
    print(f"   ✅ Mechanisms: {stats['mechanisms']:,}")
    print(f"   ✅ Targets: {stats['targets']:,}")
    
    if db_stats:
        print(f"\n💾 DATABASE: SQLite connected")
        print(f"   ✅ Drugs in DB: {db_stats.get('drugs', 0):,}")
        print(f"   ✅ Papers in DB: {db_stats.get('papers', 0):,}")
        print(f"   📍 Location: {db_stats.get('file', 'N/A')}")
        print(f"   💾 Size: {db_stats.get('size_mb', 0):.2f} MB")
    
    print(f"\n🌐 SERVER: http://localhost:{os.getenv('PORT', 8000)}")
    print(f"📚 DOCS: http://localhost:{os.getenv('PORT', 8000)}/docs")
    print(f"🔒 RATE LIMIT: {os.getenv('RATE_LIMIT_PER_MINUTE', 60)}/min")
    print("=" * 70 + "\n")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down server...")

# Create app with lifespan
app = FastAPI(
    title="OncoPurpose Drug Repurposing Platform",
    description="6,800+ compounds from Broad Institute + Hero Cases + MySQL Database",
    version="3.0.0",
    lifespan=lifespan
)

# State for rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS - Production settings
cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5500').split(',')
environment = os.getenv('ENVIRONMENT', 'development')

if environment == 'production':
    # Strict CORS for production
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )
else:
    # Permissive CORS for development
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include routers FIRST (before static files)
app.include_router(api_router)  # In-memory endpoints
app.include_router(db_router)   # Database endpoints
app.include_router(library_router)  # Research library endpoints
app.include_router(discovery_router)  # Discovery/analysis endpoints
app.include_router(dashboard_router)  # Dashboard generation endpoints
app.include_router(reports_router)  # Report generation endpoints


# API Routes (defined before static files)
@app.get("/api")
@limiter.limit("60/minute")
async def api_root(request: Request):
    return {
        "platform": "OncoPurpose Drug Repurposing",
        "version": "3.0.0 - Production Ready",
        "compounds": "6,800+",
        "research_papers": "547",
        "endpoints": {
            "in_memory": "/api/v1/*",
            "database": "/api/v1/db/*",
            "library": "/api/v1/library/*",
            "discovery": "/api/discovery/*",
            "dashboard": "/api/dashboard/*",
            "reports": "/api/reports/*",
            "docs": "/docs"
        },
        "status": "online"
    }


@app.get("/health")
@limiter.limit("120/minute")
async def health_check(request: Request):
    """Enhanced health check"""
    from data_loader import get_data_loader
    from sqlite_connection import test_connection
    
    loader = get_data_loader()
    stats = loader.get_stats()
    db_status = test_connection()
    
    return {
        "status": "healthy",
        "environment": environment,
        "database": "connected" if db_status else "disconnected",
        "in_memory_drugs": stats['total_drugs'],
        "timestamp": None  # Will be set by FastAPI
    }


# Mount static files LAST (catch-all for HTML pages)
static_dir = Path(__file__).parent.parent
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")


# Error handling middleware
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if environment == 'development' else "An error occurred"
        }
    )


if __name__ == "__main__":
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8000))
    workers = int(os.getenv('WORKERS', 1))  # Use 1 for dev, 4+ for production
    
    uvicorn.run(
        "server:app",
        host=host,
        port=port,
        reload=(environment == 'development'),
        workers=workers if environment == 'production' else 1
    )

