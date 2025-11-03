"""
Response models for API endpoints
"""
from typing import Any, Optional, Generic, TypeVar, List
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
    is_ai_generated: Optional[bool] = None
    status: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    created_at: str
    updated_at: str


class StudyTaskResponse(BaseModel):
    """Study task response model"""
    title: str
    description: str
    estimated_hours: int
    priority: str
    resources: List[str]


class WeeklyScheduleResponse(BaseModel):
    """Weekly schedule response model"""
    week: int
    focus: str
    tasks: List[StudyTaskResponse]


class MilestoneResponse(BaseModel):
    """Milestone response model"""
    week: int
    milestone: str
    assessment: str


class AIStudyPlanResponse(BaseModel):
    """AI generated study plan response model"""
    plan_title: str
    overview: str
    learning_objectives: List[str]
    weekly_schedule: List[WeeklyScheduleResponse]
    milestones: List[MilestoneResponse]
    resources: List[str]
    tips: List[str]
    generated_at: str
    tokens_used: Optional[int] = None
    saved_plan_id: Optional[int] = None


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
    subject: Optional[str] = None
    difficulty_level: Optional[str] = None
    is_public: bool = False
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
