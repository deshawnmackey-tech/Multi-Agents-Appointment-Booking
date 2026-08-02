"""
Calendar model for managing user calendar connections.
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from src.database.session import Base
from src.database.types import GUID


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
        name: Friendly calendar name
        calendar_id: External calendar ID from provider
        external_id: Backward-compatible alias for the provider ID
        access_token: Encrypted OAuth access token
        refresh_token: Encrypted OAuth refresh token
        is_primary: Whether this is the user's primary calendar
        is_active: Whether the calendar connection is active
        last_synced: Last successful sync timestamp
        created_at: Connection creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "calendars"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    provider = Column(Enum(CalendarProvider), nullable=False)
    name = Column(String, nullable=False)
    calendar_id = Column(String, nullable=False)
    external_id = Column(String, nullable=False)
    access_token = Column(String, nullable=False)  # Should be encrypted
    refresh_token = Column(String)  # Should be encrypted
    is_primary = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    sync_enabled = Column(Boolean, default=True)
    timezone = Column(String, default="UTC")
    color = Column(String)
    last_synced = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="calendars")
    events = relationship("CalendarEvent", back_populates="calendar", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Calendar(id={self.id}, provider={self.provider}, external_id={self.external_id}, user_id={self.user_id})>"

# Made with Bob
