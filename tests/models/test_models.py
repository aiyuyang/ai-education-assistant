"""
Database model tests
"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.models import User, StudyPlan, StudyTask, ErrorLog, Conversation, Message, UserSession
from app.core.security import get_password_hash


class TestUserModel:
    """Test User model."""
    
    def test_create_user(self, db_session):
        """Test creating a user."""
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=get_password_hash("password123"),
            nickname="Test User",
            is_active=True,
            is_verified=True
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        assert user.id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.nickname == "Test User"
        assert user.is_active is True
        assert user.is_verified is True
        assert user.created_at is not None
        assert user.updated_at is not None
    
    def test_user_relationships(self, db_session):
        """Test user relationships."""
        # Create user
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=get_password_hash("password123"),
            nickname="Test User",
            is_active=True,
            is_verified=True
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create study plan
        study_plan = StudyPlan(
            user_id=user.id,
            title="Test Plan",
            description="Test Description",
            subject="Test Subject",
            difficulty_level="beginner",
            estimated_duration=30,
            is_public=True
        )
        db_session.add(study_plan)
        db_session.commit()
        
        # Create error log
        error_log = ErrorLog(
            user_id=user.id,
            question="Test Question",
            user_answer="Test Answer",
            correct_answer="Correct Answer",
            subject="Test Subject",
            difficulty_level="easy",
            explanation="Test Explanation"
        )
        db_session.add(error_log)
        db_session.commit()
        
        # Create conversation
        conversation = Conversation(
            user_id=user.id,
            title="Test Conversation",
            subject="Test Subject",
            difficulty_level="beginner",
            is_public=False
        )
        db_session.add(conversation)
        db_session.commit()
        
        # Test relationships
        assert len(user.study_plans) == 1
        assert len(user.error_logs) == 1
        assert len(user.conversations) == 1
        
        assert user.study_plans[0].title == "Test Plan"
        assert user.error_logs[0].question == "Test Question"
        assert user.conversations[0].title == "Test Conversation"


class TestStudyPlanModel:
    """Test StudyPlan model."""
    
    def test_create_study_plan(self, db_session, test_user):
        """Test creating a study plan."""
        study_plan = StudyPlan(
            user_id=test_user.id,
            title="Python学习计划",
            description="学习Python编程基础",
            subject="编程",
            difficulty_level="beginner",
            estimated_duration=30,
            is_public=True
        )
        
        db_session.add(study_plan)
        db_session.commit()
        db_session.refresh(study_plan)
        
        assert study_plan.id is not None
        assert study_plan.user_id == test_user.id
        assert study_plan.title == "Python学习计划"
        assert study_plan.description == "学习Python编程基础"
        assert study_plan.subject == "编程"
        assert study_plan.difficulty_level == "beginner"
        assert study_plan.estimated_duration == 30
        assert study_plan.is_public is True
        assert study_plan.created_at is not None
        assert study_plan.updated_at is not None
    
    def test_study_plan_relationships(self, db_session, test_user):
        """Test study plan relationships."""
        # Create study plan
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
        
        # Create study task
        task = StudyTask(
            study_plan_id=study_plan.id,
            title="Test Task",
            description="Test Task Description",
            task_type="reading",
            difficulty_level="easy",
            estimated_duration=10,
            is_completed=False
        )
        db_session.add(task)
        db_session.commit()
        
        # Test relationships
        assert study_plan.user.username == "testuser"
        assert len(study_plan.tasks) == 1
        assert study_plan.tasks[0].title == "Test Task"


class TestStudyTaskModel:
    """Test StudyTask model."""
    
    def test_create_study_task(self, db_session, test_user):
        """Test creating a study task."""
        # Create study plan first
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
        
        # Create study task
        task = StudyTask(
            study_plan_id=study_plan.id,
            title="Python基础语法",
            description="学习Python的基本语法规则",
            task_type="reading",
            difficulty_level="easy",
            estimated_duration=10,
            is_completed=False
        )
        
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)
        
        assert task.id is not None
        assert task.study_plan_id == study_plan.id
        assert task.title == "Python基础语法"
        assert task.description == "学习Python的基本语法规则"
        assert task.task_type == "reading"
        assert task.difficulty_level == "easy"
        assert task.estimated_duration == 10
        assert task.is_completed is False
        assert task.created_at is not None
        assert task.updated_at is not None


class TestErrorLogModel:
    """Test ErrorLog model."""
    
    def test_create_error_log(self, db_session, test_user):
        """Test creating an error log."""
        error_log = ErrorLog(
            user_id=test_user.id,
            question="什么是Python？",
            user_answer="一种编程语言",
            correct_answer="Python是一种高级编程语言",
            subject="编程",
            difficulty_level="easy",
            explanation="Python是一种简单易学的编程语言"
        )
        
        db_session.add(error_log)
        db_session.commit()
        db_session.refresh(error_log)
        
        assert error_log.id is not None
        assert error_log.user_id == test_user.id
        assert error_log.question == "什么是Python？"
        assert error_log.user_answer == "一种编程语言"
        assert error_log.correct_answer == "Python是一种高级编程语言"
        assert error_log.subject == "编程"
        assert error_log.difficulty_level == "easy"
        assert error_log.explanation == "Python是一种简单易学的编程语言"
        assert error_log.created_at is not None
        assert error_log.updated_at is not None


class TestConversationModel:
    """Test Conversation model."""
    
    def test_create_conversation(self, db_session, test_user):
        """Test creating a conversation."""
        conversation = Conversation(
            user_id=test_user.id,
            title="Python学习讨论",
            subject="编程",
            difficulty_level="beginner",
            is_public=False
        )
        
        db_session.add(conversation)
        db_session.commit()
        db_session.refresh(conversation)
        
        assert conversation.id is not None
        assert conversation.user_id == test_user.id
        assert conversation.title == "Python学习讨论"
        assert conversation.subject == "编程"
        assert conversation.difficulty_level == "beginner"
        assert conversation.is_public is False
        assert conversation.created_at is not None
        assert conversation.updated_at is not None
    
    def test_conversation_relationships(self, db_session, test_user):
        """Test conversation relationships."""
        # Create conversation
        conversation = Conversation(
            user_id=test_user.id,
            title="Test Conversation",
            subject="Test Subject",
            difficulty_level="beginner",
            is_public=False
        )
        db_session.add(conversation)
        db_session.commit()
        db_session.refresh(conversation)
        
        # Create message
        message = Message(
            conversation_id=conversation.id,
            content="Hello, how can I help you?",
            message_type="ai",
            metadata_json={"model": "gpt-3.5-turbo"}
        )
        db_session.add(message)
        db_session.commit()
        
        # Test relationships
        assert conversation.user.username == "testuser"
        assert len(conversation.messages) == 1
        assert conversation.messages[0].content == "Hello, how can I help you?"


class TestMessageModel:
    """Test Message model."""
    
    def test_create_message(self, db_session, test_user):
        """Test creating a message."""
        # Create conversation first
        conversation = Conversation(
            user_id=test_user.id,
            title="Test Conversation",
            subject="Test Subject",
            difficulty_level="beginner",
            is_public=False
        )
        db_session.add(conversation)
        db_session.commit()
        db_session.refresh(conversation)
        
        # Create message
        message = Message(
            conversation_id=conversation.id,
            content="Hello, how can I help you?",
            message_type="ai",
            metadata_json={"model": "gpt-3.5-turbo", "tokens": 10}
        )
        
        db_session.add(message)
        db_session.commit()
        db_session.refresh(message)
        
        assert message.id is not None
        assert message.conversation_id == conversation.id
        assert message.content == "Hello, how can I help you?"
        assert message.message_type == "ai"
        assert message.metadata_json == {"model": "gpt-3.5-turbo", "tokens": 10}
        assert message.created_at is not None
        assert message.updated_at is not None


class TestUserSessionModel:
    """Test UserSession model."""
    
    def test_create_user_session(self, db_session, test_user):
        """Test creating a user session."""
        session = UserSession(
            user_id=test_user.id,
            token_jti="test-jti-123",
            expires_at=datetime.utcnow() + timedelta(minutes=30),
            is_revoked=False
        )
        
        db_session.add(session)
        db_session.commit()
        db_session.refresh(session)
        
        assert session.id is not None
        assert session.user_id == test_user.id
        assert session.token_jti == "test-jti-123"
        assert session.is_revoked is False
        assert session.created_at is not None
        assert session.updated_at is not None

