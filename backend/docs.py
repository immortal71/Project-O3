"""
API documentation configuration for OncoPurpose API
Implements OpenAPI/Swagger documentation with custom styling
"""

from typing import Dict, Any, Optional

from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.responses import HTMLResponse

from app.core.config import settings


class DocumentationConfig:
    """API documentation configuration"""
    
    def __init__(self):
        self.title = "OncoPurpose API"
        self.description = """
        # OncoPurpose - Oncology Drug Repurposing Platform
        
        ## Overview
        OncoPurpose is a comprehensive platform for oncology drug repurposing that combines 
        machine learning, external data integration, and collaborative research tools to 
        accelerate the discovery of new cancer treatments.
        
        ## Features
        - **Drug-Cancer Matching**: ML-powered prediction engine for drug repurposing
        - **External Data Integration**: PubMed, ClinicalTrials.gov, and DrugBank integration
        - **Research Collaboration**: Collaborative research tools and data sharing
        - **Business Intelligence**: Analytics and reporting for pharmaceutical companies
        
        ## Authentication
        This API uses JWT Bearer token authentication. Include the token in the 
        Authorization header: `Bearer <your-token>`
        
        ## Rate Limiting
        Rate limits are enforced based on subscription tier:
        - **Basic**: 100 requests/hour
        - **Professional**: 1000 requests/hour  
        - **Enterprise**: Unlimited requests
        
        ## Support
        For support and documentation, visit our [documentation site](https://docs.oncopurpose.com)
        """
        
        self.version = "1.0.0"
        self.contact = {
            "name": "OncoPurpose Support",
            "email": "support@oncopurpose.com",
            "url": "https://support.oncopurpose.com"
        }
        
        self.license_info = {
            "name": "Commercial License",
            "url": "https://oncopurpose.com/license"
        }
        
        self.servers = [
            {"url": "https://api.oncopurpose.com", "description": "Production server"},
            {"url": "https://staging-api.oncopurpose.com", "description": "Staging server"},
            {"url": "http://localhost:8000", "description": "Local development"}
        ]
        
        self.tags_metadata = [
            {
                "name": "authentication",
                "description": "User authentication and authorization endpoints",
                "externalDocs": {
                    "description": "Authentication Guide",
                    "url": "https://docs.oncopurpose.com/auth"
                }
            },
            {
                "name": "drugs",
                "description": "Drug information and management",
                "externalDocs": {
                    "description": "Drug Data Guide",
                    "url": "https://docs.oncopurpose.com/drugs"
                }
            },
            {
                "name": "cancers",
                "description": "Cancer type information and management",
                "externalDocs": {
                    "description": "Cancer Data Guide", 
                    "url": "https://docs.oncopurpose.com/cancers"
                }
            },
            {
                "name": "predictions",
                "description": "ML-powered drug-cancer prediction endpoints",
                "externalDocs": {
                    "description": "Prediction Guide",
                    "url": "https://docs.oncopurpose.com/predictions"
                }
            },
            {
                "name": "research",
                "description": "Research papers and external data integration",
                "externalDocs": {
                    "description": "Research Integration Guide",
                    "url": "https://docs.oncopurpose.com/research"
                }
            },
            {
                "name": "analytics",
                "description": "Business intelligence and analytics",
                "externalDocs": {
                    "description": "Analytics Guide",
                    "url": "https://docs.oncopurpose.com/analytics"
                }
            },
            {
                "name": "admin",
                "description": "Administrative endpoints (Admin users only)",
                "externalDocs": {
                    "description": "Admin Guide",
                    "url": "https://docs.oncopurpose.com/admin"
                }
            }
        ]
    
    def configure_openapi(self, app: FastAPI) -> FastAPI:
        """Configure OpenAPI documentation"""
        
        # Update app OpenAPI configuration
        app.title = self.title
        app.description = self.description
        app.version = self.version
        
        # Configure OpenAPI schema
        def custom_openapi():
            if app.openapi_schema:
                return app.openapi_schema
            
            from fastapi.openapi.utils import get_openapi
            
            openapi_schema = get_openapi(
                title=self.title,
                version=self.version,
                description=self.description,
                routes=app.routes,
                contact=self.contact,
                license_info=self.license_info,
                servers=self.servers
            )
            
            # Add security schemes
            openapi_schema["components"]["securitySchemes"] = {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                    "description": "JWT Bearer token authentication"
                },
                "ApiKeyAuth": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-API-Key",
                    "description": "API key for external integrations"
                }
            }
            
            # Add global security requirement
            openapi_schema["security"] = [{"BearerAuth": []}]
            
            # Add tags metadata
            openapi_schema["tags"] = self.tags_metadata
            
            # Add custom extensions
            openapi_schema["x-logo"] = {
                "url": "https://oncopurpose.com/assets/logo.png",
                "altText": "OncoPurpose Logo"
            }
            
            openapi_schema["x-tagGroups"] = [
                {
                    "name": "Core API",
                    "tags": ["authentication", "drugs", "cancers", "predictions"]
                },
                {
                    "name": "Research & Analytics",
                    "tags": ["research", "analytics"]
                },
                {
                    "name": "Administration",
                    "tags": ["admin"]
                }
            ]
            
            app.openapi_schema = openapi_schema
            return app.openapi_schema
        
        app.openapi = custom_openapi
        return app
    
    def add_documentation_routes(self, app: FastAPI) -> FastAPI:
        """Add custom documentation routes"""
        
        @app.get("/docs", include_in_schema=False)
        async def custom_swagger_ui_html():
            return get_swagger_ui_html(
                openapi_url=app.openapi_url,
                title=f"{self.title} - Swagger UI",
                oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
                swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
                swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
                swagger_favicon_url="https://oncopurpose.com/favicon.ico"
            )
        
        @app.get("/redoc", include_in_schema=False)
        async def redoc_html():
            return get_redoc_html(
                openapi_url=app.openapi_url,
                title=f"{self.title} - ReDoc",
                redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@2/bundles/redoc.standalone.js",
                with_google_fonts=False,
                redoc_favicon_url="https://oncopurpose.com/favicon.ico"
            )
        
        @app.get("/docs/json", include_in_schema=False)
        async def openapi_json():
            return app.openapi()
        
        return app


