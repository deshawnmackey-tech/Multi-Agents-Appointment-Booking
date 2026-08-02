"""
Tests for the CalDAV integration client.
"""
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from src.integrations.caldav_client import CalDAVClient


def _fake_settings(
    url="https://caldav.example.com",
    username="user@example.com",
    secret="app-specific-secret",
    calendar_name="",
):
    """Build a minimal settings stand-in exposing only what CalDAVClient needs."""
    return SimpleNamespace(
        caldav_url=url,
        caldav_username=username,
        caldav_password=SimpleNamespace(get_secret_value=lambda: secret),
        caldav_calendar_name=calendar_name,
        has_caldav_calendar=bool(url and username and secret),
    )


@pytest.fixture
def client():
    """Create a CalDAVClient with fully configured fake settings."""
    caldav_client = CalDAVClient()
    caldav_client.settings = _fake_settings()
    return caldav_client


def _mock_calendar(name="Calendar"):
    calendar = MagicMock()
    calendar.name = name
    calendar.url = f"https://caldav.example.com/{name}"
    return calendar


def _mock_event(uid="event-123", summary="Team Sync", description=None, location=None,
                 start=None, end=None):
    event = MagicMock()
    component = {
        "uid": uid,
        "summary": summary,
        "description": description,
        "location": location,
    }
    component["dtstart"] = SimpleNamespace(dt=start) if start is not None else None
    component["dtend"] = SimpleNamespace(dt=end) if end is not None else None

    event.icalendar_component = component
    event.id = uid
    return event


class TestConfiguration:
    def test_is_configured_true_when_all_fields_present(self, client):
        assert client.is_configured() is True

    def test_is_configured_false_when_missing_fields(self):
        caldav_client = CalDAVClient()
        caldav_client.settings = _fake_settings(url="", username="", secret="")
        assert caldav_client.is_configured() is False

    def test_missing_fields_reports_each_absent_setting(self):
        caldav_client = CalDAVClient()
        caldav_client.settings = _fake_settings(url="", username="", secret="")
        missing = caldav_client.missing_fields()
        assert "caldav_url" in missing
        assert "caldav_username" in missing
        assert "caldav_password" in missing

    def test_ensure_configured_raises_when_not_configured(self):
        caldav_client = CalDAVClient()
        caldav_client.settings = _fake_settings(url="", username="", secret="")
        with pytest.raises(ValueError, match="CalDAV is not configured"):
            caldav_client.ensure_configured()

    def test_ensure_configured_passes_when_configured(self, client):
        client.ensure_configured()  # should not raise


class TestConnection:
    def test_test_connection_lists_calendars(self, client):
        cal1 = _mock_calendar("Home")
        cal2 = _mock_calendar("Work")

        mock_principal = MagicMock()
        mock_principal.calendars.return_value = [cal1, cal2]

        mock_dav_client = MagicMock()
        mock_dav_client.principal.return_value = mock_principal
        mock_dav_client.__enter__.return_value = mock_dav_client
        mock_dav_client.__exit__.return_value = False

        with patch("src.integrations.caldav_client.DAVClient", return_value=mock_dav_client):
            result = client.test_connection()

        assert result["connected"] is True
        assert result["calendar_count"] == 2
        assert {c["name"] for c in result["calendars"]} == {"Home", "Work"}

    def test_test_connection_raises_when_not_configured(self):
        caldav_client = CalDAVClient()
        caldav_client.settings = _fake_settings(url="", username="", secret="")
        with pytest.raises(ValueError):
            caldav_client.test_connection()


