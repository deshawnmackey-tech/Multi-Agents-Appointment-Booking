"""Microsoft Graph integration client helpers."""
from typing import Dict, List, Tuple
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json

from src.config import get_settings


class MicrosoftGraphClient:
    """Microsoft Graph calendar client with OAuth helpers and config checks."""

    scopes = (
        "openid",
        "email",
        "profile",
        "offline_access",
        "Calendars.Read",
    )

    required_fields = (
        "microsoft_client_id",
        "microsoft_client_secret",
        "microsoft_tenant_id",
        "microsoft_redirect_uri",
    )

    def __init__(self) -> None:
        self.settings = get_settings()

    def is_configured(self) -> bool:
        return self.settings.has_microsoft_calendar and bool(self.settings.microsoft_redirect_uri)

    def missing_fields(self) -> Dict[str, str]:
        missing = {}
        if not self.settings.microsoft_client_id:
            missing["microsoft_client_id"] = "Set MICROSOFT_CLIENT_ID"
        if not self.settings.microsoft_client_secret.get_secret_value():
            missing["microsoft_client_secret"] = "Set MICROSOFT_CLIENT_SECRET"
        if not self.settings.microsoft_tenant_id:
            missing["microsoft_tenant_id"] = "Set MICROSOFT_TENANT_ID"
        if not self.settings.microsoft_redirect_uri:
            missing["microsoft_redirect_uri"] = "Set MICROSOFT_REDIRECT_URI"
        return missing

    def ensure_configured(self) -> None:
        missing = self.missing_fields()
        if missing:
            details = ", ".join(missing.keys())
            raise ValueError(f"Microsoft Graph is not configured. Missing: {details}")

    @property
    def tenant_authority(self) -> str:
        """Build the base Microsoft OAuth authority URL."""
        return f"https://login.microsoftonline.com/{self.settings.microsoft_tenant_id}/oauth2/v2.0"

    def authorization_url(self, state: str) -> str:
        """Build the Microsoft consent URL for an authenticated app user."""
        self.ensure_configured()
        query = urlencode(
            {
                "client_id": self.settings.microsoft_client_id,
                "response_type": "code",
                "redirect_uri": self.settings.microsoft_redirect_uri,
                "response_mode": "query",
                "scope": " ".join(self.scopes),
                "state": state,
            }
        )
        return f"{self.tenant_authority}/authorize?{query}"

    def exchange_code(self, code: str) -> Dict[str, str]:
        """Exchange Microsoft's authorization code for OAuth tokens."""
        self.ensure_configured()
        payload = urlencode(
            {
                "client_id": self.settings.microsoft_client_id,
                "client_secret": self.settings.microsoft_client_secret.get_secret_value(),
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.settings.microsoft_redirect_uri,
            }
        ).encode("utf-8")
        request = Request(
            f"{self.tenant_authority}/token",
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        with urlopen(request, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))

    def list_calendars(self, access_token: str) -> List[Dict[str, str | bool]]:
        """Fetch Microsoft calendars for the authenticated account."""
        request = Request(
            "https://graph.microsoft.com/v1.0/me/calendars",
            headers={"Authorization": f"Bearer {access_token}"},
            method="GET",
        )
        with urlopen(request, timeout=15) as response:
            payload = json.loads(response.read().decode("utf-8"))
        calendars = []
        for item in payload.get("value", []):
            calendar_id = item.get("id")
            if not calendar_id:
                continue
            calendars.append(
                {
                    "id": calendar_id,
                    "summary": item.get("name") or calendar_id,
                    "primary": bool(item.get("isDefaultCalendar", False)),
                }
            )
        return calendars
