"""
CalendarEvent model for tracking synced events across calendars.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from src.database.session import Base


class SyncStatus(str, enum.Enum):
    """Sync status for calendar events."""
    SYNCED = "synced"
    PENDING = "pending"
    FAILED = "failed"


class CalendarEvent(Base):
    """
    CalendarEvent model representing synced events in external calendars.
    Links appointments to their corresponding events in external calendar systems.
    
    Attributes:
        id: Unique event identifier (UUID)
        appointment_id: Foreign key to appointment
        calendar_id: Foreign key to calendar
        external_event_id: Event ID in the external calendar system
        sync_status: Current sync status
        last_synced_at: Last successful sync timestamp
    """
    __tablename__ = "calendar_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    appointment_id = Column(UUID(as_uuid=True), ForeignKey("appointments.id"), nullable=False)
    calendar_id = Column(UUID(as_uuid=True), ForeignKey("calendars.id"), nullable=False)
    external_event_id = Column(String, nullable=False)
    sync_status = Column(Enum(SyncStatus), default=SyncStatus.PENDING)
    last_synced_at = Column(DateTime)
    
    # Relationships
    appointment = relationship("Appointment", back_populates="calendar_events")
    calendar = relationship("Calendar", back_populates="events")
    
    def __repr__(self) -> str:
        return f"<CalendarEvent(id={self.id}, external_id={self.external_event_id}, status={self.sync_status})>"

# Made with Bob
