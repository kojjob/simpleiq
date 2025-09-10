"""
Comprehensive tests for authentication system
"""

from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from jose import jwt

from app.core.config import settings
from app.main import app
from app.services.user_service import USERS_DB


@pytest.fixture(autouse=True)
def clear_users_db():
    """Clear the in-memory users database before each test"""
    USERS_DB.clear()
    yield
    USERS_DB.clear()


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture
def test_user_data():
    """Sample user data for testing"""
    return {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User",
        "company_name": "Test Company"
    }


@pytest.fixture
def registered_user(client, test_user_data):
    """Register a user and return the user data"""
    response = client.post("/api/v1/auth/register", json=test_user_data)
    assert response.status_code == 200
    return test_user_data


@pytest.fixture
def auth_token(client, registered_user):
    """Get an authentication token for a registered user"""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": registered_user["email"],
            "password": registered_user["password"]
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


class TestUserRegistration:
    """Test user registration functionality"""

    def test_successful_registration(self, client, test_user_data):
        """Test successful user registration"""
        response = client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["full_name"] == test_user_data["full_name"]
        assert data["company_name"] == test_user_data["company_name"]
        assert data["is_active"] is True
        assert "id" in data
        assert "password" not in data
        assert "hashed_password" not in data

    def test_registration_without_company(self, client):
        """Test registration without company name (optional field)"""
        user_data = {
            "email": "nocompany@example.com",
            "password": "Password123!",
            "full_name": "No Company User"
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["company_name"] is None

    def test_registration_duplicate_email(self, client, registered_user):
        """Test that duplicate email registration fails"""
        response = client.post("/api/v1/auth/register", json=registered_user)
        
        # Now properly returns 400 for duplicate email
        assert response.status_code == 400

    def test_registration_invalid_email(self, client):
        """Test registration with invalid email format"""
        user_data = {
            "email": "invalid-email",
            "password": "Password123!",
            "full_name": "Test User"
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 422

    def test_registration_missing_fields(self, client):
        """Test registration with missing required fields"""
        # Missing password
        response = client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "full_name": "Test User"
        })
        assert response.status_code == 422

        # Missing email
        response = client.post("/api/v1/auth/register", json={
            "password": "Password123!",
            "full_name": "Test User"
        })
        assert response.status_code == 422

        # Missing full_name
        response = client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "Password123!"
        })
        assert response.status_code == 422


class TestUserLogin:
    """Test user login functionality"""

    def test_successful_login(self, client, registered_user):
        """Test successful user login"""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": registered_user["email"],
                "password": registered_user["password"]
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        
        # Verify token is valid JWT
        payload = jwt.decode(
            data["access_token"],
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        assert payload["sub"] == registered_user["email"]

    def test_login_wrong_password(self, client, registered_user):
        """Test login with wrong password"""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": registered_user["email"],
                "password": "WrongPassword123!"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Incorrect email or password"

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user"""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "Password123!"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Incorrect email or password"

    def test_login_invalid_content_type(self, client, registered_user):
        """Test login with JSON instead of form data"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": registered_user["email"],
                "password": registered_user["password"]
            }
        )
        
        assert response.status_code == 422


class TestCurrentUser:
    """Test current user endpoint"""

    def test_get_current_user(self, client, registered_user, auth_token):
        """Test getting current user with valid token"""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == registered_user["email"]
        assert data["full_name"] == registered_user["full_name"]
        assert data["company_name"] == registered_user["company_name"]
        assert data["is_active"] is True
        assert "password" not in data
        assert "hashed_password" not in data

    def test_get_current_user_no_token(self, client):
        """Test accessing current user without token"""
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

    def test_get_current_user_invalid_token(self, client):
        """Test accessing current user with invalid token"""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Could not validate credentials"

    def test_get_current_user_expired_token(self, client):
        """Test accessing current user with expired token"""
        # Create an expired token
        expire = datetime.utcnow() - timedelta(minutes=30)
        payload = {"sub": "test@example.com", "exp": expire}
        expired_token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Could not validate credentials"


class TestCORSConfiguration:
    """Test CORS configuration"""

    def test_cors_preflight_allowed_origin(self, client):
        """Test CORS preflight request from allowed origin"""
        response = client.options(
            "/api/v1/auth/register",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        
        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
        assert "POST" in response.headers["access-control-allow-methods"]

    def test_cors_preflight_disallowed_origin(self, client):
        """Test CORS preflight request from disallowed origin"""
        response = client.options(
            "/api/v1/auth/register",
            headers={
                "Origin": "http://evil.com",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        
        assert response.status_code == 400


class TestAuthenticationFlow:
    """Test complete authentication flow"""

    def test_complete_auth_flow(self, client):
        """Test complete registration -> login -> get user flow"""
        # 1. Register a new user
        user_data = {
            "email": "flow@example.com",
            "password": "FlowPassword123!",
            "full_name": "Flow Test User",
            "company_name": "Flow Company"
        }
        
        register_response = client.post("/api/v1/auth/register", json=user_data)
        assert register_response.status_code == 200
        
        # 2. Login with the new user
        login_response = client.post(
            "/api/v1/auth/login",
            data={
                "username": user_data["email"],
                "password": user_data["password"]
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # 3. Get current user info
        me_response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert me_response.status_code == 200
        user_info = me_response.json()
        assert user_info["email"] == user_data["email"]
        assert user_info["full_name"] == user_data["full_name"]
        
        # 4. Try to register with same email (should fail)
        duplicate_response = client.post("/api/v1/auth/register", json=user_data)
        assert duplicate_response.status_code == 400  # Now properly returns 400
        
        # 5. Logout is handled on frontend by removing token
        # No backend logout endpoint needed for JWT