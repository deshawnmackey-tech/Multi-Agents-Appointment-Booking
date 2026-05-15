"""
Tests for validation utilities.
"""
from src.utils.validators import (
    validate_email,
    validate_timezone,
    validate_phone_number,
    validate_url,
    validate_uuid,
    validate_password_strength,
    validate_calendar_provider,
    validate_appointment_status
)


def test_validate_email():
    """Test email validation."""
    assert validate_email("test@example.com") is True
    assert validate_email("user.name+tag@example.co.uk") is True
    assert validate_email("invalid.email") is False
    assert validate_email("@example.com") is False
    assert validate_email("test@") is False


def test_validate_timezone():
    """Test timezone validation."""
    assert validate_timezone("UTC") is True
    assert validate_timezone("America/New_York") is True
    assert validate_timezone("Europe/London") is True
    assert validate_timezone("Invalid/Timezone") is False


def test_validate_phone_number():
    """Test phone number validation."""
    assert validate_phone_number("+1234567890") is True
    assert validate_phone_number("123-456-7890") is True
    assert validate_phone_number("(123) 456-7890") is True
    assert validate_phone_number("12345") is False  # Too short
    assert validate_phone_number("abc123") is False  # Contains letters


def test_validate_url():
    """Test URL validation."""
    assert validate_url("https://example.com") is True
    assert validate_url("http://example.com/path") is True
    assert validate_url("https://sub.example.com:8080/path?query=1") is True
    assert validate_url("not-a-url") is False
    assert validate_url("ftp://example.com") is False


def test_validate_uuid():
    """Test UUID validation."""
    assert validate_uuid("550e8400-e29b-41d4-a716-446655440000") is True
    assert validate_uuid("invalid-uuid") is False
    assert validate_uuid("12345") is False


def test_validate_password_strength():
    """Test password strength validation."""
    # Valid password
    is_valid, error = validate_password_strength("Password123")
    assert is_valid is True
    assert error is None
    
    # Too short
    is_valid, error = validate_password_strength("Pass1")
    assert is_valid is False
    assert "at least 8 characters" in error
    
    # No uppercase
    is_valid, error = validate_password_strength("password123")
    assert is_valid is False
    assert "uppercase" in error
    
    # No lowercase
    is_valid, error = validate_password_strength("PASSWORD123")
    assert is_valid is False
    assert "lowercase" in error
    
    # No digit
    is_valid, error = validate_password_strength("Password")
    assert is_valid is False
    assert "digit" in error


def test_validate_calendar_provider():
    """Test calendar provider validation."""
    assert validate_calendar_provider("google") is True
    assert validate_calendar_provider("outlook") is True
    assert validate_calendar_provider("caldav") is True
    assert validate_calendar_provider("invalid") is False


def test_validate_appointment_status():
    """Test appointment status validation."""
    assert validate_appointment_status("confirmed") is True
    assert validate_appointment_status("tentative") is True
    assert validate_appointment_status("cancelled") is True
    assert validate_appointment_status("pending") is True
    assert validate_appointment_status("invalid") is False

# Made with Bob