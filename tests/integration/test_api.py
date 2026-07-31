"""
Integration tests for API endpoints.
"""
from fastapi.testclient import TestClient


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

# Made with Bob