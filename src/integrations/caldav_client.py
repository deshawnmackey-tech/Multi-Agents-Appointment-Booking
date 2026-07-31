"""CalDAV integration client scaffold."""
from typing import Any, Dict

from caldav import DAVClient

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

    def test_connection(self) -> Dict[str, Any]:
        """Attempt an authenticated CalDAV connection and enumerate calendars."""
        self.ensure_configured()
        with DAVClient(
            url=self.settings.caldav_url,
            username=self.settings.caldav_username,
            password=self.settings.caldav_password.get_secret_value(),
        ) as client:
            principal = client.principal()
            calendars = principal.calendars()

        payload = []
        for calendar in calendars:
            name = getattr(calendar, "name", None)
            payload.append({
                "name": name if name else "Unnamed calendar",
                "url": str(getattr(calendar, "url", "")),
            })

        return {
            "connected": True,
            "calendar_count": len(payload),
            "calendars": payload,
        }
