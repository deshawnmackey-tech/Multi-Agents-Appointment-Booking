"""Microsoft Graph integration client scaffold."""
from typing import Dict

from src.config import get_settings


class MicrosoftGraphClient:
    """Microsoft Graph calendar client with configuration checks."""

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
