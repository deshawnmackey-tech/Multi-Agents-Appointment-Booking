"""
Integration tests for API endpoints.
"""
import io
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlparse

from fastapi.testclient import TestClient
from src.integrations.caldav_client import CalDAVClient
from src.integrations.microsoft_graph import MicrosoftGraphClient
from src.services.auth_service import AuthService


def test_health_check(client: TestClient):
    """Test health check endpoint."""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data
    assert "version" in data


def test_root_endpoint(client: TestClient):
    """Test root endpoint."""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "docs" in data


def test_api_docs_available(client: TestClient):
    """Test that API documentation is available."""
    response = client.get("/api/docs")
    
    assert response.status_code == 200


def test_openapi_schema(client: TestClient):
    """Test that OpenAPI schema is available."""
    response = client.get("/api/openapi.json")
    
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "info" in data
    assert "paths" in data


def test_register_login_and_google_oauth_url(client: TestClient, sample_user_data):
    """An authenticated user can generate a Google OAuth consent URL."""
    register_response = client.post("/api/auth/register", json=sample_user_data)
    assert register_response.status_code == 201

    login_response = client.post(
        "/api/auth/login",
        data={
            "username": sample_user_data["email"],
            "password": sample_user_data["password"],
        },
    )
    assert login_response.status_code == 200
    tokens = login_response.json()
    assert tokens["access_token"]
    assert tokens["refresh_token"]

    oauth_response = client.get(
        "/auth/google/login",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert oauth_response.status_code == 200
    assert oauth_response.json()["authorization_url"].startswith(
        "https://accounts.google.com/o/oauth2/auth"
    )


def test_register_login_and_microsoft_oauth_url(client: TestClient, sample_user_data):
    """An authenticated user can request a Microsoft OAuth consent URL."""
    register_response = client.post("/api/auth/register", json=sample_user_data)
    assert register_response.status_code == 201

    login_response = client.post(
        "/api/auth/login",
        data={
            "username": sample_user_data["email"],
            "password": sample_user_data["password"],
        },
    )
    assert login_response.status_code == 200
    tokens = login_response.json()

    oauth_response = client.get(
        "/auth/microsoft/login",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )

    # This endpoint is configuration-driven in local/dev environments.
    assert oauth_response.status_code in (200, 400)
    if oauth_response.status_code == 200:
        authorization_url = oauth_response.json()["authorization_url"]
        assert authorization_url.startswith("https://login.microsoftonline.com/")
        parsed_query = parse_qs(urlparse(authorization_url).query)
        assert parsed_query["code_challenge_method"] == ["S256"]
        assert parsed_query["code_challenge"]
        state_token = parsed_query["state"][0]
        state_payload = AuthService.decode_token(state_token)
        assert state_payload["code_verifier"]
    else:
        assert "not configured" in oauth_response.json()["detail"].lower()


def test_microsoft_callback_returns_retry_url_when_code_expired(client: TestClient, sample_user_data, monkeypatch):
    """Expired Microsoft authorization codes produce a retryable response with a fresh sign-in URL."""
    register_response = client.post("/api/auth/register", json=sample_user_data)
    assert register_response.status_code == 201

    login_response = client.post(
        "/api/auth/login",
        data={
            "username": sample_user_data["email"],
            "password": sample_user_data["password"],
        },
    )
    assert login_response.status_code == 200
    tokens = login_response.json()

    login_url_response = client.get(
        "/auth/microsoft/login",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert login_url_response.status_code == 200
    authorization_url = login_url_response.json()["authorization_url"]
    state = parse_qs(urlparse(authorization_url).query)["state"][0]

    def raise_expired_code(*args, **kwargs):
        body = b'{"error":"invalid_grant","error_description":"AADSTS70008: The provided authorization code or refresh token has expired due to inactivity"}'
        raise HTTPError("https://login.microsoftonline.com/token", 400, "Bad Request", {}, io.BytesIO(body))

    monkeypatch.setattr("src.api.routes.microsoft_oauth.MicrosoftGraphClient.exchange_code", raise_expired_code)

    response = client.get(
        f"/auth/microsoft/callback?code=expired-code&state={state}",
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"].startswith("https://login.microsoftonline.com/")


def test_microsoft_exchange_code_includes_client_secret_with_pkce(monkeypatch):
    """Microsoft token exchange includes the client secret even when PKCE is used."""

    class DummySecret:
        def get_secret_value(self):
            return "top-secret"

    class DummySettings:
        microsoft_client_id = "client-id"
        microsoft_client_secret = DummySecret()
        microsoft_tenant_id = "tenant-id"
        microsoft_redirect_uri = "https://example.com/callback"
        has_microsoft_calendar = True

    monkeypatch.setattr("src.integrations.microsoft_graph.get_settings", lambda: DummySettings())

    captured = {}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return b'{"access_token":"abc"}'

    def fake_urlopen(request, timeout=15):
        captured["data"] = request.data.decode("utf-8")
        return FakeResponse()

    monkeypatch.setattr("src.integrations.microsoft_graph.urlopen", fake_urlopen)

    client = MicrosoftGraphClient()
    client.exchange_code("auth-code", code_verifier="verifier")

    assert "code_verifier=verifier" in captured["data"]
    assert "client_secret=top-secret" in captured["data"]


def test_microsoft_callback_returns_retry_url_for_unauthorized_exchange(client: TestClient, sample_user_data, monkeypatch):
    """Unauthorized Microsoft token exchanges trigger a fresh consent flow instead of a hard failure."""
    register_response = client.post("/api/auth/register", json=sample_user_data)
    assert register_response.status_code == 201

    login_response = client.post(
        "/api/auth/login",
        data={
            "username": sample_user_data["email"],
            "password": sample_user_data["password"],
        },
    )
    assert login_response.status_code == 200
    tokens = login_response.json()

    login_url_response = client.get(
        "/auth/microsoft/login",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert login_url_response.status_code == 200
    authorization_url = login_url_response.json()["authorization_url"]
    state = parse_qs(urlparse(authorization_url).query)["state"][0]

    def raise_unauthorized(*args, **kwargs):
        body = b'{"error":"invalid_client","error_description":"401 Unauthorized"}'
        raise HTTPError("https://login.microsoftonline.com/token", 401, "Unauthorized", {}, io.BytesIO(body))

    monkeypatch.setattr("src.api.routes.microsoft_oauth.MicrosoftGraphClient.exchange_code", raise_unauthorized)

    response = client.get(
        f"/auth/microsoft/callback?code=bad-code&state={state}",
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"].startswith("https://login.microsoftonline.com/")


def test_caldav_test_connection_handles_unconfigured(client: TestClient, monkeypatch):
    """CalDAV probe endpoint reports configuration errors without crashing."""
    monkeypatch.setattr(CalDAVClient, "test_connection", lambda self: (_ for _ in ()).throw(ValueError("CalDAV is not configured")))

    response = client.get("/api/integrations/caldav/test")
    assert response.status_code == 400
    assert "not configured" in response.json()["detail"].lower()


def test_caldav_test_connection_success(client: TestClient, monkeypatch):
    """CalDAV probe endpoint returns live-style connection details when successful."""
    monkeypatch.setattr(
        CalDAVClient,
        "test_connection",
        lambda self: {
            "connected": True,
            "calendar_count": 1,
            "calendars": [{"name": "Home", "url": "https://example.com/caldav/home"}],
        },
    )

    response = client.get("/api/integrations/caldav/test")
    assert response.status_code == 200
    payload = response.json()
    assert payload["connected"] is True
    assert payload["calendar_count"] == 1

# Made with Bob