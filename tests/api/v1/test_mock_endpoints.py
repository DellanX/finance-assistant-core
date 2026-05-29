from fastapi.testclient import TestClient
import pytest

from app import main as app_main
from app.providers import registry


@pytest.fixture(autouse=True)
def client():
    with TestClient(app_main.app) as c:
        yield c


def test_get_mock_state_existing(client, mock_provider):
    pid = mock_provider.get("id")
    r = client.get(f"/api/v1/mock/state/{pid}")
    assert r.status_code == 200
    assert isinstance(r.json().get("state"), dict)


def test_get_mock_state_not_found(client):
    r = client.get("/api/v1/mock/state/notfound")
    assert r.status_code == 404


def test_update_mock_state_and_persist(client, mock_provider):
    pid = mock_provider.get("id")
    updates = {"name": "Updated Mock Name"}
    r = client.post(f"/api/v1/mock/state/{pid}", json=updates)
    assert r.status_code == 200
    assert r.json().get("status") == "success"

    # subsequent GET should reflect updated state
    r2 = client.get(f"/api/v1/mock/state/{pid}")
    assert r2.status_code == 200
    assert r2.json()["state"]["name"] == "Updated Mock Name"


def test_update_mock_state_not_mock(client):
    class Dummy:
        id = "dummy-no-update"

    registry.add_provider(Dummy())
    try:
        r = client.post(f"/api/v1/mock/state/{Dummy.id}", json={"x": 1})
        assert r.status_code == 400
    finally:
        try:
            del registry.active_providers[Dummy.id]
        except Exception:
            pass
