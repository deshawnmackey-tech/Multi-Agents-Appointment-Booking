"""
Tests for authentication service.
"""
from src.services.auth_service import AuthService


def test_password_hashing():
    """Test password hashing and verification."""
    password = "TestPassword123!"
    
    # Hash password
    hashed = AuthService.get_password_hash(password)
    
    # Verify correct password
    assert AuthService.verify_password(password, hashed) is True
    
    # Verify incorrect password
    assert AuthService.verify_password("WrongPassword", hashed) is False


def test_create_access_token():
    """Test JWT access token creation."""
    data = {"user_id": "123", "email": "test@example.com"}
    
    token = AuthService.create_access_token(data)
    
    assert isinstance(token, str)
    assert len(token) > 0


def test_decode_token():
    """Test JWT token decoding."""
    data = {"user_id": "123", "email": "test@example.com"}
    
    # Create token
    token = AuthService.create_access_token(data)
    
    # Decode token
    decoded = AuthService.decode_token(token)
    
    assert decoded is not None
    assert decoded["user_id"] == "123"
    assert decoded["email"] == "test@example.com"
    assert "exp" in decoded


def test_decode_invalid_token():
    """Test decoding invalid token."""
    invalid_token = "invalid.token.here"
    
    decoded = AuthService.decode_token(invalid_token)
    
    assert decoded is None


def test_create_refresh_token():
    """Test JWT refresh token creation."""
    data = {"user_id": "123"}
    
    token = AuthService.create_refresh_token(data)
    
    assert isinstance(token, str)
    assert len(token) > 0
    
    # Decode and verify it's a refresh token
    decoded = AuthService.decode_token(token)
    assert decoded is not None
    assert decoded.get("type") == "refresh"

# Made with Bob