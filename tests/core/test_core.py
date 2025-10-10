"""
Core functionality tests
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from app.core.security import (
    verify_password, get_password_hash, create_access_token,
    create_refresh_token, verify_token, generate_jti
)
from app.core.exceptions import AuthenticationError, ValidationError
from app.core.dependencies import get_current_user
from app.models.models import User


class TestSecurityFunctions:
    """Test security utility functions."""
    
    def test_password_hashing(self):
        """Test password hashing and verification."""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        # Hash should be different from original password
        assert hashed != password
        assert len(hashed) > 0
        
        # Verification should work
        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False
    
    def test_password_hash_consistency(self):
        """Test that password hashing is consistent."""
        password = "testpassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Hashes should be different (due to salt)
        assert hash1 != hash2
        
        # But both should verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True
    
    def test_jwt_token_creation(self):
        """Test JWT token creation and verification."""
        data = {
            "sub": "123",
            "username": "testuser",
            "jti": "test-jti"
        }
        
        # Create access token
        access_token = create_access_token(data)
        assert access_token is not None
        assert len(access_token) > 0
        
        # Create refresh token
        refresh_token = create_refresh_token(data)
        assert refresh_token is not None
        assert len(refresh_token) > 0
        
        # Tokens should be different
        assert access_token != refresh_token
    
    def test_jwt_token_verification(self):
        """Test JWT token verification."""
        data = {
            "sub": "123",
            "username": "testuser",
            "jti": "test-jti"
        }
        
        # Create token
        token = create_access_token(data)
        
        # Verify token
        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == "123"
        assert payload["username"] == "testuser"
        assert payload["jti"] == "test-jti"
        assert payload["type"] == "access"
    
    def test_jwt_token_verification_invalid(self):
        """Test JWT token verification with invalid token."""
        invalid_token = "invalid.token.here"
        
        payload = verify_token(invalid_token)
        assert payload is None
    
    def test_jwt_token_expiration(self):
        """Test JWT token expiration."""
        data = {
            "sub": "123",
            "username": "testuser",
            "jti": "test-jti"
        }
        
        # Create token with short expiration
        token = create_access_token(data, expires_delta=timedelta(seconds=1))
        
        # Verify token immediately
        payload = verify_token(token)
        assert payload is not None
        
        # Wait for expiration
        import time
        time.sleep(2)
        
        # Token should now be invalid
        payload = verify_token(token)
        assert payload is None
    
    def test_generate_jti(self):
        """Test JTI generation."""
        jti1 = generate_jti()
        jti2 = generate_jti()
        
        # JTIs should be different
        assert jti1 != jti2
        
        # JTIs should be 32 characters long
        assert len(jti1) == 32
        assert len(jti2) == 32
        
        # JTIs should contain only alphanumeric characters
        assert jti1.isalnum()
        assert jti2.isalnum()


class TestExceptions:
    """Test custom exceptions."""
    
    def test_authentication_error(self):
        """Test AuthenticationError exception."""
        error = AuthenticationError("Invalid credentials")
        
        assert error.message == "Invalid credentials"
        assert error.code == 401
        assert error.details is None
    
    def test_authentication_error_with_details(self):
        """Test AuthenticationError with details."""
        error = AuthenticationError("Invalid credentials", details={"reason": "expired"})
        
        assert error.message == "Invalid credentials"
        assert error.code == 401
        assert error.details == {"reason": "expired"}
    
    def test_validation_error(self):
        """Test ValidationError exception."""
        error = ValidationError("Invalid input data")
        
        assert error.message == "Invalid input data"
        assert error.code == 400
        assert error.details is None
    
    def test_validation_error_with_details(self):
        """Test ValidationError with details."""
        error = ValidationError("Invalid input data", details={"field": "email"})
        
        assert error.message == "Invalid input data"
        assert error.code == 400
        assert error.details == {"field": "email"}


class TestDependencies:
    """Test dependency injection functions."""
    
    @pytest.mark.asyncio
    async def test_get_current_user_success(self, db_session, test_user):
        """Test getting current user successfully."""
        # Create a valid token
        token_data = {
            "sub": str(test_user.id),
            "username": test_user.username,
            "jti": "test-jti"
        }
        token = create_access_token(token_data)
        
        # Mock the request
        from fastapi import Request
        # 模拟 FastAPI 依赖：我们直接传递 credentials 和 db
        class DummyCreds:
            def __init__(self, token):
                self.scheme = "Bearer"
                self.credentials = token
        creds = DummyCreds(token)
        
        # Test dependency
        user = await get_current_user(credentials=creds, db=db_session)
        
        assert user.id == test_user.id
        assert user.username == test_user.username
    
    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, db_session):
        """Test getting current user with invalid token."""
        from fastapi import Request
        class DummyCreds:
            def __init__(self, token):
                self.scheme = "Bearer"
                self.credentials = token
        creds = DummyCreds("invalid-token")
        
        with pytest.raises(AuthenticationError):
            await get_current_user(credentials=creds, db=db_session)
    
    @pytest.mark.asyncio
    async def test_get_current_user_no_token(self, db_session):
        """Test getting current user without token."""
        from fastapi import Request
        class DummyCreds:
            def __init__(self, token=None):
                self.scheme = "Bearer"
                self.credentials = token
        creds = DummyCreds(None)
        
        with pytest.raises(AuthenticationError):
            await get_current_user(credentials=creds, db=db_session)
    
    @pytest.mark.asyncio
    async def test_get_current_user_inactive_user(self, db_session):
        """Test getting current user with inactive user."""
        # Create inactive user
        user = User(
            username="inactiveuser",
            email="inactive@example.com",
            password_hash=get_password_hash("password123"),
            nickname="Inactive User",
            is_active=False,
            is_verified=True
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create token for inactive user
        token_data = {
            "sub": str(user.id),
            "username": user.username,
            "jti": "test-jti"
        }
        token = create_access_token(token_data)
        
        # Mock the request
        from fastapi import Request
        class DummyCreds:
            def __init__(self, token):
                self.scheme = "Bearer"
                self.credentials = token
        creds = DummyCreds(token)
        
        # Test dependency
        with pytest.raises(AuthenticationError):
            await get_current_user(credentials=creds, db=db_session)


class TestRateLimiting:
    """Test rate limiting functionality."""
    
    @patch('app.core.dependencies.get_redis')
    @pytest.mark.asyncio
    async def test_rate_limit_5_per_minute(self, mock_get_redis):
        """Test rate limiting 5 requests per minute."""
        # Mock Redis client
        mock_redis = MagicMock()
        mock_get_redis.return_value = mock_redis
        mock_redis.get.return_value = "3"  # 3 requests already made
        
        from app.core.dependencies import rate_limit_5_per_minute
        from fastapi import Request
        
        request = MagicMock(spec=Request)
        request.client.host = "127.0.0.1"
        
        # Should not raise exception (3 < 5)
        await rate_limit_5_per_minute(request, mock_redis)
    
    @patch('app.core.dependencies.get_redis')
    @pytest.mark.asyncio
    async def test_rate_limit_exceeded(self, mock_get_redis):
        """Test rate limiting when exceeded."""
        # Mock Redis client
        mock_redis = MagicMock()
        mock_get_redis.return_value = mock_redis
        mock_redis.get.return_value = "6"  # 6 requests already made
        
        from app.core.dependencies import rate_limit_5_per_minute
        from fastapi import Request
        
        request = MagicMock(spec=Request)
        request.client.host = "127.0.0.1"
        
        # Should raise exception (6 > 5)
        with pytest.raises(Exception):  # Rate limit exceeded
            await rate_limit_5_per_minute(request, mock_redis)
