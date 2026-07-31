"""SendGrid integration client scaffold."""
from typing import Dict

from src.config import get_settings


class SendGridClient:
    """SendGrid client with configuration checks."""

    required_fields = (
        "sendgrid_api_key",
        "sendgrid_from_email",
    )

    def __init__(self) -> None:
        self.settings = get_settings()

    def is_configured(self) -> bool:
        return self.settings.has_email_notifications

    def missing_fields(self) -> Dict[str, str]:
        missing = {}
        if not self.settings.sendgrid_api_key.get_secret_value():
            missing["sendgrid_api_key"] = "Set SENDGRID_API_KEY"
        if not self.settings.sendgrid_from_email:
            missing["sendgrid_from_email"] = "Set SENDGRID_FROM_EMAIL"
        return missing

    def ensure_configured(self) -> None:
        missing = self.missing_fields()
        if missing:
            details = ", ".join(missing.keys())
            raise ValueError(f"SendGrid is not configured. Missing: {details}")
