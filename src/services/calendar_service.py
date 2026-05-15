"""
Calendar service for managing calendar operations and synchronization.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from src.models.calendar import Calendar
from src.models.calendar_event import CalendarEvent
from src.schemas.calendar import CalendarCreate, CalendarUpdate


class CalendarService:
    """Service for calendar operations."""
    
    @staticmethod
    def get_calendar_by_id(
        db: Session,
        calendar_id: UUID,
        user_id: UUID
    ) -> Optional[Calendar]:
        """
        Get calendar by ID for a specific user.
        
        Args:
            db: Database session
            calendar_id: Calendar ID
            user_id: User ID
            
        Returns:
            Calendar object or None if not found
        """
        return db.query(Calendar).filter(
            Calendar.id == calendar_id,
            Calendar.user_id == user_id
        ).first()
    
    @staticmethod
    def get_user_calendars(
        db: Session,
        user_id: UUID,
        provider: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[Calendar]:
        """
        Get all calendars for a user with optional filters.
        
        Args:
            db: Database session
            user_id: User ID
            provider: Optional provider filter
            is_active: Optional active status filter
            
        Returns:
            List of calendar objects
        """
        query = db.query(Calendar).filter(Calendar.user_id == user_id)
        
        if provider:
            query = query.filter(Calendar.provider == provider)
        
        if is_active is not None:
            query = query.filter(Calendar.is_active == is_active)
        
        return query.all()
    
    @staticmethod
    def create_calendar(
        db: Session,
        user_id: UUID,
        calendar_data: CalendarCreate
    ) -> Calendar:
        """
        Create a new calendar.
        
        Args:
            db: Database session
            user_id: User ID
            calendar_data: Calendar creation data
            
        Returns:
            Created calendar object
        """
        db_calendar = Calendar(
            user_id=user_id,
            name=calendar_data.name,
            provider=calendar_data.provider,
            external_id=calendar_data.external_id,
            timezone=calendar_data.timezone,
            color=calendar_data.color,
            is_primary=calendar_data.is_primary,
            access_token=calendar_data.access_token,
            refresh_token=calendar_data.refresh_token
        )
        
        db.add(db_calendar)
        db.commit()
        db.refresh(db_calendar)
        
        return db_calendar
    
    @staticmethod
    def update_calendar(
        db: Session,
        calendar: Calendar,
        calendar_data: CalendarUpdate
    ) -> Calendar:
        """
        Update calendar information.
        
        Args:
            db: Database session
            calendar: Calendar object to update
            calendar_data: Calendar update data
            
        Returns:
            Updated calendar object
        """
        update_data = calendar_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(calendar, field, value)
        
        db.commit()
        db.refresh(calendar)
        
        return calendar
    
    @staticmethod
    def delete_calendar(db: Session, calendar: Calendar) -> None:
        """
        Delete a calendar.
        
        Args:
            db: Database session
            calendar: Calendar object to delete
        """
        db.delete(calendar)
        db.commit()
    
    @staticmethod
    def update_sync_time(
        db: Session,
        calendar: Calendar
    ) -> Calendar:
        """
        Update calendar's last sync time.
        
        Args:
            db: Database session
            calendar: Calendar object
            
        Returns:
            Updated calendar object
        """
        calendar.last_synced = datetime.utcnow()
        db.commit()
        db.refresh(calendar)
        
        return calendar
    
    @staticmethod
    def get_calendar_events(
        db: Session,
        calendar_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[CalendarEvent]:
        """
        Get events for a calendar with optional date filters.
        
        Args:
            db: Database session
            calendar_id: Calendar ID
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            List of calendar event objects
        """
        query = db.query(CalendarEvent).filter(
            CalendarEvent.calendar_id == calendar_id
        )
        
        if start_date:
            query = query.filter(CalendarEvent.start_time >= start_date)
        
        if end_date:
            query = query.filter(CalendarEvent.end_time <= end_date)
        
        return query.order_by(CalendarEvent.start_time).all()
    
    @staticmethod
    def sync_calendar_events(
        db: Session,
        calendar: Calendar,
        events_data: List[dict]
    ) -> int:
        """
        Sync calendar events from external source.
        
        Args:
            db: Database session
            calendar: Calendar object
            events_data: List of event data from external calendar
            
        Returns:
            Number of events synced
        """
        synced_count = 0
        
        for event_data in events_data:
            # Check if event already exists
            existing_event = db.query(CalendarEvent).filter(
                CalendarEvent.calendar_id == calendar.id,
                CalendarEvent.external_id == event_data.get("external_id")
            ).first()
            
            if existing_event:
                # Update existing event
                for field, value in event_data.items():
                    if hasattr(existing_event, field):
                        setattr(existing_event, field, value)
            else:
                # Create new event
                new_event = CalendarEvent(
                    calendar_id=calendar.id,
                    **event_data
                )
                db.add(new_event)
            
            synced_count += 1
        
        db.commit()
        CalendarService.update_sync_time(db, calendar)
        
        return synced_count

# Made with Bob