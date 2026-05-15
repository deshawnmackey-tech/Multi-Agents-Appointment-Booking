"""
Pytest configuration and fixtures.
"""
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from src.main import app
from src.database.session import get_db, Base
from src.config import get_settings

settings = get_settings()

# Create test database engine
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """
    Create a fresh database for each test.
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    """
    Create a test client with database dependency override.
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data() -> dict:
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "name": "Test User",
        "password": "TestPassword123!",
        "timezone": "UTC"
    }


@pytest.fixture
def sample_calendar_data() -> dict:
    """Sample calendar data for testing."""
    return {
        "name": "Test Calendar",
        "provider": "google",
        "external_id": "test_calendar_id",
        "timezone": "UTC",
        "access_token": "test_access_token",
        "is_primary": True
    }


@pytest.fixture
def sample_appointment_data() -> dict:
    """Sample appointment data for testing."""
    return {
        "title": "Test Appointment",
        "description": "Test Description",
        "location": "Test Location",
        "start_time": "2024-01-01T10:00:00Z",
        "end_time": "2024-01-01T11:00:00Z",
        "timezone": "UTC",
        "is_all_day": False
    }

# Made with Bob