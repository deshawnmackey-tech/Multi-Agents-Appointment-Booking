"""
Appointment service for managing appointment operations.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from src.models.appointment import Appointment
from src.models.participant import Participant
from src.schemas.appointment import AppointmentCreate, AppointmentUpdate


class AppointmentService:
    """Service for appointment operations."""
    
    @staticmethod
    def get_appointment_by_id(
        db: Session,
        appointment_id: UUID,
        user_id: UUID
    ) -> Optional[Appointment]:
        """
        Get appointment by ID for a specific user.
        
        Args:
            db: Database session
            appointment_id: Appointment ID
            user_id: User ID
            
        Returns:
            Appointment object or None if not found
        """
        return db.query(Appointment).filter(
            Appointment.id == appointment_id,
            Appointment.user_id == user_id
        ).first()
    
    @staticmethod
    def get_user_appointments(
        db: Session,
        user_id: UUID,
        calendar_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Appointment]:
        """
        Get appointments for a user with optional filters.
        
        Args:
            db: Database session
            user_id: User ID
            calendar_id: Optional calendar ID filter
            start_date: Optional start date filter
            end_date: Optional end date filter
            status: Optional status filter
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of appointment objects
        """
        query = db.query(Appointment).filter(Appointment.user_id == user_id)
        
        if calendar_id:
            query = query.filter(Appointment.calendar_id == calendar_id)
        
        if start_date:
            query = query.filter(Appointment.start_time >= start_date)
        
        if end_date:
            query = query.filter(Appointment.end_time <= end_date)
        
        if status:
            query = query.filter(Appointment.status == status)
        
        return query.order_by(Appointment.start_time).offset(skip).limit(limit).all()
    
    @staticmethod
    def create_appointment(
        db: Session,
        user_id: UUID,
        appointment_data: AppointmentCreate
    ) -> Appointment:
        """
        Create a new appointment.
        
        Args:
            db: Database session
            user_id: User ID
            appointment_data: Appointment creation data
            
        Returns:
            Created appointment object
        """
        # Create appointment
        db_appointment = Appointment(
            user_id=user_id,
            calendar_id=appointment_data.calendar_id,
            title=appointment_data.title,
            description=appointment_data.description,
            location=appointment_data.location,
            start_time=appointment_data.start_time,
            end_time=appointment_data.end_time,
            timezone=appointment_data.timezone,
            is_all_day=appointment_data.is_all_day,
            recurrence_rule=appointment_data.recurrence_rule,
            status="confirmed"
        )
        
        db.add(db_appointment)
        db.flush()  # Flush to get the appointment ID
        
        # Add participants if provided
        if appointment_data.participants:
            for participant_data in appointment_data.participants:
                db_participant = Participant(
                    appointment_id=db_appointment.id,
                    email=participant_data.email,
                    name=participant_data.name,
                    is_organizer=participant_data.is_organizer,
                    response_status=participant_data.response_status
                )
                db.add(db_participant)
        
        db.commit()
        db.refresh(db_appointment)
        
        return db_appointment
    
    @staticmethod
    def update_appointment(
        db: Session,
        appointment: Appointment,
        appointment_data: AppointmentUpdate
    ) -> Appointment:
        """
        Update appointment information.
        
        Args:
            db: Database session
            appointment: Appointment object to update
            appointment_data: Appointment update data
            
        Returns:
            Updated appointment object
        """
        update_data = appointment_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            if hasattr(appointment, field):
                setattr(appointment, field, value)
        
        db.commit()
        db.refresh(appointment)
        
        return appointment
    
    @staticmethod
    def delete_appointment(db: Session, appointment: Appointment) -> None:
        """
        Delete an appointment.
        
        Args:
            db: Database session
            appointment: Appointment object to delete
        """
        db.delete(appointment)
        db.commit()
    
    @staticmethod
    def check_conflicts(
        db: Session,
        user_id: UUID,
        start_time: datetime,
        end_time: datetime,
        calendar_ids: Optional[List[UUID]] = None,
        exclude_appointment_id: Optional[UUID] = None
    ) -> List[Appointment]:
        """
        Check for appointment conflicts in a time range.
        
        Args:
            db: Database session
            user_id: User ID
            start_time: Start time to check
            end_time: End time to check
            calendar_ids: Optional list of calendar IDs to check
            exclude_appointment_id: Optional appointment ID to exclude from check
            
        Returns:
            List of conflicting appointments
        """
        query = db.query(Appointment).filter(
            Appointment.user_id == user_id,
            Appointment.status != "cancelled",
            or_(
                and_(
                    Appointment.start_time <= start_time,
                    Appointment.end_time > start_time
                ),
                and_(
                    Appointment.start_time < end_time,
                    Appointment.end_time >= end_time
                ),
                and_(
                    Appointment.start_time >= start_time,
                    Appointment.end_time <= end_time
                )
            )
        )
        
        if calendar_ids:
            query = query.filter(Appointment.calendar_id.in_(calendar_ids))
        
        if exclude_appointment_id:
            query = query.filter(Appointment.id != exclude_appointment_id)
        
        return query.all()
    
    @staticmethod
    def search_appointments(
        db: Session,
        user_id: UUID,
        query_text: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        calendar_ids: Optional[List[UUID]] = None,
        status: Optional[str] = None
    ) -> List[Appointment]:
        """
        Search appointments with advanced filters.
        
        Args:
            db: Database session
            user_id: User ID
            query_text: Optional text search in title/description
            start_date: Optional start date filter
            end_date: Optional end date filter
            calendar_ids: Optional calendar IDs filter
            status: Optional status filter
            
        Returns:
            List of matching appointments
        """
        query = db.query(Appointment).filter(Appointment.user_id == user_id)
        
        if query_text:
            search_filter = or_(
                Appointment.title.ilike(f"%{query_text}%"),
                Appointment.description.ilike(f"%{query_text}%")
            )
            query = query.filter(search_filter)
        
        if start_date:
            query = query.filter(Appointment.start_time >= start_date)
        
        if end_date:
            query = query.filter(Appointment.end_time <= end_date)
        
        if calendar_ids:
            query = query.filter(Appointment.calendar_id.in_(calendar_ids))
        
        if status:
            query = query.filter(Appointment.status == status)
        
        return query.order_by(Appointment.start_time).all()

# Made with Bob