from fastapi.testclient import TestClient
import pytest

from app import main as app_main
from app.providers.config import ProviderConfig
from app.providers import registry


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


def test_get_provider_config_not_found(client):
    r = client.get("/api/v1/providers/nope/config")
    assert r.status_code == 404


def test_update_provider_config_not_found(client):
    r = client.put("/api/v1/providers/nope/config", json={"config": {"foo": "bar"}})
    assert r.status_code == 404


def test_update_and_get_provider_config_roundtrip(client):
    # register a config and ensure update/read works
    pid = "test-config-pid"
    cfg = ProviderConfig(provider_id=pid, data={"a": 1})
    registry.register_provider_config(cfg)

    # update
    r = client.put(f"/api/v1/providers/{pid}/config", json={"config": {"b": 2}})
    assert r.status_code == 200
    d = r.json()
    # Response currently exposes the merged config mapping under `config`
    assert d["config"]["a"] == 1
    assert d["config"]["b"] == 2

    # get
    r2 = client.get(f"/api/v1/providers/{pid}/config")
    assert r2.status_code == 200
    d2 = r2.json()
    assert d2["config"]["b"] == 2


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
