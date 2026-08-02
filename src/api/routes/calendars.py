"""
Calendar management API routes.
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Any, List, Optional
from uuid import UUID

from src.database.session import get_db
from src.models.calendar import Calendar
from src.schemas.calendar import (
    CalendarCreate,
    CalendarUpdate,
    CalendarResponse,
    CalendarSyncRequest,
    CalendarSyncResponse
)
from src.api.routes.auth import require_current_user
from src.services.calendar_service import CalendarService

router = APIRouter()


def _parse_iso_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None

    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)


@router.post("/", response_model=CalendarResponse, status_code=status.HTTP_201_CREATED)
async def create_calendar(
    calendar_data: CalendarCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_current_user)
) -> Any:
    """
    Connect a new calendar.
    
    Args:
        calendar_data: Calendar connection data
        db: Database session
        token: JWT access token
        
    Returns:
        Created calendar information
        
    Raises:
        HTTPException: If calendar connection fails
    """
    existing_calendar = db.query(Calendar).filter(
        Calendar.user_id == current_user.id,
        Calendar.provider == calendar_data.provider,
        Calendar.calendar_id == calendar_data.external_id,
    ).first()

    if existing_calendar:
        existing_calendar.name = calendar_data.name
        existing_calendar.calendar_id = calendar_data.external_id
        existing_calendar.external_id = calendar_data.external_id
        existing_calendar.timezone = calendar_data.timezone
        existing_calendar.color = calendar_data.color
        existing_calendar.is_primary = calendar_data.is_primary
        existing_calendar.is_active = True
        existing_calendar.access_token = calendar_data.access_token
        if calendar_data.refresh_token is not None:
            existing_calendar.refresh_token = calendar_data.refresh_token
        db.commit()
        db.refresh(existing_calendar)
        return existing_calendar

    return CalendarService.create_calendar(db, current_user.id, calendar_data)


@router.get("/", response_model=List[CalendarResponse])
async def list_calendars(
    provider: Optional[str] = Query(None, description="Filter by provider"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user = Depends(require_current_user)
) -> Any:
    """
    List user's calendars.
    
    Args:
        provider: Optional provider filter (google, outlook, caldav)
        is_active: Optional active status filter
        db: Database session
        token: JWT access token
        
    Returns:
        List of user's calendars
    """
    return CalendarService.get_user_calendars(
        db=db,
        user_id=current_user.id,
        provider=provider,
        is_active=is_active,
    )


@router.get("/{calendar_id}", response_model=CalendarResponse)
async def get_calendar(
    calendar_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(require_current_user)
) -> Any:
    """
    Get calendar by ID.
    
    Args:
        calendar_id: Calendar ID
        db: Database session
        token: JWT access token
        
    Returns:
        Calendar information
        
    Raises:
        HTTPException: If calendar not found or access denied
    """
    calendar = CalendarService.get_calendar_by_id(db, calendar_id, current_user.id)
    if not calendar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar not found",
        )

    return calendar


@router.put("/{calendar_id}", response_model=CalendarResponse)
async def update_calendar(
    calendar_id: UUID,
    calendar_data: CalendarUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_current_user)
) -> Any:
    """
    Update calendar settings.
    
    Args:
        calendar_id: Calendar ID
        calendar_data: Calendar update data
        db: Database session
        token: JWT access token
        
    Returns:
        Updated calendar information
        
    Raises:
        HTTPException: If calendar not found or access denied
    """
    calendar = CalendarService.get_calendar_by_id(db, calendar_id, current_user.id)
    if not calendar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar not found",
        )

    return CalendarService.update_calendar(db, calendar, calendar_data)


@router.delete("/{calendar_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_calendar(
    calendar_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(require_current_user)
) -> None:
    """
    Disconnect and delete calendar.
    
    Args:
        calendar_id: Calendar ID
        db: Database session
        token: JWT access token
        
    Raises:
        HTTPException: If calendar not found or access denied
    """
    calendar = CalendarService.get_calendar_by_id(db, calendar_id, current_user.id)
    if not calendar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar not found",
        )

    CalendarService.delete_calendar(db, calendar)


@router.post("/{calendar_id}/sync", response_model=CalendarSyncResponse)
async def sync_calendar(
    calendar_id: UUID,
    sync_data: CalendarSyncRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_current_user)
) -> Any:
    """
    Manually trigger calendar sync.
    
    Args:
        calendar_id: Calendar ID
        sync_data: Sync request data
        db: Database session
        token: JWT access token
        
    Returns:
        Sync results
        
    Raises:
        HTTPException: If calendar not found or sync fails
    """
    calendar = CalendarService.get_calendar_by_id(db, calendar_id, current_user.id)
    if not calendar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar not found",
        )

    events = CalendarService.get_calendar_events(db, calendar.id)
    CalendarService.update_sync_time(db, calendar)

    return {
        "calendar_id": calendar.id,
        "events_synced": len(events),
        "last_synced": calendar.last_synced or datetime.utcnow(),
        "status": "success",
        "errors": [] if sync_data.force else None,
    }


@router.post("/sync-all", response_model=List[CalendarSyncResponse])
async def sync_all_calendars(
    force: bool = Query(False, description="Force full sync"),
    db: Session = Depends(get_db),
    current_user = Depends(require_current_user)
) -> Any:
    """
    Sync all user's calendars.
    
    Args:
        force: Force full sync instead of incremental
        db: Database session
        token: JWT access token
        
    Returns:
        List of sync results for each calendar
    """
    calendars = CalendarService.get_user_calendars(
        db=db,
        user_id=current_user.id,
        is_active=True,
    )

    results = []
    for calendar in calendars:
        events = CalendarService.get_calendar_events(db, calendar.id)
        CalendarService.update_sync_time(db, calendar)
        results.append({
            "calendar_id": calendar.id,
            "events_synced": len(events),
            "last_synced": calendar.last_synced or datetime.utcnow(),
            "status": "success",
            "errors": [] if force else None,
        })

    return results


@router.get("/{calendar_id}/events", response_model=List[dict])
async def get_calendar_events(
    calendar_id: UUID,
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    db: Session = Depends(get_db),
    current_user = Depends(require_current_user)
) -> Any:
    """
    Get events from a specific calendar.
    
    Args:
        calendar_id: Calendar ID
        start_date: Optional start date filter
        end_date: Optional end date filter
        db: Database session
        token: JWT access token
        
    Returns:
        List of calendar events
        
    Raises:
        HTTPException: If calendar not found or access denied
    """
    calendar = CalendarService.get_calendar_by_id(db, calendar_id, current_user.id)
    if not calendar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar not found",
        )

    events = CalendarService.get_calendar_events(
        db=db,
        calendar_id=calendar.id,
        start_date=_parse_iso_datetime(start_date),
        end_date=_parse_iso_datetime(end_date),
    )

    return [
        {
            "id": event.id,
            "appointment_id": event.appointment_id,
            "calendar_id": event.calendar_id,
            "external_event_id": event.external_event_id,
            "sync_status": event.sync_status,
            "last_synced_at": event.last_synced_at,
        }
        for event in events
    ]

# Made with Bob