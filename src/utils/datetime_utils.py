"""
Date and time utility functions.
"""
from datetime import datetime, timedelta, time
from typing import List, Optional, Tuple
import pytz
from dateutil import parser


def parse_datetime(date_string: str, timezone: str = "UTC") -> datetime:
    """
    Parse a date string into a timezone-aware datetime object.
    
    Args:
        date_string: Date string to parse
        timezone: Timezone name (default: UTC)
        
    Returns:
        Timezone-aware datetime object
    """
    dt = parser.parse(date_string)
    
    if dt.tzinfo is None:
        # If no timezone info, assume the given timezone
        tz = pytz.timezone(timezone)
        dt = tz.localize(dt)
    
    return dt


def convert_timezone(dt: datetime, to_timezone: str) -> datetime:
    """
    Convert datetime to a different timezone.
    
    Args:
        dt: Datetime object to convert
        to_timezone: Target timezone name
        
    Returns:
        Datetime in target timezone
    """
    if dt.tzinfo is None:
        # Assume UTC if no timezone info
        dt = pytz.UTC.localize(dt)
    
    target_tz = pytz.timezone(to_timezone)
    return dt.astimezone(target_tz)


def get_current_time(timezone: str = "UTC") -> datetime:
    """
    Get current time in specified timezone.
    
    Args:
        timezone: Timezone name (default: UTC)
        
    Returns:
        Current datetime in specified timezone
    """
    tz = pytz.timezone(timezone)
    return datetime.now(tz)


def is_within_working_hours(
    dt: datetime,
    working_start: time,
    working_end: time,
    timezone: str = "UTC"
) -> bool:
    """
    Check if a datetime falls within working hours.
    
    Args:
        dt: Datetime to check
        working_start: Working hours start time
        working_end: Working hours end time
        timezone: Timezone for comparison
        
    Returns:
        True if within working hours, False otherwise
    """
    # Convert to target timezone
    dt_tz = convert_timezone(dt, timezone)
    dt_time = dt_tz.time()
    
    return working_start <= dt_time <= working_end


def get_time_slots(
    start_date: datetime,
    end_date: datetime,
    slot_duration: int,
    working_start: time,
    working_end: time,
    timezone: str = "UTC",
    working_days: Optional[List[int]] = None
) -> List[Tuple[datetime, datetime]]:
    """
    Generate time slots within a date range.
    
    Args:
        start_date: Start date
        end_date: End date
        slot_duration: Duration of each slot in minutes
        working_start: Working hours start time
        working_end: Working hours end time
        timezone: Timezone for slots
        working_days: List of working days (0=Monday, 6=Sunday), None for all days
        
    Returns:
        List of (start, end) datetime tuples for each slot
    """
    if working_days is None:
        working_days = [0, 1, 2, 3, 4]  # Monday to Friday
    
    slots = []
    current_date = start_date.date()
    end = end_date.date()
    
    tz = pytz.timezone(timezone)
    
    while current_date <= end:
        # Check if it's a working day
        if current_date.weekday() in working_days:
            # Create datetime for working start
            slot_start = tz.localize(
                datetime.combine(current_date, working_start)
            )
            day_end = tz.localize(
                datetime.combine(current_date, working_end)
            )
            
            # Generate slots for this day
            while slot_start < day_end:
                slot_end = slot_start + timedelta(minutes=slot_duration)
                
                if slot_end <= day_end:
                    # Only add if slot is within date range
                    if slot_start >= start_date and slot_end <= end_date:
                        slots.append((slot_start, slot_end))
                
                slot_start = slot_end
        
        current_date += timedelta(days=1)
    
    return slots


def format_duration(minutes: int) -> str:
    """
    Format duration in minutes to human-readable string.
    
    Args:
        minutes: Duration in minutes
        
    Returns:
        Formatted duration string (e.g., "1h 30m")
    """
    hours = minutes // 60
    mins = minutes % 60
    
    if hours > 0 and mins > 0:
        return f"{hours}h {mins}m"
    elif hours > 0:
        return f"{hours}h"
    else:
        return f"{mins}m"


def get_date_range_days(start_date: datetime, end_date: datetime) -> int:
    """
    Calculate number of days between two dates.
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        Number of days
    """
    delta = end_date.date() - start_date.date()
    return delta.days


def round_to_nearest_slot(
    dt: datetime,
    slot_duration: int = 15
) -> datetime:
    """
    Round datetime to nearest time slot.
    
    Args:
        dt: Datetime to round
        slot_duration: Slot duration in minutes (default: 15)
        
    Returns:
        Rounded datetime
    """
    # Round to nearest slot
    minutes = (dt.minute // slot_duration) * slot_duration
    return dt.replace(minute=minutes, second=0, microsecond=0)


def is_business_day(dt: datetime, timezone: str = "UTC") -> bool:
    """
    Check if a date is a business day (Monday-Friday).
    
    Args:
        dt: Datetime to check
        timezone: Timezone for date calculation
        
    Returns:
        True if business day, False otherwise
    """
    dt_tz = convert_timezone(dt, timezone)
    return dt_tz.weekday() < 5  # 0-4 are Monday-Friday


def add_business_days(dt: datetime, days: int, timezone: str = "UTC") -> datetime:
    """
    Add business days to a datetime.
    
    Args:
        dt: Starting datetime
        days: Number of business days to add
        timezone: Timezone for calculation
        
    Returns:
        Datetime after adding business days
    """
    dt_tz = convert_timezone(dt, timezone)
    current = dt_tz
    
    while days > 0:
        current += timedelta(days=1)
        if is_business_day(current, timezone):
            days -= 1
    
    return current

# Made with Bob