"""
Pydantic schemas for calendar-related operations.
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List
from uuid import UUID


class CalendarBase(BaseModel):
    """Base calendar schema with common fields."""
    name: str = Field(..., min_length=1, max_length=100, description="Calendar name")
    provider: str = Field(..., description="Calendar provider (google, outlook, caldav)")
    timezone: str = Field(default="UTC", description="Calendar timezone")
    color: Optional[str] = Field(None, description="Calendar color code")
    is_primary: bool = Field(default=False, description="Whether this is the primary calendar")


class CalendarCreate(CalendarBase):
    """Schema for creating a new calendar."""
    access_token: str = Field(..., description="OAuth access token")
    refresh_token: Optional[str] = Field(None, description="OAuth refresh token")
    external_id: str = Field(..., description="External calendar ID from provider")


class CalendarUpdate(BaseModel):
    """Schema for updating calendar information."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    timezone: Optional[str] = None
    color: Optional[str] = None
    is_primary: Optional[bool] = None
    is_active: Optional[bool] = None


class CalendarResponse(CalendarBase):
    """Schema for calendar response."""
    id: UUID
    user_id: UUID
    external_id: str
    is_active: bool
    last_synced: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class CalendarSyncRequest(BaseModel):
    """Schema for calendar sync request."""
    calendar_id: UUID = Field(..., description="Calendar ID to sync")
    force: bool = Field(default=False, description="Force full sync")


class CalendarSyncResponse(BaseModel):
    """Schema for calendar sync response."""
    calendar_id: UUID
    events_synced: int
    last_synced: datetime
    status: str = Field(..., description="Sync status (success, partial, failed)")
    errors: Optional[List[str]] = Field(None, description="List of errors if any")

# Made with Bob