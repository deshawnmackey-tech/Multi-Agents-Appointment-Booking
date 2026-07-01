"""
Participant model for managing appointment participants.
"""
from sqlalchemy import Column, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
import uuid
import enum
from src.database.session import Base
from src.database.types import GUID


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
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    appointment_id = Column(GUID(), ForeignKey("appointments.id"), nullable=False)
    email = Column(String, nullable=False)
    name = Column(String)
    status = Column(Enum(ParticipantStatus), default=ParticipantStatus.PENDING)
    
    # Relationships
    appointment = relationship("Appointment", back_populates="participants")
    
    def __repr__(self) -> str:
        return f"<Participant(id={self.id}, email={self.email}, status={self.status})>"

# Made with Bob
