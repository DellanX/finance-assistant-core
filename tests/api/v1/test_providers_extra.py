import json

from app.providers.config import ProviderConfig
import app.providers.registry as registry


def test_get_provider_config_not_found(client, mock_provider):
    pid = mock_provider.get("id")
    # ensure no config exists for this provider id
    registry.provider_configs.pop(pid, None)
    r = client.get(f"/api/v1/providers/{pid}/config")
    assert r.status_code == 404


def test_get_provider_config_and_schema_success(client, mock_provider):
    pid = mock_provider.get("id")
    # register a ProviderConfig
    cfg = ProviderConfig(provider_id=pid, data={"a": 1}, schema={"x": "y"})
    registry.register_provider_config(cfg)

    r = client.get(f"/api/v1/providers/{pid}/config")
    assert r.status_code == 200
    assert r.json().get("config").get("a") == 1

    r2 = client.get(f"/api/v1/providers/{pid}/config/schema")
    assert r2.status_code == 200
    assert r2.json().get("schema") == {"x": "y"}


def test_update_provider_config_persist_called(client, mock_provider, monkeypatch):
    pid = mock_provider.get("id")
    called = {"persisted": False}

    def _fake_persist(pid_arg):
        called["persisted"] = True
        return True

    # providers module imports persist_provider_config at import-time; patch that reference
    import app.api.v1.providers as prov_module
    monkeypatch.setattr(prov_module, "persist_provider_config", _fake_persist)

    # ensure a ProviderConfig is registered so the endpoint can merge into it
    cfg = ProviderConfig(provider_id=pid, data={})
    registry.register_provider_config(cfg)

    payload = {"config": {"new": 2}}
    r = client.put(f"/api/v1/providers/{pid}/config", json=payload)
    assert r.status_code == 200
    assert called["persisted"] is True
    assert r.json().get("config").get("new") == 2


def test_delete_provider_stops_coordinator_and_removes_file(client, tmp_path):
    # create a dummy provider with a coordinator that has async stop
    class DummyCoord:
        def __init__(self):
            self.stopped = False

        async def stop(self):
            self.stopped = True

    class DummyProv:
        def __init__(self, pid, path):
            self.id = pid
            self.name = "dummy"
            self.coordinator = DummyCoord()
            self.config_path = path

    pid = "deltest"
    path = tmp_path / f"{pid}.json"
    path.write_text(json.dumps({"id": pid}))
    prov = DummyProv(pid, str(path))
    registry.active_providers[pid] = prov

    r = client.delete(f"/api/v1/providers/{pid}")
    assert r.status_code == 204
    # file should be removed
    assert not path.exists()
    # provider removed
    assert registry.get_provider(pid) is None


def test_create_provider_missing_integration(client):
    # Pydantic validation will reject missing required fields with 422
    r = client.post("/api/v1/providers", json={})
    assert r.status_code == 422


def test_create_provider_unknown_integration(client):
    r = client.post("/api/v1/providers", json={"integration": "no_such_integration"})
    assert r.status_code == 404
