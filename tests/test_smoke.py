
"""Smoke tests for the CSMS v1.0.0 Flask application."""

from flask.testing import FlaskClient


def test_home_page_is_available(client: FlaskClient) -> None:
    """The home page should load successfully."""
    response = client.get("/")

    assert response.status_code == 200
    assert b"Community Services Management System" in response.data
    assert b"Sprint 0 - Developer Onboarding" in response.data
    assert b"Python with Flask" in response.data
    assert b"v1.0.0" in response.data


def test_health_endpoint_returns_ok(client: FlaskClient) -> None:
    """The health endpoint should report an operational application."""
    response = client.get("/health")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload is not None
    assert payload["status"] == "ok"
    assert payload["version"] == "1.0.0"


def test_unknown_page_returns_not_found(client: FlaskClient) -> None:
    """An unknown route should return HTTP 404."""
    response = client.get("/does-not-exist")

    assert response.status_code == 404
