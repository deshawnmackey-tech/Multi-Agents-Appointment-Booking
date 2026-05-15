"""
Participant model for managing appointment participants.
"""
from sqlalchemy import Column, String, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum
from src.database.session import Base


class ParticipantStatus(str, enum.Enum):
    """Participant response status."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"


class Participant(Base):
    """
    Participant model representing people invited to appointments.
    
    Attributes:
        id: Unique participant identifier (UUID)
        appointment_id: Foreign key to appointment
        email: Participant's email address
        name: Participant's name
        status: Response status (pending, accepted, declined)
    """
    __tablename__ = "participants"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    appointment_id = Column(UUID(as_uuid=True), ForeignKey("appointments.id"), nullable=False)
    email = Column(String, nullable=False)
    name = Column(String)
    status = Column(Enum(ParticipantStatus), default=ParticipantStatus.PENDING)
    
    # Relationships
    appointment = relationship("Appointment", back_populates="participants")
    
    def __repr__(self) -> str:
        return f"<Participant(id={self.id}, email={self.email}, status={self.status})>"

# Made with Bob
