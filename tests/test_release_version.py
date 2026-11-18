from csms.config import BaseConfig


def test_application_release_version_is_1_0_0():
    assert BaseConfig.APP_VERSION == "1.0.0"


def test_health_endpoint_reports_release_version(client):
    response = client.get("/health")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload is not None
    assert payload["version"] == "1.0.0"
    assert payload["status"] == "ok"


def test_homepage_displays_release_version(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"v1.0.0" in response.data