"""
Test configuration and fixtures for OncoPurpose API
"""

import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.database import Base, get_db
from app.main import app


# Test database configuration
TEST_DATABASE_URL = "postgresql+asyncpg://test_user:test_password@localhost:5432/oncopurpose_test"
SYNC_TEST_DATABASE_URL = "postgresql://test_user:test_password@localhost:5432/oncopurpose_test"

# Create test database engine
engine = create_async_engine(TEST_DATABASE_URL, echo=True)
TestSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """Create test database and tables"""
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield TestSessionLocal()
    
    # Drop all tables after tests
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def test_app() -> FastAPI:
    """Create test FastAPI application"""
    
    # Override database dependency
    async def override_get_db():
        async with TestSessionLocal() as session:
            yield session
    
    app.dependency_overrides[get_db] = override_get_db
    
    return app


@pytest.fixture
def client(test_app: FastAPI) -> Generator[TestClient, None, None]:
    """Create test client"""
    with TestClient(test_app) as test_client:
        yield test_client


@pytest_asyncio.fixture
async def async_client(test_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Create async test client"""
    async with AsyncClient(app=test_app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_drug_data():
    """Sample drug data for testing"""
    return {
        "name": "Test Drug",
        "generic_name": "Test Generic",
        "smiles": "CC(=O)OC1=CC=CC=C1C(=O)O",
        "molecular_formula": "C9H8O4",
        "molecular_weight": 180.16,
        "indication": "Test indication",
        "mechanism_of_action": "Test mechanism",
        "approval_status": "approved",
        "fda_approved": True,
        "approval_year": 2020
    }


@pytest.fixture
def sample_cancer_data():
    """Sample cancer data for testing"""
    return {
        "name": "Test Cancer",
        "icd_code": "C00",
        "mesh_term": "Test Neoplasms",
        "description": "Test cancer description",
        "prevalence": 100000,
        "incidence_rate": 10.0,
        "mortality_rate": 5.0,
        "age_group": "adult",
        "gender_preference": "both",
        "tissue_type": "epithelial"
    }


@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User",
        "company_name": "Test Company",
        "role": "researcher",
        "subscription_tier": "basic"
    }


@pytest.fixture
def auth_headers():
    """Sample authentication headers"""
    return {"Authorization": "Bearer test-token"}


class TestHelpers:
    """Helper functions for tests"""
    
    @staticmethod
    async def create_test_user(db: AsyncSession, user_data: dict):
        """Create a test user in the database"""
        from app.models.user import User
        from app.core.security import get_password_hash
        
        user = User(
            email=user_data["email"],
            password_hash=get_password_hash(user_data["password"]),
            full_name=user_data["full_name"],
            company_name=user_data["company_name"],
            role=user_data["role"],
            subscription_tier=user_data["subscription_tier"]
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    
    @staticmethod
    async def create_test_drug(db: AsyncSession, drug_data: dict):
        """Create a test drug in the database"""
        from app.models.drug import Drug
        
        drug = Drug(**drug_data)
        db.add(drug)
        await db.commit()
        await db.refresh(drug)
        return drug
    
    @staticmethod
    async def create_test_cancer(db: AsyncSession, cancer_data: dict):
        """Create a test cancer in the database"""
        from app.models.cancer import Cancer
        
        cancer = Cancer(**cancer_data)
        db.add(cancer)
        await db.commit()
        await db.refresh(cancer)
        return cancer
    
    @staticmethod
    def assert_response_structure(response_data: dict, expected_fields: list):
        """Assert that response has expected structure"""
        for field in expected_fields:
            assert field in response_data, f"Missing field: {field}"
    
    @staticmethod
    def assert_pagination_structure(response_data: dict):
        """Assert that paginated response has correct structure"""
        expected_fields = ["items", "total", "page", "size", "pages"]
        TestHelpers.assert_response_structure(response_data, expected_fields)
        
        # Check pagination metadata
        assert isinstance(response_data["items"], list)
        assert isinstance(response_data["total"], int)
        assert isinstance(response_data["page"], int)
        assert isinstance(response_data["size"], int)
        assert isinstance(response_data["pages"], int)
    
    @staticmethod
    def assert_error_response(response_data: dict, expected_error_code: str):
        """Assert that error response has correct structure"""
        expected_fields = ["error", "message", "details", "field", "help"]
        TestHelpers.assert_response_structure(response_data, expected_fields)
        assert response_data["error"] == expected_error_code


@pytest.fixture
def helpers():
    """Provide test helpers"""
    return TestHelpers