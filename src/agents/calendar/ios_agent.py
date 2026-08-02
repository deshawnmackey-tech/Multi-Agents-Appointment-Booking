"""
iOS Calendar Agent for syncing appointments with Apple/iCloud calendars via CalDAV.

Unlike the NLP-driven agents, this agent wraps the CalDAV protocol directly and
does not require an LLM - it performs deterministic CRUD and availability
operations against the configured CalDAV server.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.integrations.caldav_client import CalDAVClient
from src.utils.logger import get_logger

logger = get_logger(__name__)


class IOSCalendarAgent:
    """
    Calendar integration agent for Apple/iOS calendars using the CalDAV protocol.

    Supported actions (via `process`):
        - "create_event": create a new calendar event
        - "update_event": update an existing calendar event
        - "delete_event": delete a calendar event
        - "list_events": list events within a date range
        - "check_availability": determine whether a time range is free
    """

    def __init__(self, client: Optional[CalDAVClient] = None):
        """
        Initialize the iOS calendar agent.

        Args:
            client: Optional CalDAVClient instance (mainly for testing/injection)
        """
        self.client = client or CalDAVClient()
        logger.info("Initialized iOS Calendar agent")

    def is_configured(self) -> bool:
        """Check whether CalDAV credentials are configured."""
        return self.client.is_configured()

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a calendar action request.

        Args:
            input_data: Dictionary containing:
                - action: One of "create_event", "update_event", "delete_event",
                  "list_events", "check_availability"
                - data: Action-specific payload

        Returns:
            Result dictionary with a "success" flag and either "data" or "error"
        """
        action = input_data.get("action")
        data = input_data.get("data", {})

        logger.info(f"IOSCalendarAgent processing action: {action}")

        try:
            if action == "create_event":
                return self._create_event(data)
            elif action == "update_event":
                return self._update_event(data)
            elif action == "delete_event":
                return self._delete_event(data)
            elif action == "list_events":
                return self._list_events(data)
            elif action == "check_availability":
                return self._check_availability(data)
            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {action}"
                }
        except Exception as e:
            logger.error(f"IOSCalendarAgent error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def _create_event(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new event on the iOS/iCloud calendar."""
        event = self.client.create_event(
            summary=data["summary"],
            start=data["start"],
            end=data["end"],
            description=data.get("description"),
            location=data.get("location"),
            calendar_name=data.get("calendar_name"),
        )
        return {"success": True, "data": event}

    def _update_event(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing event on the iOS/iCloud calendar."""
        event = self.client.update_event(
            external_event_id=data["external_event_id"],
            summary=data.get("summary"),
            start=data.get("start"),
            end=data.get("end"),
            description=data.get("description"),
            location=data.get("location"),
            calendar_name=data.get("calendar_name"),
        )
        return {"success": True, "data": event}

    def _delete_event(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Delete an event from the iOS/iCloud calendar."""
        self.client.delete_event(
            external_event_id=data["external_event_id"],
            calendar_name=data.get("calendar_name"),
        )
        return {"success": True, "data": {"external_event_id": data["external_event_id"]}}

    def _list_events(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """List events within a date range."""
        events = self.client.list_events(
            start=data["start"],
            end=data["end"],
            calendar_name=data.get("calendar_name"),
        )
        return {"success": True, "data": events}

    def _check_availability(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check whether a requested time range is free of conflicts.

        Args:
            data: Dictionary with "start", "end", and optional "calendar_name"

        Returns:
            Result dictionary with "available" flag and any "conflicts"
        """
        start: datetime = data["start"]
        end: datetime = data["end"]

        events = self.client.list_events(
            start=start,
            end=end,
            calendar_name=data.get("calendar_name"),
        )

        conflicts: List[Dict[str, Any]] = [
            event for event in events
            if self._overlaps(event, start, end)
        ]

        return {
            "success": True,
            "data": {
                "available": len(conflicts) == 0,
                "conflicts": conflicts,
            }
        }

    @staticmethod
    def _overlaps(event: Dict[str, Any], start: datetime, end: datetime) -> bool:
        """Check if an event's time range overlaps with the given window."""
        event_start = event.get("start_time")
        event_end = event.get("end_time")

        if event_start is None or event_end is None:
            return False

        return event_start < end and event_end > start

# Made with Bob
