"""Integration readiness routes for external APIs."""
from typing import Any, Dict

from fastapi import APIRouter

from src.config import get_settings
from src.integrations.caldav_client import CalDAVClient
from src.integrations.google_calendar import GoogleCalendarClient
from src.integrations.microsoft_graph import MicrosoftGraphClient
from src.integrations.openai_client import OpenAIClient
from src.integrations.sendgrid_client import SendGridClient
from src.integrations.twilio_client import TwilioClient

router = APIRouter()


@router.get("/status")
async def integration_status() -> Dict[str, Any]:
    """Return which integrations are configured and which env vars are missing."""
    settings = get_settings()

    google = GoogleCalendarClient()
    microsoft = MicrosoftGraphClient()
    openai = OpenAIClient()
    caldav = CalDAVClient()
    sendgrid = SendGridClient()
    twilio = TwilioClient()

    status: Dict[str, Any] = {
        "openai": {
            "configured": openai.is_configured(),
            "missing": list(openai.missing_fields().values()),
        },
        "google_calendar": {
            "configured": google.is_configured(),
            "missing": list(google.missing_fields().values()),
        },
        "microsoft_graph": {
            "configured": microsoft.is_configured(),
            "missing": list(microsoft.missing_fields().values()),
        },
        "caldav": {
            "configured": caldav.is_configured(),
            "missing": list(caldav.missing_fields().values()),
        },
        "sendgrid": {
            "configured": sendgrid.is_configured(),
            "missing": list(sendgrid.missing_fields().values()),
        },
        "twilio": {
            "configured": twilio.is_configured(),
            "missing": list(twilio.missing_fields().values()),
        },
        "redis": {
            "configured": bool(settings.redis_url.get_secret_value()),
            "missing": [] if settings.redis_url.get_secret_value() else ["REDIS_URL"],
        },
    }

    ready = all(section["configured"] for section in status.values())

    return {
        "ready": ready,
        "integrations": status,
    }
