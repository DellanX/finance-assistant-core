import asyncio
import importlib

from app.api.v1.actions import _collect_provider_defs
import app.providers.registry as registry


def test_collect_provider_defs_variants():
    class P1:
        def get_action_definitions(self):
            return [{"id": "p1", "name": "P1"}]

    class P2:
        async def get_action_definitions(self):
            return [{"id": "p2", "name": "P2"}]

    class P3:
        def get_action_definitions(self):
            raise RuntimeError("boom")

    res1 = asyncio.run(_collect_provider_defs("pid1", P1()))
    assert res1 and res1[0]["provider_id"] == "pid1"

    res2 = asyncio.run(_collect_provider_defs("pid2", P2()))
    assert res2 and res2[0]["provider_id"] == "pid2"

    res3 = asyncio.run(_collect_provider_defs("pid3", P3()))
    assert res3 == []


def test_list_provider_actions_entity_id_existing_default(client, monkeypatch):
    # provider module returns an action type with an entity_id param already
    class Mod:
        @staticmethod
        def get_action_types():
            return [{"id": "has_eid", "params": {"entity_id": {"type": "string"}}}]

    def fake_import(name, package=None):
        if name == "app.providers.mock":
            return Mod
        return importlib.import_module(name)

    monkeypatch.setattr(importlib, "import_module", fake_import)
    some = next(iter(registry.active_providers.keys()))
    r = client.get(f"/api/v1/actions/providers/{some}")
    assert r.status_code == 200
    data = r.json()
    for a in data.get("actions", []):
        if a.get("id") == "has_eid":
            assert a.get("params", {}).get("entity_id", {}).get("default") == some
            break


def test_execute_export_state_sync_getter(client, mock_provider):
    pid = mock_provider.get("id")
    prov = registry.get_provider(pid)

    def sget():
        return {"ok": True}

    prov.get_state = sget
    r = client.post(f"/api/v1/actions/export_state/execute", json={"entity_id": pid})
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    assert r.json()["result"]["ok"] is True


def test_force_reconcile_force_method_sync_and_async(client, mock_provider):
    pid = mock_provider.get("id")
    prov = registry.get_provider(pid)

    def fforce():
        return "forced"

    prov.force_reconcile = fforce
    r = client.post(f"/api/v1/actions/force_reconcile/execute", json={"entity_id": pid})
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

    async def aforce():
        await asyncio.sleep(0)
        return "aforced"

    prov.force_reconcile = aforce
    r = client.post(f"/api/v1/actions/force_reconcile/execute", json={"entity_id": pid})
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_execute_core_provider_not_found(client):
    r = client.post("/api/v1/actions/refresh/execute", json={"entity_id": "no-such"})
    assert r.status_code == 404


def test_list_provider_actions_provider_not_found(client):
    r = client.get("/api/v1/actions/providers/no-such")
    assert r.status_code == 404


def test_list_provider_actions_infer_integration_attribute(client):
    class FakeProvider:
        def __init__(self, id):
            self._id = id
            self.integration = "mock"

    pid = "fake-p"
    fp = FakeProvider(pid)
    registry.active_providers[pid] = fp
    r = client.get(f"/api/v1/actions/providers/{pid}")
    assert r.status_code == 200
    registry.active_providers.pop(pid, None)


def test_list_provider_actions_import_raises_handled(client, monkeypatch):
    def fake_import(name, package=None):
        raise ImportError("boom")

    monkeypatch.setattr(importlib, "import_module", fake_import)
    some = next(iter(registry.active_providers.keys()))
    r = client.get(f"/api/v1/actions/providers/{some}")
    assert r.status_code == 200


def test_list_provider_actions_skips_types_without_id(client, monkeypatch):
    monkeypatch.setattr(registry, "list_integration_packages", lambda: ["mock"]) 

    class Mod3:
        @staticmethod
        def get_action_types():
            return [{"name": "noid"}]

    def fake_import(name, package=None):
        if name == "app.providers.mock":
            return Mod3
        return importlib.import_module(name)

    monkeypatch.setattr(importlib, "import_module", fake_import)
    some = next(iter(registry.active_providers.keys()))
    r = client.get(f"/api/v1/actions/providers/{some}")
    assert r.status_code == 200


def test_list_provider_actions_injects_entity_id_default(client, monkeypatch):
    class Mod4:
        @staticmethod
        def get_action_types():
            return [{"id": "only", "params": {}}]

    def fake_import(name, package=None):
        if name == "app.providers.mock":
            return Mod4
        return importlib.import_module(name)

    monkeypatch.setattr(importlib, "import_module", fake_import)
    some = next(iter(registry.active_providers.keys()))
    r = client.get(f"/api/v1/actions/providers/{some}")
    assert r.status_code == 200
    data = r.json()
    for a in data.get("actions", []):
        if a.get("id") == "only":
            assert a.get("params", {}).get("entity_id", {}).get("default") == some
            break


def test_list_provider_actions_infer_integration_exception(client):
    class BadProvider:
        def __init__(self, id):
            self._id = id

        def __getattribute__(self, name):
            if name == "__class__":
                raise RuntimeError("boom")
            return object.__getattribute__(self, name)

    pid = "bad-p"
    bp = BadProvider(pid)
    registry.active_providers[pid] = bp
    r = client.get(f"/api/v1/actions/providers/{pid}")
    assert r.status_code == 200
    registry.active_providers.pop(pid, None)
