"""
Response models for API endpoints
"""
from typing import Any, Optional, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar('T')


class BaseResponse(BaseModel, Generic[T]):
    """Base response model"""
    code: int = 0
    message: str = "Success"
    data: Optional[T] = None


class ErrorResponse(BaseModel):
    """Error response model"""
    code: int
    message: str
    details: Optional[dict] = None


class PaginationMeta(BaseModel):
    """Pagination metadata"""
    page: int
    per_page: int
    total: int
    pages: int
    has_next: bool
    has_prev: bool


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response model"""
    code: int = 0
    message: str = "Success"
    data: list[T]
    meta: PaginationMeta


class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    """User response model"""
    id: int
    username: str
    email: str
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: str
    updated_at: str


class StudyPlanResponse(BaseModel):
    """Study plan response model"""
    id: int
    user_id: int
    title: str
    description: Optional[str] = None
    subject: Optional[str] = None
    difficulty_level: Optional[str] = None
    estimated_duration: Optional[int] = None
    is_public: Optional[bool] = None
    status: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    created_at: str
    updated_at: str


class ErrorLogResponse(BaseModel):
    """Error log response model"""
    id: int
    user_id: int
    subject: Optional[str] = None
    topic: Optional[str] = None
    question: Optional[str] = None
    question_content: str
    question_image_url: Optional[str] = None
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    difficulty: str
    status: str
    review_count: int
    last_reviewed_at: Optional[str] = None
    created_at: str
    updated_at: str


class ConversationResponse(BaseModel):
    """Conversation response model"""
    id: int
    user_id: int
    title: str
    summary: Optional[str] = None
    is_active: bool
    created_at: str
    updated_at: str


class MessageResponse(BaseModel):
    """Message response model"""
    id: int
    conversation_id: int
    role: str
    content: str
    content_type: str
    metadata_json: Optional[dict] = None
    tokens_used: Optional[int] = None
    created_at: str
