"""CalDAV integration client for connecting to and managing iOS/Apple calendars."""
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, Iterator, List, Optional

from caldav import Calendar as DAVCalendar
from caldav import DAVClient

from src.config import get_settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class CalDAVClient:
    """CalDAV client with configuration checks and event CRUD operations."""

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

    @contextmanager
    def _client(self) -> Iterator[DAVClient]:
        """Yield an authenticated DAVClient, ensuring configuration first."""
        self.ensure_configured()
        with DAVClient(
            url=self.settings.caldav_url,
            username=self.settings.caldav_username,
            password=self.settings.caldav_password.get_secret_value(),
        ) as client:
            yield client

    def _get_calendar(self, client: DAVClient, calendar_name: Optional[str] = None) -> DAVCalendar:
        """
        Resolve a calendar by name, falling back to the configured default
        or the principal's first available calendar.

        Args:
            client: An authenticated DAVClient
            calendar_name: Optional calendar name override

        Returns:
            The matching DAVCalendar

        Raises:
            ValueError: If no calendars are available, or the named one isn't found
        """
        principal = client.principal()
        calendars = principal.calendars()

        if not calendars:
            raise ValueError("No CalDAV calendars found for this account")

        target_name = calendar_name or self.settings.caldav_calendar_name
        if target_name:
            for calendar in calendars:
                if getattr(calendar, "name", None) == target_name:
                    return calendar
            raise ValueError(f"CalDAV calendar '{target_name}' not found")

        return calendars[0]

    def test_connection(self) -> Dict[str, Any]:
        """Attempt an authenticated CalDAV connection and enumerate calendars."""
        with self._client() as client:
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

    def list_events(
        self,
        start: datetime,
        end: datetime,
        calendar_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        List events within a date range from the CalDAV calendar.

        Args:
            start: Range start (inclusive)
            end: Range end (exclusive)
            calendar_name: Optional calendar name override

        Returns:
            List of event dictionaries with external_event_id, summary,
            start, end, description, and location
        """
        with self._client() as client:
            calendar = self._get_calendar(client, calendar_name)
            events = calendar.date_search(start, end)
            return [self._serialize_event(event) for event in events]

    def create_event(
        self,
        summary: str,
        start: datetime,
        end: datetime,
        description: Optional[str] = None,
        location: Optional[str] = None,
        calendar_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new event on the CalDAV calendar.

        Args:
            summary: Event title
            start: Event start datetime
            end: Event end datetime
            description: Optional event description
            location: Optional event location
            calendar_name: Optional calendar name override

        Returns:
            Serialized event dictionary including its external_event_id (UID)
        """
        with self._client() as client:
            calendar = self._get_calendar(client, calendar_name)
            event = calendar.save_event(
                dtstart=start,
                dtend=end,
                summary=summary,
                description=description,
                location=location,
            )
            logger.info(f"Created CalDAV event '{summary}'")
            return self._serialize_event(event)

    def update_event(
        self,
        external_event_id: str,
        summary: Optional[str] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        calendar_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update an existing CalDAV event by UID.

        Args:
            external_event_id: The event's UID on the CalDAV server
            summary: Optional updated title
            start: Optional updated start datetime
            end: Optional updated end datetime
            description: Optional updated description
            location: Optional updated location
            calendar_name: Optional calendar name override

        Returns:
            Serialized event dictionary reflecting the update

        Raises:
            ValueError: If the event cannot be found
        """
        with self._client() as client:
            calendar = self._get_calendar(client, calendar_name)
            event = calendar.event_by_uid(external_event_id)
            if event is None:
                raise ValueError(f"CalDAV event '{external_event_id}' not found")

            component = event.icalendar_component
            if summary is not None:
                component["summary"] = summary
            if start is not None:
                component["dtstart"] = start
            if end is not None:
                component["dtend"] = end
            if description is not None:
                component["description"] = description
            if location is not None:
                component["location"] = location

            event.save()
            logger.info(f"Updated CalDAV event '{external_event_id}'")
            return self._serialize_event(event)

    def delete_event(self, external_event_id: str, calendar_name: Optional[str] = None) -> None:
        """
        Delete a CalDAV event by UID.

        Args:
            external_event_id: The event's UID on the CalDAV server
            calendar_name: Optional calendar name override

        Raises:
            ValueError: If the event cannot be found
        """
        with self._client() as client:
            calendar = self._get_calendar(client, calendar_name)
            event = calendar.event_by_uid(external_event_id)
            if event is None:
                raise ValueError(f"CalDAV event '{external_event_id}' not found")
            event.delete()
            logger.info(f"Deleted CalDAV event '{external_event_id}'")

    @staticmethod
    def _serialize_event(event: Any) -> Dict[str, Any]:
        """Convert a caldav Event object into a plain dictionary."""
        component = event.icalendar_component

        def _as_str(value: Any) -> Any:
            return str(value) if value is not None else None

        start = component.get("dtstart")
        end = component.get("dtend")

        return {
            "external_event_id": str(component.get("uid", getattr(event, "id", ""))),
            "summary": _as_str(component.get("summary")),
            "description": _as_str(component.get("description")),
            "location": _as_str(component.get("location")),
            "start_time": start.dt if start else None,
            "end_time": end.dt if end else None,
        }
