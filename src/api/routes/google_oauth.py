"""Google Calendar OAuth routes."""
from datetime import timedelta
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Query, status
from googleapiclient.discovery import build
from sqlalchemy.orm import Session

from src.api.routes.auth import require_current_user
from src.database.session import get_db
from src.integrations.google_calendar import GoogleCalendarClient
from src.models.calendar import Calendar, CalendarProvider
from src.services.auth_service import AuthService
from src.utils.encryption import encryption_service

router = APIRouter(prefix="/auth/google")


@router.get("/login")
async def google_login(current_user=Depends(require_current_user)) -> Dict[str, str]:
    """Create a Google consent URL for the authenticated application user."""
    state_token = AuthService.create_access_token(
        {
            "user_id": str(current_user.id),
            "purpose": "google_calendar_oauth",
        },
        expires_delta=timedelta(minutes=10),
    )
    authorization_url, _ = GoogleCalendarClient().authorization_url(state_token)
    return {"authorization_url": authorization_url}


@router.get("/callback")
async def google_callback(
    code: str | None = Query(None),
    state_token: str = Query(..., alias="state"),
    error: str | None = Query(None),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Exchange Google's code and persist encrypted calendar credentials."""
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Google authorization failed: {error}",
        )

    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google authorization code is missing",
        )

    state_payload = AuthService.decode_token(state_token)
    if not state_payload or state_payload.get("purpose") != "google_calendar_oauth":
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

    try:
        credentials = GoogleCalendarClient().exchange_code(code, state_token)
        calendar_api = build("calendar", "v3", credentials=credentials, cache_discovery=False)
        calendar_items = calendar_api.calendarList().list().execute().get("items", [])
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google token exchange or calendar discovery failed",
        ) from exc

    encrypted_access_token = encryption_service.encrypt_token(credentials.token)
    encrypted_refresh_token = (
        encryption_service.encrypt_token(credentials.refresh_token)
        if credentials.refresh_token
        else None
    )

    connected_calendars = []
    for item in calendar_items:
        external_id = item.get("id")
        if not external_id:
            continue

        calendar = db.query(Calendar).filter(
            Calendar.user_id == user.id,
            Calendar.provider == CalendarProvider.GOOGLE,
            Calendar.calendar_id == external_id,
        ).first()

        if calendar is None:
            calendar = Calendar(
                user_id=user.id,
                provider=CalendarProvider.GOOGLE,
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

        connected_calendars.append({
            "id": external_id,
            "summary": item.get("summary", external_id),
            "primary": bool(item.get("primary")),
        })

    db.commit()
    return {
        "connected": True,
        "provider": "google",
        "calendar_count": len(connected_calendars),
        "calendars": connected_calendars,
    }
