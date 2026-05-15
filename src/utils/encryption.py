"""
Encryption and token utilities for secure data handling.
"""
from cryptography.fernet import Fernet
from typing import Optional
import base64
import secrets

from src.config import get_settings

settings = get_settings()


class EncryptionService:
    """Service for encrypting and decrypting sensitive data."""
    
    def __init__(self):
        """Initialize encryption service with secret key."""
        # Derive a Fernet key from the secret key
        secret = settings.secret_key.get_secret_value()
        # Ensure key is 32 bytes for Fernet
        key = base64.urlsafe_b64encode(secret.encode().ljust(32)[:32])
        self.cipher = Fernet(key)
    
    def encrypt(self, data: str) -> str:
        """
        Encrypt a string.
        
        Args:
            data: String to encrypt
            
        Returns:
            Encrypted string (base64 encoded)
        """
        encrypted = self.cipher.encrypt(data.encode())
        return encrypted.decode()
    
    def decrypt(self, encrypted_data: str) -> Optional[str]:
        """
        Decrypt an encrypted string.
        
        Args:
            encrypted_data: Encrypted string to decrypt
            
        Returns:
            Decrypted string or None if decryption fails
        """
        try:
            decrypted = self.cipher.decrypt(encrypted_data.encode())
            return decrypted.decode()
        except Exception:
            return None
    
    def encrypt_token(self, token: str) -> str:
        """
        Encrypt an OAuth token.
        
        Args:
            token: Token to encrypt
            
        Returns:
            Encrypted token
        """
        return self.encrypt(token)
    
    def decrypt_token(self, encrypted_token: str) -> Optional[str]:
        """
        Decrypt an OAuth token.
        
        Args:
            encrypted_token: Encrypted token
            
        Returns:
            Decrypted token or None if decryption fails
        """
        return self.decrypt(encrypted_token)


def generate_random_token(length: int = 32) -> str:
    """
    Generate a cryptographically secure random token.
    
    Args:
        length: Length of the token in bytes
        
    Returns:
        Random token as hex string
    """
    return secrets.token_hex(length)


def generate_reset_token() -> str:
    """
    Generate a password reset token.
    
    Returns:
        Reset token
    """
    return generate_random_token(32)


def generate_api_key() -> str:
    """
    Generate an API key.
    
    Returns:
        API key
    """
    return generate_random_token(32)


def mask_token(token: str, visible_chars: int = 4) -> str:
    """
    Mask a token for safe display.
    
    Args:
        token: Token to mask
        visible_chars: Number of characters to show at start and end
        
    Returns:
        Masked token (e.g., "abcd...wxyz")
    """
    if len(token) <= visible_chars * 2:
        return "*" * len(token)
    
    start = token[:visible_chars]
    end = token[-visible_chars:]
    return f"{start}...{end}"


def mask_email(email: str) -> str:
    """
    Mask an email address for safe display.
    
    Args:
        email: Email to mask
        
    Returns:
        Masked email (e.g., "j***@example.com")
    """
    if '@' not in email:
        return email
    
    local, domain = email.split('@', 1)
    
    if len(local) <= 2:
        masked_local = local[0] + '*'
    else:
        masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
    
    return f"{masked_local}@{domain}"


def generate_verification_code(length: int = 6) -> str:
    """
    Generate a numeric verification code.
    
    Args:
        length: Length of the code
        
    Returns:
        Numeric verification code
    """
    return ''.join(str(secrets.randbelow(10)) for _ in range(length))


# Create singleton instance
encryption_service = EncryptionService()

# Made with Bob