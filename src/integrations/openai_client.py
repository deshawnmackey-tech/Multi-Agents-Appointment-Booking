"""OpenAI integration client scaffold."""
from typing import Dict

from src.config import get_settings


class OpenAIClient:
    """OpenAI client with configuration checks."""

    required_fields = (
        "openai_api_key",
        "openai_model",
    )

    def __init__(self) -> None:
        self.settings = get_settings()

    def is_configured(self) -> bool:
        return self.settings.has_openai

    def missing_fields(self) -> Dict[str, str]:
        missing = {}
        if not self.settings.openai_api_key.get_secret_value():
            missing["openai_api_key"] = "Set OPENAI_API_KEY"
        if not self.settings.openai_model:
            missing["openai_model"] = "Set OPENAI_MODEL"
        return missing

    def ensure_configured(self) -> None:
        missing = self.missing_fields()
        if missing:
            details = ", ".join(missing.keys())
            raise ValueError(f"OpenAI is not configured. Missing: {details}")
