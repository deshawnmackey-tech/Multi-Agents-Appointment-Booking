"""
Configuration management for the Multi-Agent Appointment Booking System.
Uses pydantic-settings for environment variable management.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application Configuration
    app_name: str = "Multi-Agents-Appointment-Booking"
    app_env: str = "development"  # Options: development, staging, production
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.app_env.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.app_env.lower() == "production"
    
    @property
    def is_staging(self) -> bool:
        """Check if running in staging environment."""
        return self.app_env.lower() == "staging"
    debug: bool = True
    secret_key: str = ""
    
    # Database
    database_url: str = ""
    database_pool_size: int = 20
    
    # Redis
    redis_url: str = ""
    
    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4-turbo-preview"
    
    # Google Calendar
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = ""
    
    # Microsoft Graph (Outlook)
    microsoft_client_id: str = ""
    microsoft_client_secret: str = ""
    microsoft_redirect_uri: str = ""
    
    # SendGrid (Email)
    sendgrid_api_key: str = ""
    sendgrid_from_email: str = ""
    
    # Twilio (SMS)
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""
    
    # JWT Authentication
    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 30
    
    # Celery
    celery_broker_url: str = ""
    celery_result_backend: str = ""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses lru_cache to ensure settings are loaded only once.
    """
    return Settings()

# Made with Bob
