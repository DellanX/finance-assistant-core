import importlib
import asyncio

from app import main as app_main
from app.api.v1 import actions as actions_mod
import app.providers.registry as registry


def test_execute_action_direct_dict_payload():
    # call the function directly with a dict payload to hit isinstance branch
    pid = next(iter(registry.active_providers.keys()))
    res = asyncio.run(actions_mod.execute_action("refresh", {"entity_id": pid}))
    assert res["status"] == "ok"


def test_execute_action_integration_import_raises(client, monkeypatch):
    monkeypatch.setattr(registry, "list_integration_packages", lambda: ["bad_import"]) 

    def fake_import(name, package=None):
        if name == "app.providers.bad_import":
            raise ImportError("boom")
        return importlib.import_module(name)

    monkeypatch.setattr(importlib, "import_module", fake_import)
    r = client.post("/api/v1/actions/some_action/execute", json={})
    assert r.status_code == 404


def test_execute_action_get_action_types_raises(client, monkeypatch, mock_provider):
    monkeypatch.setattr(registry, "list_integration_packages", lambda: ["mock"]) 

    class FaultyMod:
        @staticmethod
        def get_action_types():
            raise RuntimeError("bad")

    def fake_import(name, package=None):
        if name == "app.providers.mock":
            return FaultyMod
        return importlib.import_module(name)

    monkeypatch.setattr(importlib, "import_module", fake_import)
    pid = mock_provider.get("id")
    r = client.post("/api/v1/actions/doesnotexist/execute", json={"entity_id": pid})
    assert r.status_code == 404


def test_integration_provider_not_found(client, monkeypatch):
    monkeypatch.setattr(registry, "list_integration_packages", lambda: ["fakeint"]) 

    class Mod:
        @staticmethod
        def get_action_types():
            return [{"id": "i1"}]

    def fake_import(name, package=None):
        if name == "app.providers.fakeint":
            return Mod
        return importlib.import_module(name)

    monkeypatch.setattr(importlib, "import_module", fake_import)
    r = client.post("/api/v1/actions/i1/execute", json={"entity_id": "no-such"})
    assert r.status_code == 404


def test_integration_removes_entity_id_before_call(client, monkeypatch):
    pid = "prov-x"

    class Prov:
        def __init__(self, id):
            self._id = id

        def execute_action(self, action, params, dry_run=False):
            assert "entity_id" not in params
            return {"ok": True}

    prov = Prov(pid)
    registry.active_providers[pid] = prov

    monkeypatch.setattr(registry, "list_integration_packages", lambda: ["fakeint"]) 

    class Mod2:
        @staticmethod
        def get_action_types():
            return [{"id": "doit"}]

    def fake_import(name, package=None):
        if name == "app.providers.fakeint":
            return Mod2
        return importlib.import_module(name)

    monkeypatch.setattr(importlib, "import_module", fake_import)

    payload = {"entity_id": pid, "params": {"entity_id": "should-go", "a": 1}}
    r = client.post("/api/v1/actions/doit/execute", json=payload)
    assert r.status_code == 200

    registry.active_providers.pop(pid, None)
