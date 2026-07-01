"""
UserPreference model for managing user scheduling preferences.
"""
from sqlalchemy import Column, Integer, Boolean, Time, ForeignKey
from sqlalchemy.orm import relationship
import uuid
from src.database.session import Base
from src.database.types import GUID


class UserPreference(Base):
    """
    UserPreference model for storing user scheduling preferences.
    
    Attributes:
        id: Unique preference identifier (UUID)
        user_id: Foreign key to user (one-to-one relationship)
        working_hours_start: Start of working hours
        working_hours_end: End of working hours
        preferred_meeting_duration: Default meeting duration in minutes
        buffer_time_minutes: Buffer time between meetings
        notification_email: Enable email notifications
        notification_sms: Enable SMS notifications
        reminder_24h: Send reminder 24 hours before
        reminder_1h: Send reminder 1 hour before
        auto_decline_conflicts: Automatically decline conflicting invites
    """
    __tablename__ = "user_preferences"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False, unique=True)
    
    # Working hours
    working_hours_start = Column(Time, default="09:00:00")
    working_hours_end = Column(Time, default="17:00:00")
    
    # Meeting preferences
    preferred_meeting_duration = Column(Integer, default=30)  # minutes
    buffer_time_minutes = Column(Integer, default=15)  # minutes
    
    # Notification preferences
    notification_email = Column(Boolean, default=True)
    notification_sms = Column(Boolean, default=False)
    reminder_24h = Column(Boolean, default=True)
    reminder_1h = Column(Boolean, default=True)
    
    # Automation preferences
    auto_decline_conflicts = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="preferences")
    
    def __repr__(self) -> str:
        return f"<UserPreference(id={self.id}, user_id={self.user_id})>"

# Made with Bob
