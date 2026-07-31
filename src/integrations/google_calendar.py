"""Google Calendar OAuth integration client."""
from typing import Dict, Optional, Tuple

from google_auth_oauthlib.flow import Flow

from src.config import get_settings


class GoogleCalendarClient:
    """Google Calendar client with OAuth configuration helpers."""

    scopes = (
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/calendar",
    )

    required_fields = (
        "google_client_id",
        "google_client_secret",
        "google_redirect_uri",
    )

    def __init__(self) -> None:
        self.settings = get_settings()

    def is_configured(self) -> bool:
        return self.settings.has_google_calendar and bool(self.settings.google_redirect_uri)

    def missing_fields(self) -> Dict[str, str]:
        missing = {}
        if not self.settings.google_client_id:
            missing["google_client_id"] = "Set GOOGLE_CLIENT_ID"
        if not self.settings.google_client_secret.get_secret_value():
            missing["google_client_secret"] = "Set GOOGLE_CLIENT_SECRET"
        if not self.settings.google_redirect_uri:
            missing["google_redirect_uri"] = "Set GOOGLE_REDIRECT_URI"
        return missing

    def ensure_configured(self) -> None:
        missing = self.missing_fields()
        if missing:
            details = ", ".join(missing.keys())
            raise ValueError(f"Google Calendar is not configured. Missing: {details}")

    def build_flow(self, state: Optional[str] = None) -> Flow:
        """Create a Google OAuth flow from application settings."""
        self.ensure_configured()
        client_config = {
            "web": {
                "client_id": self.settings.google_client_id,
                "client_secret": self.settings.google_client_secret.get_secret_value(),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        }
        flow = Flow.from_client_config(
            client_config,
            scopes=list(self.scopes),
            state=state,
        )
        flow.redirect_uri = self.settings.google_redirect_uri
        return flow

    def authorization_url(self, state: str) -> Tuple[str, str]:
        """Build the Google consent URL for an authenticated app user."""
        flow = self.build_flow(state=state)
        return flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
        )

    def exchange_code(self, code: str, state: str):
        """Exchange Google's authorization code for OAuth credentials."""
        flow = self.build_flow(state=state)
        flow.fetch_token(code=code)
        return flow.credentials
