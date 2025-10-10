"""
API endpoint tests
"""
import pytest
from fastapi.testclient import TestClient


class TestAuthAPI:
    """Test authentication API endpoints."""
    
    def test_register_success(self, client):
        """Test successful user registration."""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword123",
            "nickname": "New User"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["message"] == "User registered successfully"
        assert data["data"]["username"] == "newuser"
        assert data["data"]["email"] == "newuser@example.com"
        assert data["data"]["is_active"] is True
        assert data["data"]["is_verified"] is False
    
    def test_register_duplicate_username(self, client, test_user):
        """Test registration with duplicate username."""
        user_data = {
            "username": "testuser",
            "email": "different@example.com",
            "password": "password123",
            "nickname": "Different User"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 400
        data = response.json()
        assert data["code"] == 400
        assert "Username already exists" in data["message"]
    
    def test_register_duplicate_email(self, client, test_user):
        """Test registration with duplicate email."""
        user_data = {
            "username": "differentuser",
            "email": "test@example.com",
            "password": "password123",
            "nickname": "Different User"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 400
        data = response.json()
        assert data["code"] == 400
        assert "Email already exists" in data["message"]
    
    def test_login_success(self, client, test_user):
        """Test successful login."""
        login_data = {
            "username": "testuser",
            "password": "testpassword"
        }
        
        response = client.post("/api/v1/auth/login", data=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["message"] == "Login successful"
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]
        assert data["data"]["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        login_data = {
            "username": "nonexistent",
            "password": "wrongpassword"
        }
        
        response = client.post("/api/v1/auth/login", data=login_data)
        
        assert response.status_code == 401
        data = response.json()
        assert data["code"] == 401
        assert "Invalid username or password" in data["message"]
    
    def test_get_current_user(self, client, auth_headers):
        """Test getting current user information."""
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["username"] == "testuser"
        assert data["data"]["email"] == "test@example.com"
    
    def test_get_current_user_unauthorized(self, client):
        """Test getting current user without authentication."""
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code in (401, 403)


class TestUsersAPI:
    """Test users API endpoints."""
    
    def test_get_user_profile(self, client, auth_headers, test_user):
        """Test getting user profile."""
        response = client.get("/api/v1/users/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["username"] == "testuser"
        assert data["data"]["email"] == "test@example.com"
    
    def test_update_user_profile(self, client, auth_headers, test_user):
        """Test updating user profile."""
        update_data = {
            "nickname": "Updated Nickname",
            "bio": "Updated bio"
        }
        
        response = client.put("/api/v1/users/me", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["nickname"] == "Updated Nickname"
    
    def test_get_user_stats(self, client, auth_headers, test_user):
        """Test getting user statistics."""
        response = client.get("/api/v1/users/me/stats", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "study_plans_count" in data["data"]
        assert "error_logs_count" in data["data"]
        assert "conversations_count" in data["data"]


class TestStudyPlansAPI:
    """Test study plans API endpoints."""
    
    def test_create_study_plan(self, client, auth_headers, sample_study_plan_data):
        """Test creating a study plan."""
        response = client.post(
            "/api/v1/study-plans/",
            json=sample_study_plan_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["title"] == "Python学习计划"
        assert data["data"].get("subject") in (None, "编程")
    
    def test_get_study_plans(self, client, auth_headers):
        """Test getting study plans."""
        response = client.get("/api/v1/study-plans/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert isinstance(data["data"], list)
    
    def test_get_study_plan_by_id(self, client, auth_headers, test_user, db_session):
        """Test getting a specific study plan."""
        # First create a study plan
        from app.models.models import StudyPlan
        study_plan = StudyPlan(
            user_id=test_user.id,
            title="Test Plan",
            description="Test Description",
            subject="Test Subject",
            difficulty_level="beginner",
            estimated_duration=30,
            is_public=True
        )
        db_session.add(study_plan)
        db_session.commit()
        db_session.refresh(study_plan)
        
        response = client.get(f"/api/v1/study-plans/{study_plan.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["title"] == "Test Plan"
    
    def test_update_study_plan(self, client, auth_headers, test_user, db_session):
        """Test updating a study plan."""
        # First create a study plan
        from app.models.models import StudyPlan
        study_plan = StudyPlan(
            user_id=test_user.id,
            title="Test Plan",
            description="Test Description",
            subject="Test Subject",
            difficulty_level="beginner",
            estimated_duration=30,
            is_public=True
        )
        db_session.add(study_plan)
        db_session.commit()
        db_session.refresh(study_plan)
        
        update_data = {
            "title": "Updated Plan",
            "description": "Updated Description"
        }
        
        response = client.put(
            f"/api/v1/study-plans/{study_plan.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["title"] == "Updated Plan"
    
    def test_delete_study_plan(self, client, auth_headers, test_user, db_session):
        """Test deleting a study plan."""
        # First create a study plan
        from app.models.models import StudyPlan
        study_plan = StudyPlan(
            user_id=test_user.id,
            title="Test Plan",
            description="Test Description",
            subject="Test Subject",
            difficulty_level="beginner",
            estimated_duration=30,
            is_public=True
        )
        db_session.add(study_plan)
        db_session.commit()
        db_session.refresh(study_plan)
        
        response = client.delete(f"/api/v1/study-plans/{study_plan.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["message"] == "Study plan deleted successfully"


class TestErrorLogsAPI:
    """Test error logs API endpoints."""
    
    def test_create_error_log(self, client, auth_headers, sample_error_log_data):
        """Test creating an error log."""
        response = client.post(
            "/api/v1/error-logs/",
            json=sample_error_log_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["question"] == "什么是Python？"
        assert data["data"]["subject"] == "编程"
    
    def test_get_error_logs(self, client, auth_headers):
        """Test getting error logs."""
        response = client.get("/api/v1/error-logs/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert isinstance(data["data"], list)
    
    def test_get_error_log_stats(self, client, auth_headers):
        """Test getting error log statistics."""
        response = client.get("/api/v1/error-logs/stats/summary", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        # backend returns detailed fields, not total_count/subjects
        assert "difficulty_distribution" in data["data"]


class TestConversationsAPI:
    """Test conversations API endpoints."""
    
    def test_create_conversation(self, client, auth_headers, sample_conversation_data):
        """Test creating a conversation."""
        response = client.post(
            "/api/v1/conversations/",
            json=sample_conversation_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["title"] == "Python学习讨论"
        assert data["data"].get("subject") in (None, "编程")
    
    def test_get_conversations(self, client, auth_headers):
        """Test getting conversations."""
        response = client.get("/api/v1/conversations/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert isinstance(data["data"], list)
    
    def test_get_conversation_stats(self, client, auth_headers):
        """Test getting conversation statistics."""
        response = client.get("/api/v1/conversations/stats/summary", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "total_conversations" in data["data"]


class TestHealthAPI:
    """Test health check API endpoints."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "Welcome to AI Education Assistant API" in data["message"]
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["status"] == "healthy"
        assert "version" in data["data"]

