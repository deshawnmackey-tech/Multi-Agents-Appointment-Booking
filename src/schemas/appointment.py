"""
Pydantic schemas for appointment-related operations.
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List
from uuid import UUID


class ParticipantBase(BaseModel):
    """Base participant schema."""
    email: str = Field(..., description="Participant email")
    name: Optional[str] = Field(None, description="Participant name")
    is_organizer: bool = Field(default=False, description="Whether participant is organizer")
    response_status: str = Field(default="needsAction", description="Response status")


class ParticipantCreate(ParticipantBase):
    """Schema for creating a participant."""
    pass


class ParticipantResponse(ParticipantBase):
    """Schema for participant response."""
    id: UUID
    appointment_id: UUID
    
    model_config = ConfigDict(from_attributes=True)


class AppointmentBase(BaseModel):
    """Base appointment schema with common fields."""
    title: str = Field(..., min_length=1, max_length=200, description="Appointment title")
    description: Optional[str] = Field(None, description="Appointment description")
    location: Optional[str] = Field(None, max_length=500, description="Appointment location")
    start_time: datetime = Field(..., description="Appointment start time")
    end_time: datetime = Field(..., description="Appointment end time")
    timezone: str = Field(default="UTC", description="Appointment timezone")
    is_all_day: bool = Field(default=False, description="Whether appointment is all-day")


class AppointmentCreate(AppointmentBase):
    """Schema for creating a new appointment."""
    calendar_id: UUID = Field(..., description="Calendar ID for the appointment")
    participants: Optional[List[ParticipantCreate]] = Field(None, description="List of participants")
    recurrence_rule: Optional[str] = Field(None, description="iCalendar recurrence rule")
    reminders: Optional[List[int]] = Field(None, description="Reminder times in minutes before event")


class AppointmentUpdate(BaseModel):
    """Schema for updating appointment information."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    location: Optional[str] = Field(None, max_length=500)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    timezone: Optional[str] = None
    is_all_day: Optional[bool] = None
    status: Optional[str] = None


class AppointmentResponse(AppointmentBase):
    """Schema for appointment response."""
    id: UUID
    calendar_id: UUID
    user_id: UUID
    external_id: Optional[str]
    status: str
    recurrence_rule: Optional[str]
    participants: List[ParticipantResponse]
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class AppointmentSearchRequest(BaseModel):
    """Schema for searching appointments."""
    start_date: Optional[datetime] = Field(None, description="Search from this date")
    end_date: Optional[datetime] = Field(None, description="Search until this date")
    calendar_ids: Optional[List[UUID]] = Field(None, description="Filter by calendar IDs")
    query: Optional[str] = Field(None, description="Search query for title/description")
    status: Optional[str] = Field(None, description="Filter by status")


class AppointmentConflictCheck(BaseModel):
    """Schema for checking appointment conflicts."""
    start_time: datetime = Field(..., description="Proposed start time")
    end_time: datetime = Field(..., description="Proposed end time")
    calendar_ids: Optional[List[UUID]] = Field(None, description="Calendars to check")
    exclude_appointment_id: Optional[UUID] = Field(None, description="Appointment ID to exclude from check")


class AppointmentConflictResponse(BaseModel):
    """Schema for conflict check response."""
    has_conflict: bool = Field(..., description="Whether conflicts exist")
    conflicts: List[AppointmentResponse] = Field(default_factory=list, description="List of conflicting appointments")
    suggested_times: Optional[List[dict]] = Field(None, description="Suggested alternative times")


class AppointmentBookingRequest(BaseModel):
    """Schema for natural language appointment booking."""
    request: str = Field(..., min_length=1, description="Natural language booking request")
    preferred_calendars: Optional[List[UUID]] = Field(None, description="Preferred calendars for booking")
    auto_resolve_conflicts: bool = Field(default=False, description="Automatically resolve conflicts")

# Made with Bob