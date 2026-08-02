"""
Database session management and connection handling.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from typing import Generator
from src.config import get_settings

settings = get_settings()

# Get database configuration from settings
db_config = settings.get_database_config()

# Create database engine with comprehensive configuration
engine = create_engine(
    db_config["url"],
    pool_size=db_config["pool_size"],
    max_overflow=db_config["max_overflow"],
    pool_timeout=db_config["pool_timeout"],
    pool_recycle=db_config["pool_recycle"],
    pool_pre_ping=db_config["pool_pre_ping"],
    echo=db_config["echo"],
    echo_pool=db_config["echo_pool"],
    connect_args=db_config["connect_args"]
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for all models
class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    Yields a database session and ensures it's closed after use.
    
    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database by creating all tables.
    Should be called on application startup.
    """
    Base.metadata.create_all(bind=engine)

# Made with Bob
