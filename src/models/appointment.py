"""
Appointment model for managing scheduled appointments.
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from src.database.session import Base


class AppointmentStatus(str, enum.Enum):
    """Appointment status options."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class Appointment(Base):
    """
    Appointment model representing scheduled appointments.
    
    Attributes:
        id: Unique appointment identifier (UUID)
        user_id: Foreign key to user who created the appointment
        title: Appointment title
        description: Detailed description
        start_time: Appointment start time
        end_time: Appointment end time
        timezone: Timezone for the appointment
        location: Meeting location (physical or virtual)
        status: Current status (pending, confirmed, cancelled)
        created_by_agent: Name of the agent that created this appointment
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "appointments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    timezone = Column(String, default="UTC")
    location = Column(String)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.PENDING)
    created_by_agent = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="appointments")
    calendar_events = relationship("CalendarEvent", back_populates="appointment", cascade="all, delete-orphan")
    participants = relationship("Participant", back_populates="appointment", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Appointment(id={self.id}, title={self.title}, status={self.status})>"

# Made with Bob
