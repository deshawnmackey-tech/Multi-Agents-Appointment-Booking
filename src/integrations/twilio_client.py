"""Twilio integration client scaffold."""
from typing import Dict

from src.config import get_settings


class TwilioClient:
    """Twilio client with configuration checks."""

    required_fields = (
        "twilio_account_sid",
        "twilio_auth_token",
        "twilio_phone_number",
    )

    def __init__(self) -> None:
        self.settings = get_settings()

    def is_configured(self) -> bool:
        return self.settings.has_sms_notifications

    def missing_fields(self) -> Dict[str, str]:
        missing = {}
        if not self.settings.twilio_account_sid:
            missing["twilio_account_sid"] = "Set TWILIO_ACCOUNT_SID"
        if not self.settings.twilio_auth_token.get_secret_value():
            missing["twilio_auth_token"] = "Set TWILIO_AUTH_TOKEN"
        if not self.settings.twilio_phone_number:
            missing["twilio_phone_number"] = "Set TWILIO_PHONE_NUMBER"
        return missing

    def ensure_configured(self) -> None:
        missing = self.missing_fields()
        if missing:
            details = ", ".join(missing.keys())
            raise ValueError(f"Twilio is not configured. Missing: {details}")
