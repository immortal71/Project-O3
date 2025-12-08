"""
Tests for authentication endpoints
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class TestAuthEndpoints:
    """Test authentication endpoints"""
    
    @pytest.mark.asyncio
    async def test_user_registration(self, async_client: AsyncClient, sample_user_data: dict):
        """Test user registration endpoint"""
        
        response = await async_client.post(
            "/api/v1/auth/register",
            json=sample_user_data
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # Check response structure
        assert "id" in data
        assert data["email"] == sample_user_data["email"]
        assert data["full_name"] == sample_user_data["full_name"]
        assert data["company_name"] == sample_user_data["company_name"]
        assert data["role"] == sample_user_data["role"]
        assert data["subscription_tier"] == sample_user_data["subscription_tier"]
        assert "password" not in data  # Password should not be returned
    
    @pytest.mark.asyncio
    async def test_user_registration_duplicate_email(self, async_client: AsyncClient, sample_user_data: dict):
        """Test registration with duplicate email"""
        
        # First registration
        response1 = await async_client.post("/api/v1/auth/register", json=sample_user_data)
        assert response1.status_code == 201
        
        # Second registration with same email
        response2 = await async_client.post("/api/v1/auth/register", json=sample_user_data)
        assert response2.status_code == 409
        
        data = response2.json()
        assert data["error"] == "RESOURCE_ALREADY_EXISTS"
        assert "email" in data["message"].lower()
    
    @pytest.mark.asyncio
    async def test_user_registration_invalid_email(self, async_client: AsyncClient, sample_user_data: dict):
        """Test registration with invalid email"""
        
        invalid_data = sample_user_data.copy()
        invalid_data["email"] = "invalid-email"
        
        response = await async_client.post("/api/v1/auth/register", json=invalid_data)
        assert response.status_code == 422
        
        data = response.json()
        assert data["error"] == "VALIDATION_ERROR"
    
    @pytest.mark.asyncio
    async def test_user_login(self, async_client: AsyncClient, sample_user_data: dict):
        """Test user login endpoint"""
        
        # First register a user
        await async_client.post("/api/v1/auth/register", json=sample_user_data)
        
        # Then login
        login_data = {
            "username": sample_user_data["email"],
            "password": sample_user_data["password"]
        }
        
        response = await async_client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
    
    @pytest.mark.asyncio
    async def test_user_login_invalid_credentials(self, async_client: AsyncClient, sample_user_data: dict):
        """Test login with invalid credentials"""
        
        # First register a user
        await async_client.post("/api/v1/auth/register", json=sample_user_data)
        
        # Login with wrong password
        login_data = {
            "username": sample_user_data["email"],
            "password": "wrongpassword"
        }
        
        response = await async_client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 401
        
        data = response.json()
        assert data["error"] == "AUTHENTICATION_FAILED"
    
    @pytest.mark.asyncio
    async def test_token_refresh(self, async_client: AsyncClient, sample_user_data: dict):
        """Test token refresh endpoint"""
        
        # Register and login
        await async_client.post("/api/v1/auth/register", json=sample_user_data)
        
        login_data = {
            "username": sample_user_data["email"],
            "password": sample_user_data["password"]
        }
        
        login_response = await async_client.post("/api/v1/auth/login", data=login_data)
        refresh_token = login_response.json()["refresh_token"]
        
        # Refresh token
        refresh_data = {"refresh_token": refresh_token}
        response = await async_client.post("/api/v1/auth/refresh", json=refresh_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    @pytest.mark.asyncio
    async def test_get_current_user(self, async_client: AsyncClient, sample_user_data: dict):
        """Test get current user endpoint"""
        
        # Register and login
        await async_client.post("/api/v1/auth/register", json=sample_user_data)
        
        login_data = {
            "username": sample_user_data["email"],
            "password": sample_user_data["password"]
        }
        
        login_response = await async_client.post("/api/v1/auth/login", data=login_data)
        access_token = login_response.json()["access_token"]
        
        # Get current user
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await async_client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["email"] == sample_user_data["email"]
        assert data["full_name"] == sample_user_data["full_name"]
        assert "password" not in data
    
    @pytest.mark.asyncio
    async def test_update_user_profile(self, async_client: AsyncClient, sample_user_data: dict):
        """Test update user profile endpoint"""
        
        # Register and login
        await async_client.post("/api/v1/auth/register", json=sample_user_data)
        
        login_data = {
            "username": sample_user_data["email"],
            "password": sample_user_data["password"]
        }
        
        login_response = await async_client.post("/api/v1/auth/login", data=login_data)
        access_token = login_response.json()["access_token"]
        
        # Update profile
        update_data = {
            "full_name": "Updated Name",
            "company_name": "Updated Company"
        }
        
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await async_client.put("/api/v1/auth/profile", json=update_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["full_name"] == "Updated Name"
        assert data["company_name"] == "Updated Company"
        assert data["email"] == sample_user_data["email"]  # Email shouldn't change
    
    @pytest.mark.asyncio
    async def test_change_password(self, async_client: AsyncClient, sample_user_data: dict):
        """Test change password endpoint"""
        
        # Register and login
        await async_client.post("/api/v1/auth/register", json=sample_user_data)
        
        login_data = {
            "username": sample_user_data["email"],
            "password": sample_user_data["password"]
        }
        
        login_response = await async_client.post("/api/v1/auth/login", data=login_data)
        access_token = login_response.json()["access_token"]
        
        # Change password
        password_data = {
            "current_password": sample_user_data["password"],
            "new_password": "NewSecurePassword123!"
        }
        
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await async_client.post("/api/v1/auth/change-password", json=password_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Password changed successfully"
        
        # Verify old password no longer works
        login_response_old = await async_client.post("/api/v1/auth/login", data=login_data)
        assert login_response_old.status_code == 401
        
        # Verify new password works
        new_login_data = {
            "username": sample_user_data["email"],
            "password": "NewSecurePassword123!"
        }
        login_response_new = await async_client.post("/api/v1/auth/login", data=new_login_data)
        assert login_response_new.status_code == 200
    
    @pytest.mark.asyncio
    async def test_logout(self, async_client: AsyncClient, sample_user_data: dict):
        """Test logout endpoint"""
        
        # Register and login
        await async_client.post("/api/v1/auth/register", json=sample_user_data)
        
        login_data = {
            "username": sample_user_data["email"],
            "password": sample_user_data["password"]
        }
        
        login_response = await async_client.post("/api/v1/auth/login", data=login_data)
        access_token = login_response.json()["access_token"]
        
        # Logout
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await async_client.post("/api/v1/auth/logout", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Logged out successfully"
        
        # Verify token no longer works
        me_response = await async_client.get("/api/v1/auth/me", headers=headers)
        assert me_response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_unauthorized_access(self, async_client: AsyncClient):
        """Test accessing protected endpoint without token"""
        
        response = await async_client.get("/api/v1/auth/me")
        assert response.status_code == 401
        
        data = response.json()
        assert data["error"] == "AUTHENTICATION_FAILED"
    
    @pytest.mark.asyncio
    async def test_invalid_token(self, async_client: AsyncClient):
        """Test accessing protected endpoint with invalid token"""
        
        headers = {"Authorization": "Bearer invalid-token"}
        response = await async_client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401
        
        data = response.json()
        assert data["error"] == "AUTHENTICATION_FAILED"
    
    @pytest.mark.asyncio
    async def test_registration_validation(self, async_client: AsyncClient):
        """Test registration input validation"""
        
        # Missing required fields
        incomplete_data = {
            "email": "test@example.com",
            "password": "password123"
            # Missing full_name, company_name
        }
        
        response = await async_client.post("/api/v1/auth/register", json=incomplete_data)
        assert response.status_code == 422
        
        # Invalid email format
        invalid_email_data = {
            "email": "invalid-email",
            "password": "password123",
            "full_name": "Test User",
            "company_name": "Test Company"
        }
        
        response = await async_client.post("/api/v1/auth/register", json=invalid_email_data)
        assert response.status_code == 422
        
        # Weak password
        weak_password_data = {
            "email": "test@example.com",
            "password": "123",
            "full_name": "Test User",
            "company_name": "Test Company"
        }
        
        response = await async_client.post("/api/v1/auth/register", json=weak_password_data)
        assert response.status_code == 422