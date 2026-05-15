"""
Pydantic schemas for user preference operations.
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import time
from typing import Optional, List, Dict, Any
from uuid import UUID


class WorkingHoursBase(BaseModel):
    """Base working hours schema."""
    day_of_week: int = Field(..., ge=0, le=6, description="Day of week (0=Monday, 6=Sunday)")
    start_time: time = Field(..., description="Working hours start time")
    end_time: time = Field(..., description="Working hours end time")
    is_working_day: bool = Field(default=True, description="Whether this is a working day")


class PreferenceBase(BaseModel):
    """Base preference schema with common fields."""
    default_meeting_duration: int = Field(default=30, ge=15, le=480, description="Default meeting duration in minutes")
    buffer_time: int = Field(default=0, ge=0, le=60, description="Buffer time between meetings in minutes")
    max_meetings_per_day: Optional[int] = Field(None, ge=1, le=20, description="Maximum meetings per day")
    preferred_meeting_times: Optional[List[str]] = Field(None, description="Preferred meeting time slots")
    notification_preferences: Dict[str, bool] = Field(
        default_factory=lambda: {
            "email": True,
            "sms": False,
            "push": True
        },
        description="Notification channel preferences"
    )
    reminder_times: List[int] = Field(
        default_factory=lambda: [15, 60],
        description="Default reminder times in minutes before event"
    )


class PreferenceCreate(PreferenceBase):
    """Schema for creating user preferences."""
    working_hours: Optional[List[WorkingHoursBase]] = Field(None, description="Working hours configuration")


class PreferenceUpdate(BaseModel):
    """Schema for updating user preferences."""
    default_meeting_duration: Optional[int] = Field(None, ge=15, le=480)
    buffer_time: Optional[int] = Field(None, ge=0, le=60)
    max_meetings_per_day: Optional[int] = Field(None, ge=1, le=20)
    preferred_meeting_times: Optional[List[str]] = None
    notification_preferences: Optional[Dict[str, bool]] = None
    reminder_times: Optional[List[int]] = None


class WorkingHoursResponse(WorkingHoursBase):
    """Schema for working hours response."""
    id: UUID
    preference_id: UUID
    
    model_config = ConfigDict(from_attributes=True)


class PreferenceResponse(PreferenceBase):
    """Schema for preference response."""
    id: UUID
    user_id: UUID
    working_hours: List[WorkingHoursResponse]
    created_at: Any  # datetime
    updated_at: Any  # datetime
    
    model_config = ConfigDict(from_attributes=True)


class AvailabilityRequest(BaseModel):
    """Schema for checking user availability."""
    start_date: Any = Field(..., description="Start date for availability check")  # datetime
    end_date: Any = Field(..., description="End date for availability check")  # datetime
    duration: int = Field(..., ge=15, description="Required duration in minutes")
    calendar_ids: Optional[List[UUID]] = Field(None, description="Calendars to check")


class AvailabilitySlot(BaseModel):
    """Schema for an available time slot."""
    start_time: Any  # datetime
    end_time: Any  # datetime
    calendar_id: UUID


class AvailabilityResponse(BaseModel):
    """Schema for availability response."""
    available_slots: List[AvailabilitySlot] = Field(default_factory=list, description="List of available time slots")
    total_slots: int = Field(..., description="Total number of available slots")

# Made with Bob