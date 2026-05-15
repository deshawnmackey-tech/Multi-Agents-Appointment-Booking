"""
Calendar model for managing user calendar connections.
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from src.database.session import Base


class CalendarProvider(str, enum.Enum):
    """Supported calendar providers."""
    GOOGLE = "google"
    OUTLOOK = "outlook"
    IOS = "ios"


class Calendar(Base):
    """
    Calendar model representing connected calendar accounts.
    
    Attributes:
        id: Unique calendar identifier (UUID)
        user_id: Foreign key to user
        provider: Calendar provider (google, outlook, ios)
        calendar_id: External calendar ID from provider
        access_token: Encrypted OAuth access token
        refresh_token: Encrypted OAuth refresh token
        is_primary: Whether this is the user's primary calendar
        sync_enabled: Whether sync is enabled for this calendar
        created_at: Connection creation timestamp
    """
    __tablename__ = "calendars"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    provider = Column(Enum(CalendarProvider), nullable=False)
    calendar_id = Column(String, nullable=False)
    access_token = Column(String, nullable=False)  # Should be encrypted
    refresh_token = Column(String)  # Should be encrypted
    is_primary = Column(Boolean, default=False)
    sync_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="calendars")
    events = relationship("CalendarEvent", back_populates="calendar", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Calendar(id={self.id}, provider={self.provider}, user_id={self.user_id})>"

# Made with Bob