class TestEventCRUD:
    def _patched_dav_client(self, calendar):
        mock_principal = MagicMock()
        mock_principal.calendars.return_value = [calendar]

        mock_dav_client = MagicMock()
        mock_dav_client.principal.return_value = mock_principal
        mock_dav_client.__enter__.return_value = mock_dav_client
        mock_dav_client.__exit__.return_value = False
        return mock_dav_client

    def test_create_event_returns_serialized_event(self, client):
        calendar = _mock_calendar()
        start = datetime(2026, 1, 1, 10, 0)
        end = datetime(2026, 1, 1, 11, 0)
        calendar.save_event.return_value = _mock_event(
            uid="new-event", summary="Kickoff", start=start, end=end
        )

        mock_dav_client = self._patched_dav_client(calendar)

        with patch("src.integrations.caldav_client.DAVClient", return_value=mock_dav_client):
            result = client.create_event(
                summary="Kickoff",
                start=start,
                end=end,
                description="Project kickoff",
                location="Room 1",
            )

        calendar.save_event.assert_called_once()
        assert result["external_event_id"] == "new-event"
        assert result["summary"] == "Kickoff"
        assert result["start_time"] == start
        assert result["end_time"] == end

    def test_list_events_returns_serialized_events(self, client):
        calendar = _mock_calendar()
        start = datetime(2026, 1, 1)
        end = datetime(2026, 1, 2)
        calendar.date_search.return_value = [
            _mock_event(uid="e1", summary="Standup"),
            _mock_event(uid="e2", summary="Retro"),
        ]

        mock_dav_client = self._patched_dav_client(calendar)

        with patch("src.integrations.caldav_client.DAVClient", return_value=mock_dav_client):
            events = client.list_events(start, end)

        calendar.date_search.assert_called_once_with(start, end)
        assert [e["external_event_id"] for e in events] == ["e1", "e2"]

    def test_update_event_modifies_and_saves(self, client):
        calendar = _mock_calendar()
        existing_event = _mock_event(uid="e1", summary="Old Title")
        calendar.event_by_uid.return_value = existing_event

        mock_dav_client = self._patched_dav_client(calendar)

        with patch("src.integrations.caldav_client.DAVClient", return_value=mock_dav_client):
            result = client.update_event(external_event_id="e1", summary="New Title")

        assert existing_event.icalendar_component["summary"] == "New Title"
        existing_event.save.assert_called_once()
        assert result["external_event_id"] == "e1"

    def test_update_event_raises_when_not_found(self, client):
        calendar = _mock_calendar()
        calendar.event_by_uid.return_value = None
        mock_dav_client = self._patched_dav_client(calendar)

        with patch("src.integrations.caldav_client.DAVClient", return_value=mock_dav_client):
            with pytest.raises(ValueError, match="not found"):
                client.update_event(external_event_id="missing", summary="X")

    def test_delete_event_calls_delete(self, client):
        calendar = _mock_calendar()
        existing_event = _mock_event(uid="e1")
        calendar.event_by_uid.return_value = existing_event
        mock_dav_client = self._patched_dav_client(calendar)

        with patch("src.integrations.caldav_client.DAVClient", return_value=mock_dav_client):
            client.delete_event(external_event_id="e1")

        existing_event.delete.assert_called_once()

    def test_delete_event_raises_when_not_found(self, client):
        calendar = _mock_calendar()
        calendar.event_by_uid.return_value = None
        mock_dav_client = self._patched_dav_client(calendar)

        with patch("src.integrations.caldav_client.DAVClient", return_value=mock_dav_client):
            with pytest.raises(ValueError, match="not found"):
                client.delete_event(external_event_id="missing")

    def test_get_calendar_by_name_not_found_raises(self, client):
        calendar = _mock_calendar("Work")
        client.settings.caldav_calendar_name = "Personal"
        mock_dav_client = self._patched_dav_client(calendar)

        with patch("src.integrations.caldav_client.DAVClient", return_value=mock_dav_client):
            with pytest.raises(ValueError, match="Personal"):
                client.list_events(datetime(2026, 1, 1), datetime(2026, 1, 2))

    def test_get_calendar_raises_when_no_calendars(self, client):
        mock_principal = MagicMock()
        mock_principal.calendars.return_value = []

        mock_dav_client = MagicMock()
        mock_dav_client.principal.return_value = mock_principal
        mock_dav_client.__enter__.return_value = mock_dav_client
        mock_dav_client.__exit__.return_value = False

        with patch("src.integrations.caldav_client.DAVClient", return_value=mock_dav_client):
            with pytest.raises(ValueError, match="No CalDAV calendars"):
                client.list_events(datetime(2026, 1, 1), datetime(2026, 1, 2))

# Made with Bob
