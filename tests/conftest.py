"""
Test configuration and fixtures
"""
import os
import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.database import get_db, Base
from app.core.config import settings
from app.core.security import get_password_hash
from app.models.models import User

TEST_DB = os.getenv("TEST_DB", "sqlite").lower()

if TEST_DB == "mysql":
    # CI MySQL connection
    SQLALCHEMY_DATABASE_URL = os.getenv(
        "MYSQL_TEST_URL",
        "mysql+pymysql://root:password@127.0.0.1:3306/ai_education_assistant?charset=utf8mb4",
    )
    engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True, future=True)
else:
    # Default: SQLite in-memory per process
    SQLALCHEMY_DATABASE_URL = "sqlite://"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

# Create test session
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_session():
    """Create a test database session."""
    # Create a fresh schema for each test
    Base.metadata.create_all(bind=engine)
    
    # Create session
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Drop tables after test to avoid locking/leaks
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database dependency override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(db_session):
    """Create a test user."""
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=get_password_hash("testpassword"),
        nickname="Test User",
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def auth_headers(client, test_user):
    """Get authentication headers for test user."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "testpassword"}
    )
    assert response.status_code == 200
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def sample_study_plan_data():
    """Sample study plan data for testing."""
    return {
        "title": "Python学习计划",
        "description": "学习Python编程基础",
        "subject": "编程",
        "difficulty_level": "beginner",
        "estimated_duration": 30,
        "is_public": True
    }


@pytest.fixture(scope="function")
def sample_error_log_data():
    """Sample error log data for testing."""
    return {
        "question": "什么是Python？",
        "user_answer": "一种编程语言",
        "correct_answer": "Python是一种高级编程语言",
        "subject": "编程",
        "difficulty_level": "easy",
        "explanation": "Python是一种简单易学的编程语言"
    }


@pytest.fixture(scope="function")
def sample_conversation_data():
    """Sample conversation data for testing."""
    return {
        "title": "Python学习讨论",
        "subject": "编程",
        "difficulty_level": "beginner",
        "is_public": False
    }

