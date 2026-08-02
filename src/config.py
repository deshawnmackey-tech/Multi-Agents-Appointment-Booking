"""
Configuration management for the Multi-Agent Appointment Booking System.

This module provides centralized configuration management using pydantic-settings
for type-safe environment variable handling with validation and documentation.

Features:
    - Type-safe configuration with Pydantic validation
    - Environment-specific settings (development, staging, production)
    - Cached settings instance for performance
    - Comprehensive validation and error handling
    - Helper properties for common configuration checks

Example:
    >>> from src.config import get_settings
    >>> settings = get_settings()
    >>> if settings.is_production:
    ...     print(f"Running in production mode")
"""
from enum import Enum
from functools import lru_cache
import os
from typing import Literal, Optional

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    """Valid application environment types."""
    
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    All settings are loaded from environment variables or .env file.
    Sensitive values (API keys, secrets) are stored as SecretStr for security.
    
    Attributes:
        app_name: Application name identifier
        app_env: Current environment (development, staging, production)
        debug: Enable debug mode (auto-disabled in production)
        secret_key: Application secret key for cryptographic operations
        
    Raises:
        ValidationError: If required settings are missing or invalid
    """
    
    # ============================================================================
    # Application Configuration
    # ============================================================================
    app_name: str = Field(
        default="Multi-Agents-Appointment-Booking",
        description="Application name identifier"
    )
    app_env: Environment = Field(
        default=Environment.DEVELOPMENT,
        description="Current application environment"
    )
    debug: bool = Field(
        default=True,
        description="Enable debug mode (auto-disabled in production)"
    )
    secret_key: SecretStr = Field(
        default="",
        description="Application secret key for cryptographic operations"
    )
    
    # ============================================================================
    # Database Configuration
    # ============================================================================
    database_url: SecretStr = Field(
        default="",
        description="PostgreSQL database connection URL"
    )
    database_pool_size: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Database connection pool size"
    )
    database_pool_max_overflow: int = Field(
        default=10,
        ge=0,
        le=50,
        description="Maximum overflow connections beyond pool_size"
    )
    database_pool_timeout: int = Field(
        default=30,
        ge=1,
        le=300,
        description="Timeout in seconds for getting connection from pool"
    )
    database_pool_recycle: int = Field(
        default=3600,
        ge=300,
        le=7200,
        description="Recycle connections after N seconds to prevent stale connections"
    )
    database_echo_pool: bool = Field(
        default=False,
        description="Log connection pool checkouts/checkins for debugging"
    )
    
    # ============================================================================
    # Redis Configuration
    # ============================================================================
    redis_url: SecretStr = Field(
        default="",
        description="Redis connection URL for caching and task queue"
    )
    redis_max_connections: int = Field(
        default=50,
        ge=1,
        le=200,
        description="Maximum Redis connection pool size"
    )
    
    # ============================================================================
    # OpenAI Configuration
    # ============================================================================
    openai_api_key: SecretStr = Field(
        default="",
        description="OpenAI API key for AI agent functionality"
    )
    openai_model: str = Field(
        default="gpt-4-turbo-preview",
        description="OpenAI model to use for completions"
    )
    openai_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Temperature for OpenAI completions (0.0-2.0)"
    )
    openai_max_tokens: int = Field(
        default=2000,
        ge=1,
        le=8000,
        description="Maximum tokens for OpenAI completions"
    )
    
    # ============================================================================
    # Google Calendar Integration
    # ============================================================================
    google_client_id: str = Field(
        default="",
        description="Google OAuth2 client ID"
    )
    google_client_secret: SecretStr = Field(
        default="",
        description="Google OAuth2 client secret"
    )
    google_redirect_uri: str = Field(
        default="",
        description="Google OAuth2 redirect URI"
    )
    
    # ============================================================================
    # Microsoft Graph (Outlook) Integration
    # ============================================================================
    microsoft_client_id: str = Field(
        default="",
        description="Microsoft OAuth2 client ID"
    )
    microsoft_client_secret: SecretStr = Field(
        default="",
        description="Microsoft OAuth2 client secret"
    )
    microsoft_redirect_uri: str = Field(
        default="",
        description="Microsoft OAuth2 redirect URI"
    )
    microsoft_tenant_id: str = Field(
        default="",
        description="Microsoft Entra Directory tenant ID",
    )

    # ============================================================================
    # CalDAV (iOS/Apple Calendar) Integration
    # ============================================================================
    caldav_url: str = Field(
        default="",
        description="CalDAV server URL"
    )
    caldav_username: str = Field(
        default="",
        description="CalDAV username"
    )
    caldav_password: SecretStr = Field(
        default="",
        description="CalDAV password or app-specific password"
    )
    caldav_calendar_name: str = Field(
        default="",
        description="Name of the default CalDAV calendar to use (defaults to the first available)"
    )
    
    # ============================================================================
    # SendGrid (Email) Configuration
    # ============================================================================
    sendgrid_api_key: SecretStr = Field(
        default="",
        description="SendGrid API key for email notifications"
    )
    sendgrid_from_email: str = Field(
        default="",
        description="Default sender email address"
    )
    
    # ============================================================================
    # Twilio (SMS) Configuration
    # ============================================================================
    twilio_account_sid: str = Field(
        default="",
        description="Twilio account SID"
    )
    twilio_auth_token: SecretStr = Field(
        default="",
        description="Twilio authentication token"
    )
    twilio_phone_number: str = Field(
        default="",
        description="Twilio phone number for SMS notifications"
    )
    
    # ============================================================================
    # JWT Authentication Configuration
    # ============================================================================
    jwt_secret_key: SecretStr = Field(
        default="",
        description="Secret key for JWT token signing"
    )
    jwt_algorithm: str = Field(
        default="HS256",
        description="Algorithm for JWT token signing"
    )
    jwt_expiration_minutes: int = Field(
        default=30,
        ge=1,
        le=10080,  # Max 1 week
        description="JWT token expiration time in minutes"
    )
    jwt_refresh_expiration_days: int = Field(
        default=7,
        ge=1,
        le=90,
        description="JWT refresh token expiration time in days"
    )
    
    # ============================================================================
    # Celery Configuration
    # ============================================================================
    celery_broker_url: SecretStr = Field(
        default="",
        description="Celery message broker URL (typically Redis)"
    )
    celery_result_backend: SecretStr = Field(
        default="",
        description="Celery result backend URL"
    )
    celery_task_time_limit: int = Field(
        default=300,
        ge=1,
        le=3600,
        description="Hard time limit for Celery tasks in seconds"
    )
    celery_task_soft_time_limit: int = Field(
        default=240,
        ge=1,
        le=3600,
        description="Soft time limit for Celery tasks in seconds"
    )
    
    # ============================================================================
    # API Configuration
    # ============================================================================
    api_rate_limit: int = Field(
        default=100,
        ge=1,
        le=10000,
        description="API rate limit per minute per user"
    )
    api_timeout: int = Field(
        default=30,
        ge=1,
        le=300,
        description="API request timeout in seconds"
    )
    
    # ============================================================================
    # Logging Configuration
    # ============================================================================
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    log_format: str = Field(
        default="json",
        description="Log format (json or text)"
    )
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        validate_default=True,
    )
    
    # ============================================================================
    # Validators
    # ============================================================================
    
    @field_validator("app_env", mode="before")
    @classmethod
    def validate_environment(cls, v: str) -> Environment:
        """Validate and normalize environment value."""
        if isinstance(v, Environment):
            return v
        try:
            return Environment(v.lower())
        except ValueError:
            raise ValueError(
                f"Invalid environment: {v}. Must be one of: "
                f"{', '.join(e.value for e in Environment)}"
            )
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(
                f"Invalid log level: {v}. Must be one of: {', '.join(valid_levels)}"
            )
        return v_upper
    
    @field_validator("log_format")
    @classmethod
    def validate_log_format(cls, v: str) -> str:
        """Validate log format."""
        valid_formats = {"json", "text"}
        v_lower = v.lower()
        if v_lower not in valid_formats:
            raise ValueError(
                f"Invalid log format: {v}. Must be one of: {', '.join(valid_formats)}"
            )
        return v_lower
    
    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        """Validate critical settings for production environment."""
        if self.is_production:
            # Force debug off in production
            self.debug = False
            
            # Validate critical secrets are set
            critical_secrets = {
                "secret_key": self.secret_key,
                "database_url": self.database_url,
                "jwt_secret_key": self.jwt_secret_key,
            }
            
            missing_secrets = [
                name for name, value in critical_secrets.items()
                if not value or value.get_secret_value() == ""
            ]
            
            if missing_secrets:
                raise ValueError(
                    f"Production environment requires the following settings: "
                    f"{', '.join(missing_secrets)}"
                )
        
        return self
    
    @model_validator(mode="after")
    def validate_celery_time_limits(self) -> "Settings":
        """Ensure soft time limit is less than hard time limit."""
        if self.celery_task_soft_time_limit >= self.celery_task_time_limit:
            raise ValueError(
                "celery_task_soft_time_limit must be less than celery_task_time_limit"
            )
        return self
    
    # ============================================================================
    # Environment Helper Properties
    # ============================================================================
    
    @property
    def is_development(self) -> bool:
        """
        Check if running in development environment.
        
        Returns:
            True if environment is development, False otherwise
        """
        return self.app_env == Environment.DEVELOPMENT
    
    @property
    def is_production(self) -> bool:
        """
        Check if running in production environment.
        
        Returns:
            True if environment is production, False otherwise
        """
        return self.app_env == Environment.PRODUCTION
    
    @property
    def is_staging(self) -> bool:
        """
        Check if running in staging environment.
        
        Returns:
            True if environment is staging, False otherwise
        """
        return self.app_env == Environment.STAGING
    
    @property
    def is_testing(self) -> bool:
        """
        Check if running in test mode.
        
        Detects test execution via pytest's PYTEST_CURRENT_TEST environment
        variable (set automatically for the duration of each test), an
        explicit TEST_DATABASE_URL override, or a configured database URL
        that contains 'test'.
        
        Returns:
            True if running under pytest or targeting a test database
        """
        if os.getenv("PYTEST_CURRENT_TEST") or os.getenv("TEST_DATABASE_URL"):
            return True
        
        db_url = self.database_url.get_secret_value() if self.database_url else ""
        return "test" in db_url.lower()
    
    # ============================================================================
    # Configuration Helper Properties
    # ============================================================================
    
    @property
    def has_google_calendar(self) -> bool:
        """Check if Google Calendar integration is configured."""
        return bool(
            self.google_client_id
            and self.google_client_secret
            and self.google_client_secret.get_secret_value()
        )
    
    @property
    def has_microsoft_calendar(self) -> bool:
        """Check if Microsoft Calendar integration is configured."""
        return bool(
            self.microsoft_client_id
            and self.microsoft_client_secret.get_secret_value()
            and self.microsoft_tenant_id
            and self.microsoft_redirect_uri
        )
    
    @property
    def has_caldav_calendar(self) -> bool:
        """Check if CalDAV integration is configured."""
        return bool(
            self.caldav_url
            and self.caldav_username
            and self.caldav_password
            and self.caldav_password.get_secret_value()
        )
    
    @property
    def has_email_notifications(self) -> bool:
        """Check if email notifications are configured."""
        return bool(
            self.sendgrid_api_key
            and self.sendgrid_api_key.get_secret_value()
            and self.sendgrid_from_email
        )
    
    @property
    def has_sms_notifications(self) -> bool:
        """Check if SMS notifications are configured."""
        return bool(
            self.twilio_account_sid
            and self.twilio_auth_token.get_secret_value()
            and self.twilio_phone_number
        )
    
    @property
    def has_openai(self) -> bool:
        """Check if OpenAI integration is configured."""
        return bool(
            self.openai_api_key
            and self.openai_api_key.get_secret_value()
        )
    
    @property
    def database_url_safe(self) -> str:
        """
        Get database URL with password masked for logging.
        
        Returns:
            Database URL with password replaced by asterisks
        """
        if not self.database_url:
            return ""
        
        url = self.database_url.get_secret_value()
        # Mask password in URL for safe logging
        if "@" in url and "://" in url:
            protocol, rest = url.split("://", 1)
            if "@" in rest:
                credentials, host = rest.split("@", 1)
                if ":" in credentials:
                    username, _ = credentials.split(":", 1)
                    return f"{protocol}://{username}:****@{host}"
        return url
    
    def get_database_config(self) -> dict:
        """
        Get database configuration dictionary for SQLAlchemy.
        
        Production requires an explicit DATABASE_URL (enforced by
        validate_production_settings). When no DATABASE_URL is configured
        outside of production, this falls back to a local SQLite database:
        a dedicated file when running under pytest/test mode, or a
        separate file for interactive development.
        
        Returns:
            Dictionary with database connection parameters
        """
        url = self.database_url.get_secret_value() if self.database_url else ""
        if not url:
            url = "sqlite:///./test.db" if self.is_testing else "sqlite:///./app.db"

        is_sqlite = url.startswith("sqlite")

        return {
            "url": url,
            "pool_size": self.database_pool_size,
            "max_overflow": self.database_pool_max_overflow,
            "pool_timeout": self.database_pool_timeout,
            "pool_recycle": self.database_pool_recycle,  # Recycle stale connections
            "pool_pre_ping": True,  # Verify connections before using
            "echo": self.debug and self.is_development,  # Log SQL in dev debug mode
            "echo_pool": self.database_echo_pool,  # Log pool checkouts/checkins
            # SQLite connections are single-threaded by default; disable that
            # check so the same connection can be shared across FastAPI's
            # request-handling threads (e.g. under TestClient).
            "connect_args": {"check_same_thread": False} if is_sqlite else {},
        }
    
    def get_redis_config(self) -> dict:
        """
        Get Redis configuration dictionary.
        
        Returns:
            Dictionary with Redis connection parameters
        """
        return {
            "url": self.redis_url.get_secret_value() if self.redis_url else "",
            "max_connections": self.redis_max_connections,
            "decode_responses": True,
        }
    
    def get_celery_config(self) -> dict:
        """
        Get Celery configuration dictionary.
        
        Returns:
            Dictionary with Celery configuration parameters
        """
        return {
            "broker_url": self.celery_broker_url.get_secret_value() if self.celery_broker_url else "",
            "result_backend": self.celery_result_backend.get_secret_value() if self.celery_result_backend else "",
            "task_time_limit": self.celery_task_time_limit,
            "task_soft_time_limit": self.celery_task_soft_time_limit,
            "task_serializer": "json",
            "result_serializer": "json",
            "accept_content": ["json"],
            "timezone": "UTC",
            "enable_utc": True,
        }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Uses lru_cache to ensure settings are loaded and validated only once,
    improving performance and ensuring consistency across the application.
    
    Returns:
        Validated Settings instance
        
    Raises:
        ValidationError: If settings validation fails
        
    Example:
        >>> settings = get_settings()
        >>> print(settings.app_name)
        'Multi-Agents-Appointment-Booking'
    """
    return Settings()


def reload_settings() -> Settings:
    """
    Force reload settings by clearing cache.
    
    Useful for testing or when environment variables change at runtime.
    
    Returns:
        Fresh Settings instance
        
    Example:
        >>> settings = reload_settings()
    """
    get_settings.cache_clear()
    return get_settings()


# Export commonly used items
__all__ = [
    "Settings",
    "Environment",
    "get_settings",
    "reload_settings",
]
