"""CalDAV integration client scaffold."""
from typing import Dict

from src.config import get_settings


class CalDAVClient:
    """CalDAV client with configuration checks."""

    required_fields = (
        "caldav_url",
        "caldav_username",
        "caldav_password",
    )

    def __init__(self) -> None:
        self.settings = get_settings()

    def is_configured(self) -> bool:
        return self.settings.has_caldav_calendar

    def missing_fields(self) -> Dict[str, str]:
        missing = {}
        if not self.settings.caldav_url:
            missing["caldav_url"] = "Set CALDAV_URL"
        if not self.settings.caldav_username:
            missing["caldav_username"] = "Set CALDAV_USERNAME"
        if not self.settings.caldav_password.get_secret_value():
            missing["caldav_password"] = "Set CALDAV_PASSWORD"
        return missing

    def ensure_configured(self) -> None:
        missing = self.missing_fields()
        if missing:
            details = ", ".join(missing.keys())
            raise ValueError(f"CalDAV is not configured. Missing: {details}")
