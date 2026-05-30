import asyncio
import importlib
from fastapi.testclient import TestClient

from app import main as app_main
from app.api.v1.actions import _collect_provider_defs
import app.providers.registry as registry


def test_collect_provider_defs_sync_and_async():
    class P1:
        def get_action_definitions(self):
            return [{"id": "p1act", "name": "P1"}]

    class P2:
        async def get_action_definitions(self):
            return [{"id": "p2act", "name": "P2"}]

    class P3:
        def get_action_definitions(self):
            raise RuntimeError("boom")

    res1 = asyncio.run(_collect_provider_defs("pid1", P1()))
    assert res1 and res1[0]["provider_id"] == "pid1"

    res2 = asyncio.run(_collect_provider_defs("pid2", P2()))
    assert res2 and res2[0]["provider_id"] == "pid2"

    res3 = asyncio.run(_collect_provider_defs("pid3", P3()))
    assert res3 == []


def test_list_actions_integration_param_added(monkeypatch):
    # Provide one integration module that returns a type missing id (skipped)
    # and one with an id but no params so entity_id should be injected
    def _list_packages():
        return ["fake1", "fake2"]

    class Mod1:
        def get_action_types(self):
            return [{"name": "noid"}]

    class Mod2:
        def get_action_types(self):
            return [{"id": "intact", "name": "HasParams", "params": {}}]

    monkeypatch.setattr(registry, "list_integration_packages", _list_packages)

    def _fake_import(name, package=None):
        if name.endswith(".fake1"):
            return Mod1()
        if name.endswith(".fake2"):
            return Mod2()
        return importlib.import_module(name)

    monkeypatch.setattr(importlib, "import_module", _fake_import)

    with TestClient(app_main.app) as client:
        r = client.get("/api/v1/actions")
        assert r.status_code == 200
        ids = {a["id"] for a in r.json().get("actions", [])}
        assert "intact" in ids
        # verify params got entity_id
        for a in r.json().get("actions", []):
            if a.get("id") == "intact":
                assert "entity_id" in a.get("params", {})


def test_execute_integration_action_sync_and_async(monkeypatch, mock_provider):
    pid = mock_provider.get("id")
    prov = registry.get_provider(pid)

    # sync execute_action
    def sync_exec(action, params, dry_run=False):
        return {"ok": "sync"}

    prov.execute_action = sync_exec
    with TestClient(app_main.app) as client:
        payload = {"entity_id": pid, "params": {"from_account": "a1", "to_account": "a2", "amount": 1}}
        r = client.post("/api/v1/actions/simulate_transfer/execute", json=payload)
        assert r.status_code == 200
        assert r.json().get("status") == "ok"

    # async execute_action
    async def async_exec(action, params, dry_run=False):
        return {"ok": "async"}

    prov.execute_action = async_exec
    with TestClient(app_main.app) as client:
        payload = {"entity_id": pid, "params": {"from_account": "a1", "to_account": "a2", "amount": 1}}
        r = client.post("/api/v1/actions/simulate_transfer/execute", json=payload)
        assert r.status_code == 200
        assert r.json().get("status") == "ok"
