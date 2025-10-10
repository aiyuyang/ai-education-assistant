"""
Authentication API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, datetime

from app.core.config import settings
from app.core.security import (
    verify_password, get_password_hash, create_access_token, 
    create_refresh_token, verify_token, generate_jti
)
from app.core.dependencies import get_current_user, rate_limit_5_per_minute
from app.core.exceptions import AuthenticationError, ValidationError
from app.db.database import get_db
from app.db.redis import get_redis, set_cache, get_cache, add_to_set
from app.models.models import User, UserSession
from app.schemas.request import UserCreateRequest, UserLoginRequest, PasswordChangeRequest
from app.schemas.response import BaseResponse, TokenResponse, UserResponse

router = APIRouter()


@router.post("/register", response_model=BaseResponse[UserResponse])
async def register(
    user_data: UserCreateRequest,
    db: Session = Depends(get_db),
    rate_limit = Depends(rate_limit_5_per_minute)
):
    """Register a new user"""
    
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise ValidationError("Username already exists")
    
    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise ValidationError("Email already exists")
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password,
        nickname=user_data.nickname,
        is_active=True,
        is_verified=False
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return BaseResponse(
        code=0,
        message="User registered successfully",
        data=UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            nickname=user.nickname,
            avatar_url=user.avatar_url,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at.isoformat(),
            updated_at=user.updated_at.isoformat()
        )
    )


@router.post("/login", response_model=BaseResponse[TokenResponse])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    redis = Depends(get_redis),
    rate_limit = Depends(rate_limit_5_per_minute)
):
    """Login user and return tokens"""
    
    # Find user by username or email
    user = db.query(User).filter(
        (User.username == form_data.username) | (User.email == form_data.username)
    ).first()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise AuthenticationError("Invalid username or password")
    
    if not user.is_active:
        raise AuthenticationError("User account is inactive")
    
    # Generate tokens
    token_data = {
        "sub": str(user.id),
        "username": user.username,
        "jti": generate_jti()
    }
    
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    # Store session in database
    session = UserSession(
        user_id=user.id,
        token_jti=token_data["jti"],
        expires_at=datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    )
    db.add(session)
    db.commit()
    
    return BaseResponse(
        code=0,
        message="Login successful",
        data=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60
        )
    )


@router.post("/refresh", response_model=BaseResponse[TokenResponse])
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db),
    redis = Depends(get_redis)
):
    """Refresh access token"""
    
    # Verify refresh token
    payload = verify_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise AuthenticationError("Invalid refresh token")
    
    # Get user
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise AuthenticationError("User not found or inactive")
    
    # Generate new tokens
    token_data = {
        "sub": str(user.id),
        "username": user.username,
        "jti": generate_jti()
    }
    
    access_token = create_access_token(token_data)
    new_refresh_token = create_refresh_token(token_data)
    
    # Store new session
    session = UserSession(
        user_id=user.id,
        token_jti=token_data["jti"],
        expires_at=datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    )
    db.add(session)
    db.commit()
    
    return BaseResponse(
        code=0,
        message="Token refreshed successfully",
        data=TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60
        )
    )


@router.post("/logout", response_model=BaseResponse[None])
async def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    redis = Depends(get_redis)
):
    """Logout user and revoke token"""
    
    # Get current token JTI from request
    # Note: In a real implementation, you'd need to extract this from the request
    # For now, we'll mark all user sessions as revoked
    
    sessions = db.query(UserSession).filter(
        UserSession.user_id == current_user.id,
        UserSession.is_revoked == False
    ).all()
    
    for session in sessions:
        session.is_revoked = True
        # Add to blacklist
        await add_to_set("blacklisted_tokens", session.token_jti)
    
    db.commit()
    
    return BaseResponse(
        code=0,
        message="Logout successful",
        data=None
    )


@router.post("/change-password", response_model=BaseResponse[None])
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    
    # Verify current password
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise AuthenticationError("Current password is incorrect")
    
    # Update password
    current_user.password_hash = get_password_hash(password_data.new_password)
    db.commit()
    
    return BaseResponse(
        code=0,
        message="Password changed successfully",
        data=None
    )


@router.get("/me", response_model=BaseResponse[UserResponse])
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    
    return BaseResponse(
        code=0,
        message="User information retrieved successfully",
        data=UserResponse(
            id=current_user.id,
            username=current_user.username,
            email=current_user.email,
            nickname=current_user.nickname,
            avatar_url=current_user.avatar_url,
            is_active=current_user.is_active,
            is_verified=current_user.is_verified,
            created_at=current_user.created_at.isoformat(),
            updated_at=current_user.updated_at.isoformat()
        )
    )
