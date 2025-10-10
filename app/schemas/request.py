"""
Request models for API endpoints
"""
from typing import Optional
from pydantic import BaseModel, validator, root_validator
from datetime import datetime, date


class UserCreateRequest(BaseModel):
    """User creation request"""
    username: str
    email: str
    password: str
    nickname: Optional[str] = None
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3 or len(v) > 50:
            raise ValueError('Username must be between 3 and 50 characters')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v


class UserLoginRequest(BaseModel):
    """User login request"""
    username: str
    password: str


class UserUpdateRequest(BaseModel):
    """User update request"""
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None


class PasswordChangeRequest(BaseModel):
    """Password change request"""
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 6:
            raise ValueError('New password must be at least 6 characters')
        return v


class StudyPlanCreateRequest(BaseModel):
    """Study plan creation request"""
    title: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    
    @validator('title')
    def validate_title(cls, v):
        if len(v) < 1 or len(v) > 100:
            raise ValueError('Title must be between 1 and 100 characters')
        return v


class StudyPlanUpdateRequest(BaseModel):
    """Study plan update request"""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class StudyTaskCreateRequest(BaseModel):
    """Study task creation request"""
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    due_date: Optional[datetime] = None
    
    @validator('title')
    def validate_title(cls, v):
        if len(v) < 1 or len(v) > 200:
            raise ValueError('Title must be between 1 and 200 characters')
        return v
    
    @validator('priority')
    def validate_priority(cls, v):
        if v not in ['low', 'medium', 'high']:
            raise ValueError('Priority must be low, medium, or high')
        return v


class StudyTaskUpdateRequest(BaseModel):
    """Study task update request"""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None


class ErrorLogCreateRequest(BaseModel):
    """Error log creation request"""
    subject: Optional[str] = None
    topic: Optional[str] = None
    question_content: Optional[str] = None
    # Backward-compatible aliases
    question: Optional[str] = None
    user_answer: Optional[str] = None
    question_image_url: Optional[str] = None
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    difficulty: str = "medium"
    difficulty_level: Optional[str] = None
    
    @root_validator(pre=True)
    def populate_aliases(cls, values):
        if not values.get('question_content') and values.get('question'):
            values['question_content'] = values['question']
        if not values.get('difficulty') and values.get('difficulty_level'):
            values['difficulty'] = values['difficulty_level']
        return values
    
    @validator('difficulty', always=True)
    def validate_difficulty(cls, v, values):
        # allow alias `difficulty_level`
        if not v and values.get('difficulty_level'):
            v = values['difficulty_level']
        v = (v or 'medium').lower()
        if v not in ['easy', 'medium', 'hard']:
            raise ValueError('Difficulty must be easy, medium, or hard')
        return v


class ErrorLogUpdateRequest(BaseModel):
    """Error log update request"""
    subject: Optional[str] = None
    topic: Optional[str] = None
    question_content: Optional[str] = None
    question_image_url: Optional[str] = None
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    difficulty: Optional[str] = None
    status: Optional[str] = None


class ConversationCreateRequest(BaseModel):
    """Conversation creation request"""
    title: Optional[str] = None


class MessageCreateRequest(BaseModel):
    """Message creation request"""
    content: str
    content_type: str = "text"
    metadata_json: Optional[dict] = None
    
    @validator('content')
    def validate_content(cls, v):
        if len(v) < 1:
            raise ValueError('Message content cannot be empty')
        return v
    
    @validator('content_type')
    def validate_content_type(cls, v):
        if v not in ['text', 'image', 'file']:
            raise ValueError('Content type must be text, image, or file')
        return v


class PaginationRequest(BaseModel):
    """Pagination request"""
    page: int = 1
    per_page: int = 20
    
    @validator('page')
    def validate_page(cls, v):
        if v < 1:
            raise ValueError('Page must be greater than 0')
        return v
    
    @validator('per_page')
    def validate_per_page(cls, v):
        if v < 1 or v > 100:
            raise ValueError('Per page must be between 1 and 100')
        return v
