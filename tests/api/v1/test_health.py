from fastapi.testclient import TestClient
import pytest

from app import main as app_main


@pytest.fixture(autouse=True)
def client():
    with TestClient(app_main.app) as c:
        yield c


def test_api_health_check(client):
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    data = r.json()
    assert data.get("status") == "ok"
    assert isinstance(data.get("providers"), dict)
def test_api_health_handles_registry_errors(client, monkeypatch):
    # simulate coordinator_statuses raising
    def _boom():
        raise RuntimeError("boom")

    monkeypatch.setattr("app.providers.registry.coordinator_statuses", _boom)
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json()["providers"] == {"error": "failed to collect provider statuses"}


def test_get_provider_config_raises_500_on_exception(client, monkeypatch):
    from fastapi import HTTPException

    def _boom(pid):
        raise HTTPException(status_code=500, detail="boom")

    monkeypatch.setattr("app.providers.registry.get_provider_config", _boom)
    monkeypatch.setattr("app.api.v1.providers.get_provider_config", _boom)
    r = client.get("/api/v1/providers/foo/config")
    assert r.status_code == 500


def test_update_provider_config_raises_500_on_exception(client, monkeypatch):
    from fastapi import HTTPException

    def _boom(pid):
        raise HTTPException(status_code=500, detail="boom")

    monkeypatch.setattr("app.providers.registry.get_provider_config", _boom)
    monkeypatch.setattr("app.api.v1.providers.get_provider_config", _boom)
    r = client.put("/api/v1/providers/foo/config", json={"config": {"x": 1}})
    assert r.status_code == 500
