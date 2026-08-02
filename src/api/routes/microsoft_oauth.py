"""Microsoft Graph OAuth routes."""
import json
import secrets
from datetime import timedelta
from typing import Any, Dict
from urllib.error import HTTPError

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from src.api.routes.auth import require_current_user
from src.database.session import get_db
from src.integrations.microsoft_graph import MicrosoftGraphClient
from src.models.calendar import Calendar, CalendarProvider
from src.services.auth_service import AuthService
from src.utils.encryption import encryption_service

router = APIRouter(prefix="/auth/microsoft")


def _is_retryable_microsoft_error(detail: str) -> bool:
    lowered = detail.lower()
    return any(
        marker in lowered
        for marker in (
            "aadsts70008",
            "expired",
            "invalid_grant",
            "invalid_client",
            "unauthorized",
            "authorization code",
            "has already been used",
        )
    )


@router.get("/login")
async def microsoft_login(current_user=Depends(require_current_user)) -> Dict[str, str]:
    """Create a Microsoft consent URL for the authenticated application user."""
    code_verifier = secrets.token_urlsafe(64)
    state_token = AuthService.create_access_token(
        {
            "user_id": str(current_user.id),
            "purpose": "microsoft_calendar_oauth",
            "code_verifier": code_verifier,
        },
        expires_delta=timedelta(minutes=10),
    )

    try:
        authorization_url = MicrosoftGraphClient().authorization_url(state_token, code_verifier=code_verifier)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return {"authorization_url": authorization_url}


@router.get("/callback")
async def microsoft_callback(
    code: str | None = Query(None),
    state_token: str = Query(..., alias="state"),
    error: str | None = Query(None),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Exchange Microsoft's code and persist encrypted calendar credentials."""
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Microsoft authorization failed: {error}",
        )

    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Microsoft authorization code is missing",
        )

    state_payload = AuthService.decode_token(state_token)
    if not state_payload or state_payload.get("purpose") != "microsoft_calendar_oauth":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Microsoft OAuth state is invalid or expired",
        )

    user = AuthService.get_user_by_id(db, state_payload.get("user_id"))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OAuth user no longer exists",
        )

    code_verifier = state_payload.get("code_verifier")

    client = MicrosoftGraphClient()
    try:
        token_payload = client.exchange_code(code, code_verifier=code_verifier)
        access_token = token_payload["access_token"]
        refresh_token = token_payload.get("refresh_token")
        calendars = client.list_calendars(access_token)
    except HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(error_body)
            detail = payload.get("error_description") or payload.get("error") or error_body
        except json.JSONDecodeError:
            detail = error_body or str(exc)

        if _is_retryable_microsoft_error(detail):
            fresh_code_verifier = secrets.token_urlsafe(64)
            fresh_state_token = AuthService.create_access_token(
                {
                    "user_id": str(user.id),
                    "purpose": "microsoft_calendar_oauth",
                    "code_verifier": fresh_code_verifier,
                },
                expires_delta=timedelta(minutes=10),
            )
            fresh_authorization_url = MicrosoftGraphClient().authorization_url(
                fresh_state_token,
                code_verifier=fresh_code_verifier,
            )
            return RedirectResponse(
                url=fresh_authorization_url,
                status_code=status.HTTP_303_SEE_OTHER,
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Microsoft token exchange failed: {detail}",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Microsoft token exchange or calendar discovery failed: {exc}",
        ) from exc

    encrypted_access_token = encryption_service.encrypt_token(access_token)
    encrypted_refresh_token = (
        encryption_service.encrypt_token(refresh_token)
        if refresh_token
        else None
    )

    connected_calendars = []
    for item in calendars:
        external_id = item["id"]
        calendar = db.query(Calendar).filter(
            Calendar.user_id == user.id,
            Calendar.provider == CalendarProvider.OUTLOOK,
            Calendar.calendar_id == external_id,
        ).first()

        if calendar is None:
            calendar = Calendar(
                user_id=user.id,
                provider=CalendarProvider.OUTLOOK,
                name=item.get("summary", external_id),
                calendar_id=external_id,
                external_id=external_id,
                access_token=encrypted_access_token,
                refresh_token=encrypted_refresh_token,
                is_primary=bool(item.get("primary")),
            )
            db.add(calendar)
        else:
            calendar.access_token = encrypted_access_token
            if encrypted_refresh_token:
                calendar.refresh_token = encrypted_refresh_token
            calendar.is_primary = bool(item.get("primary"))
            calendar.name = item.get("summary", external_id)
            calendar.external_id = external_id
            calendar.calendar_id = external_id

        connected_calendars.append(
            {
                "id": external_id,
                "summary": item.get("summary", external_id),
                "primary": bool(item.get("primary")),
            }
        )

    db.commit()
    return {
        "connected": True,
        "provider": "microsoft",
        "calendar_count": len(connected_calendars),
        "calendars": connected_calendars,
    }
