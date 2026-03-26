"""API endpoint tests."""

import pytest
from fastapi.testclient import TestClient

from agent.server import app

client = TestClient(app)

def test_get_status():
    """Test the /api/v1/status endpoint."""
    response = client.get("/api/v1/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"
    assert "version" in data
    assert "platform" in data
    assert "tools_ready" in data

def test_post_wifi_invalid_input():
    """Test input sanitization on WiFi configuration."""
    response = client.post(
        "/api/v1/wifi",
        json={"ssid": "MyWifi", "password": "pass'word"}
    )
    assert response.status_code == 400
    assert "Invalid characters" in response.json()["error"]
