"""
Input validation utilities.
"""
import re
from datetime import datetime, time
from typing import Optional
from uuid import UUID


def validate_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_timezone(timezone: str) -> bool:
    """
    Validate timezone string.
    
    Args:
        timezone: Timezone string to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        import pytz
        return timezone in pytz.all_timezones
    except Exception:
        return False


def validate_phone_number(phone: str) -> bool:
    """
    Validate phone number format (basic validation).
    
    Args:
        phone: Phone number to validate
        
    Returns:
        True if valid, False otherwise
    """
    # Remove common separators
    cleaned = re.sub(r'[\s\-\(\)\+]', '', phone)
    # Check if it's all digits and reasonable length
    return cleaned.isdigit() and 10 <= len(cleaned) <= 15


def validate_url(url: str) -> bool:
    """
    Validate URL format.
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return bool(re.match(pattern, url, re.IGNORECASE))


def validate_uuid(uuid_string: str) -> bool:
    """
    Validate UUID string format.
    
    Args:
        uuid_string: UUID string to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        UUID(uuid_string)
        return True
    except (ValueError, AttributeError):
        return False


def validate_time_range(
    start_time: datetime,
    end_time: datetime,
    min_duration_minutes: int = 1
) -> bool:
    """
    Validate that end time is after start time with minimum duration.
    
    Args:
        start_time: Start datetime
        end_time: End datetime
        min_duration_minutes: Minimum duration in minutes
        
    Returns:
        True if valid, False otherwise
    """
    if end_time <= start_time:
        return False
    
    duration = (end_time - start_time).total_seconds() / 60
    return duration >= min_duration_minutes


def validate_working_hours(start_time: time, end_time: time) -> bool:
    """
    Validate working hours (end must be after start).
    
    Args:
        start_time: Working hours start time
        end_time: Working hours end time
        
    Returns:
        True if valid, False otherwise
    """
    return end_time > start_time


def validate_day_of_week(day: int) -> bool:
    """
    Validate day of week (0-6, where 0 is Monday).
    
    Args:
        day: Day of week integer
        
    Returns:
        True if valid, False otherwise
    """
    return 0 <= day <= 6


def validate_password_strength(
    password: str,
    min_length: int = 8,
    require_uppercase: bool = True,
    require_lowercase: bool = True,
    require_digit: bool = True,
    require_special: bool = False
) -> tuple[bool, Optional[str]]:
    """
    Validate password strength.
    
    Args:
        password: Password to validate
        min_length: Minimum password length
        require_uppercase: Require at least one uppercase letter
        require_lowercase: Require at least one lowercase letter
        require_digit: Require at least one digit
        require_special: Require at least one special character
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < min_length:
        return False, f"Password must be at least {min_length} characters long"
    
    if require_uppercase and not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if require_lowercase and not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if require_digit and not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    if require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    return True, None


def validate_recurrence_rule(rule: str) -> bool:
    """
    Validate iCalendar recurrence rule format (basic validation).
    
    Args:
        rule: Recurrence rule string
        
    Returns:
        True if valid, False otherwise
    """
    if not rule.startswith('RRULE:'):
        return False
    
    # Check for required FREQ parameter
    if 'FREQ=' not in rule:
        return False
    
    # Valid frequencies
    valid_freqs = ['DAILY', 'WEEKLY', 'MONTHLY', 'YEARLY']
    freq_match = re.search(r'FREQ=(\w+)', rule)
    
    if not freq_match or freq_match.group(1) not in valid_freqs:
        return False
    
    return True


def sanitize_string(text: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize string input by removing potentially harmful characters.
    
    Args:
        text: Text to sanitize
        max_length: Optional maximum length
        
    Returns:
        Sanitized string
    """
    # Remove null bytes and control characters
    sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    # Trim whitespace
    sanitized = sanitized.strip()
    
    # Truncate if max_length specified
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized


def validate_calendar_provider(provider: str) -> bool:
    """
    Validate calendar provider name.
    
    Args:
        provider: Provider name
        
    Returns:
        True if valid, False otherwise
    """
    valid_providers = ['google', 'outlook', 'caldav', 'ios']
    return provider.lower() in valid_providers


def validate_appointment_status(status: str) -> bool:
    """
    Validate appointment status.
    
    Args:
        status: Status string
        
    Returns:
        True if valid, False otherwise
    """
    valid_statuses = ['confirmed', 'tentative', 'cancelled', 'pending']
    return status.lower() in valid_statuses

# Made with Bob