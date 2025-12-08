"""
Main API router
"""

# Copyright (c) 2025 OncoPurpose (trovesx)
# All Rights Reserved.
# For licensing info, see LICENSE or contact oncopurpose@trovesx.com

from fastapi import APIRouter

from app.api.v1 import auth, drugs, search
from app import research_api

api_router = APIRouter()

# Include all API routers
api_router.include_router(auth.router)
api_router.include_router(drugs.router)
api_router.include_router(search.router)
api_router.include_router(research_api.router)