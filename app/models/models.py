"""
Database models for AI Education Assistant
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum, Date, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.db.database import Base


class UserStatus(str, enum.Enum):
    """User status enum"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class PlanStatus(str, enum.Enum):
    """Plan status enum"""
    ONGOING = "ongoing"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class TaskStatus(str, enum.Enum):
    """Task status enum"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TaskPriority(str, enum.Enum):
    """Task priority enum"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ErrorLogStatus(str, enum.Enum):
    """Error log status enum"""
    UNRESOLVED = "unresolved"
    RESOLVED = "resolved"
    MASTERED = "mastered"


class ErrorLogDifficulty(str, enum.Enum):
    """Error log difficulty enum"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class MessageRole(str, enum.Enum):
    """Message role enum"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ContentType(str, enum.Enum):
    """Content type enum"""
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"


class User(Base):
    """User model"""
    __tablename__ = "users"
    __table_args__ = {"sqlite_autoincrement": True}
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    nickname = Column(String(50), nullable=True)
    avatar_url = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    study_plans = relationship("StudyPlan", back_populates="user", cascade="all, delete-orphan")
    error_logs = relationship("ErrorLog", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")


class StudyPlan(Base):
    """Study plan model"""
    __tablename__ = "study_plans"
    __table_args__ = {"sqlite_autoincrement": True}
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    # Additional fields expected by tests/API
    subject = Column(String(50), nullable=True)
    difficulty_level = Column(String(20), nullable=True)
    estimated_duration = Column(Integer, nullable=True)
    is_public = Column(Boolean, default=False)
    is_ai_generated = Column(Boolean, default=False, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(PlanStatus), nullable=False, default=PlanStatus.ONGOING, index=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="study_plans")
    tasks = relationship("StudyTask", back_populates="plan", cascade="all, delete-orphan")


class StudyTask(Base):
    """Study task model"""
    __tablename__ = "study_tasks"
    __table_args__ = {"sqlite_autoincrement": True}
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    study_plan_id = Column(Integer, ForeignKey("study_plans.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(TaskStatus), nullable=False, default=TaskStatus.PENDING, index=True)
    priority = Column(Enum(TaskPriority), nullable=False, default=TaskPriority.MEDIUM)
    task_type = Column(String(50), nullable=True)
    difficulty_level = Column(String(20), nullable=True)
    estimated_duration = Column(Integer, nullable=True)
    is_completed = Column(Boolean, default=False)
    due_date = Column(DateTime, nullable=True, index=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    plan = relationship("StudyPlan", back_populates="tasks")


class ErrorLog(Base):
    """Error log model"""
    __tablename__ = "error_logs"
    __table_args__ = {"sqlite_autoincrement": True}
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    subject = Column(String(50), nullable=True, index=True)
    topic = Column(String(100), nullable=True)
    question_content = Column(Text, nullable=False)
    # Backward-compatible aliases/fields used by tests
    user_answer = Column(Text, nullable=True)
    question_image_url = Column(String(255), nullable=True)
    correct_answer = Column(Text, nullable=True)
    explanation = Column(Text, nullable=True)
    difficulty = Column(Enum(ErrorLogDifficulty), nullable=False, default=ErrorLogDifficulty.MEDIUM, index=True)
    # compatibility field used in some tests
    difficulty_level = Column(String(20), nullable=True)
    status = Column(Enum(ErrorLogStatus), nullable=False, default=ErrorLogStatus.UNRESOLVED, index=True)
    review_count = Column(Integer, default=0)
    last_reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now(), index=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="error_logs")

    # Property alias to support tests using `question`
    @property
    def question(self) -> str:
        return self.question_content

    @question.setter
    def question(self, value: str) -> None:
        self.question_content = value


class Conversation(Base):
    """Conversation model"""
    __tablename__ = "conversations"
    __table_args__ = {"sqlite_autoincrement": True}
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    subject = Column(String(50), nullable=True)
    difficulty_level = Column(String(20), nullable=True)
    is_public = Column(Boolean, default=False, index=True)
    title = Column(String(100), nullable=False)
    summary = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=func.now(), index=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    """Message model"""
    __tablename__ = "messages"
    __table_args__ = {"sqlite_autoincrement": True}
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    # Keep legacy enum role for backend filters while allowing string type for tests
    role = Column(Enum(MessageRole), nullable=True, index=True)
    message_type = Column(String(10), nullable=True, index=True)  # 'user' or 'ai'
    content = Column(Text, nullable=False)
    content_type = Column(Enum(ContentType), nullable=False, default=ContentType.TEXT)
    metadata_json = Column(JSON, nullable=True)
    tokens_used = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=func.now(), index=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")


class UserSession(Base):
    """User session model for JWT management"""
    __tablename__ = "user_sessions"
    __table_args__ = {"sqlite_autoincrement": True}
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_jti = Column(String(255), unique=True, nullable=False, index=True)
    is_revoked = Column(Boolean, default=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="sessions")


class SystemConfig(Base):
    """System configuration model"""
    __tablename__ = "system_configs"
    __table_args__ = {"sqlite_autoincrement": True}
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False)
    description = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