class ExampleGenerator:
    """Generate examples for API documentation"""
    
    @staticmethod
    def get_drug_examples():
        return {
            "drug_create": {
                "name": "Aspirin",
                "generic_name": "Acetylsalicylic acid",
                "smiles": "CC(=O)OC1=CC=CC=C1C(=O)O",
                "molecular_formula": "C9H8O4",
                "molecular_weight": 180.16,
                "indication": "Pain relief, anti-inflammatory",
                "mechanism_of_action": "Cyclooxygenase inhibitor",
                "approval_status": "approved",
                "fda_approved": True,
                "approval_year": 1950
            },
            "drug_response": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Aspirin",
                "generic_name": "Acetylsalicylic acid",
                "smiles": "CC(=O)OC1=CC=CC=C1C(=O)O",
                "molecular_formula": "C9H8O4",
                "molecular_weight": 180.16,
                "indication": "Pain relief, anti-inflammatory",
                "mechanism_of_action": "Cyclooxygenase inhibitor",
                "approval_status": "approved",
                "fda_approved": True,
                "approval_year": 1950,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }
    
    @staticmethod
    def get_cancer_examples():
        return {
            "cancer_create": {
                "name": "Breast Cancer",
                "icd_code": "C50",
                "mesh_term": "Breast Neoplasms",
                "description": "Malignant neoplasm of breast tissue",
                "prevalence": 1250000,
                "incidence_rate": 125.0,
                "mortality_rate": 20.0,
                "age_group": "adult",
                "gender_preference": "female",
                "tissue_type": "epithelial"
            },
            "cancer_response": {
                "id": "660e8400-e29b-41d4-a716-446655440001",
                "name": "Breast Cancer",
                "icd_code": "C50",
                "mesh_term": "Breast Neoplasms",
                "description": "Malignant neoplasm of breast tissue",
                "prevalence": 1250000,
                "incidence_rate": 125.0,
                "mortality_rate": 20.0,
                "age_group": "adult",
                "gender_preference": "female",
                "tissue_type": "epithelial",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }
    
    @staticmethod
    def get_prediction_examples():
        return {
            "prediction_request": {
                "drug_id": "550e8400-e29b-41d4-a716-446655440000",
                "cancer_id": "660e8400-e29b-41d4-a716-446655440001",
                "confidence_threshold": 0.7
            },
            "prediction_response": {
                "id": "770e8400-e29b-41d4-a716-446655440002",
                "drug_id": "550e8400-e29b-41d4-a716-446655440000",
                "cancer_id": "660e8400-e29b-41d4-a716-446655440001",
                "prediction_score": 0.85,
                "confidence_interval": [0.82, 0.88],
                "prediction_class": "high_potential",
                "reasoning": "Strong molecular pathway alignment",
                "evidence_sources": ["PubMed", "ClinicalTrials.gov"],
                "created_at": "2024-01-15T10:35:00Z"
            }
        }
    
    @staticmethod
    def get_error_examples():
        return {
            "validation_error": {
                "error": "VALIDATION_ERROR",
                "message": "Validation failed",
                "details": {
                    "fields": {
                        "email": "Invalid email format",
                        "password": "Password too short"
                    }
                },
                "field": None,
                "help": "Please check your input data and try again"
            },
            "authentication_error": {
                "error": "AUTHENTICATION_FAILED",
                "message": "Invalid credentials",
                "details": None,
                "field": None,
                "help": "Please check your credentials and try again"
            },
            "not_found_error": {
                "error": "RESOURCE_NOT_FOUND",
                "message": "Drug not found: 550e8400-e29b-41d4-a716-446655440000",
                "details": None,
                "field": None,
                "help": "The requested resource could not be found"
            }
        }


# Global instances
docs_config = DocumentationConfig()
example_generator = ExampleGenerator()


def setup_documentation(app: FastAPI) -> FastAPI:
    """Set up API documentation"""
    
    # Configure OpenAPI
    app = docs_config.configure_openapi(app)
    
    # Add documentation routes
    app = docs_config.add_documentation_routes(app)
    
    return app