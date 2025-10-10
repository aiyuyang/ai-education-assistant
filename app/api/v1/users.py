"""
User management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.dependencies import get_current_active_user, get_current_verified_user
from app.core.exceptions import NotFoundError, ValidationError
from app.db.database import get_db
from app.models.models import User
from app.schemas.request import UserUpdateRequest, PaginationRequest
from app.schemas.response import BaseResponse, UserResponse, PaginatedResponse

router = APIRouter()


@router.get("/me", response_model=BaseResponse[UserResponse])
async def get_my_profile(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's profile"""
    
    return BaseResponse(
        code=0,
        message="Profile retrieved successfully",
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


@router.put("/me", response_model=BaseResponse[UserResponse])
async def update_my_profile(
    user_data: UserUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile"""
    
    # Update user data
    if user_data.nickname is not None:
        current_user.nickname = user_data.nickname
    
    if user_data.avatar_url is not None:
        current_user.avatar_url = user_data.avatar_url
    
    db.commit()
    db.refresh(current_user)
    
    return BaseResponse(
        code=0,
        message="Profile updated successfully",
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


@router.delete("/me", response_model=BaseResponse[None])
async def delete_my_account(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete current user's account"""
    
    # Soft delete by deactivating the account
    current_user.is_active = False
    db.commit()
    
    return BaseResponse(
        code=0,
        message="Account deleted successfully",
        data=None
    )


@router.get("/{user_id}", response_model=BaseResponse[UserResponse])
async def get_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user by ID (public profile)"""
    
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise NotFoundError("User not found")
    
    return BaseResponse(
        code=0,
        message="User profile retrieved successfully",
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


@router.get("/", response_model=BaseResponse[List[UserResponse]])
async def search_users(
    query: Optional[str] = None,
    pagination: PaginationRequest = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Search users by username or nickname"""
    
    users_query = db.query(User).filter(User.is_active == True)
    
    if query:
        users_query = users_query.filter(
            (User.username.contains(query)) | 
            (User.nickname.contains(query))
        )
    
    # Apply pagination
    offset = (pagination.page - 1) * pagination.per_page
    users = users_query.offset(offset).limit(pagination.per_page).all()
    
    user_responses = [
        UserResponse(
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
        for user in users
    ]
    
    return BaseResponse(
        code=0,
        message="Users retrieved successfully",
        data=user_responses
    )


@router.post("/upload-avatar", response_model=BaseResponse[str])
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload user avatar"""
    
    # Validate file type
    if file.content_type not in ["image/jpeg", "image/png", "image/gif"]:
        raise ValidationError("Only JPEG, PNG, and GIF images are allowed")
    
    # Validate file size (10MB max)
    max_size = 10 * 1024 * 1024  # 10MB
    content = await file.read()
    if len(content) > max_size:
        raise ValidationError("File size exceeds 10MB limit")
    
    # In a real implementation, you would upload to a cloud storage service
    # For now, we'll just return a placeholder URL
    avatar_url = f"https://example.com/avatars/{current_user.id}_{file.filename}"
    
    # Update user's avatar URL
    current_user.avatar_url = avatar_url
    db.commit()
    
    return BaseResponse(
        code=0,
        message="Avatar uploaded successfully",
        data=avatar_url
    )


@router.get("/me/stats", response_model=BaseResponse[dict])
async def get_my_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's statistics"""
    
    # Get user statistics
    stats = {
        "study_plans_count": len(current_user.study_plans),
        "error_logs_count": len(current_user.error_logs),
        "conversations_count": len(current_user.conversations),
        "active_study_plans": len([p for p in current_user.study_plans if p.status == "ongoing"]),
        "resolved_error_logs": len([e for e in current_user.error_logs if e.status == "resolved"]),
        "active_conversations": len([c for c in current_user.conversations if c.is_active])
    }
    
    return BaseResponse(
        code=0,
        message="User statistics retrieved successfully",
        data=stats
    )

