"""Microsoft Graph OAuth routes."""
from datetime import timedelta
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.api.routes.auth import require_current_user
from src.database.session import get_db
from src.integrations.microsoft_graph import MicrosoftGraphClient
from src.models.calendar import Calendar, CalendarProvider
from src.services.auth_service import AuthService
from src.utils.encryption import encryption_service

router = APIRouter(prefix="/auth/microsoft")


@router.get("/login")
async def microsoft_login(current_user=Depends(require_current_user)) -> Dict[str, str]:
    """Create a Microsoft consent URL for the authenticated application user."""
    state_token = AuthService.create_access_token(
        {
            "user_id": str(current_user.id),
            "purpose": "microsoft_calendar_oauth",
        },
        expires_delta=timedelta(minutes=10),
    )

    try:
        authorization_url = MicrosoftGraphClient().authorization_url(state_token)
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
            detail="Invalid or expired OAuth state",
        )

    user = AuthService.get_user_by_id(db, state_payload.get("user_id"))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OAuth user no longer exists",
        )

    client = MicrosoftGraphClient()
    try:
        token_payload = client.exchange_code(code)
        access_token = token_payload["access_token"]
        refresh_token = token_payload.get("refresh_token")
        calendars = client.list_calendars(access_token)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Microsoft token exchange or calendar discovery failed",
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
                calendar_id=external_id,
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
