import importlib

import app.providers.registry as registry


def test_get_actions_includes_core_and_integration(client, mock_provider):
    r = client.get("/api/v1/actions")
    assert r.status_code == 200
    data = r.json()
    ids = {a["id"] for a in data.get("actions", [])}
    assert "refresh" in ids
    assert "simulate_transfer" in ids


def test_get_actions_handles_get_action_types_exception(client, monkeypatch):
    def _list():
        return ["badmod"]

    class Mod:
        def get_action_types(self):
            raise RuntimeError("nope")

    monkeypatch.setattr(registry, "list_integration_packages", _list)

    def _fake_import(name, package=None):
        if name.endswith(".badmod"):
            return Mod()
        return importlib.import_module(name)

    monkeypatch.setattr(importlib, "import_module", _fake_import)

    r = client.get("/api/v1/actions")
    assert r.status_code == 200
    ids = {a["id"] for a in r.json().get("actions", [])}
    assert "refresh" in ids


def test_get_actions_integration_param_added(client, monkeypatch):
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

    r = client.get("/api/v1/actions")
    assert r.status_code == 200
    ids = {a["id"] for a in r.json().get("actions", [])}
    assert "intact" in ids
    for a in r.json().get("actions", []):
        if a.get("id") == "intact":
            assert "entity_id" in a.get("params", {})


def test_get_actions_import_failure(client, monkeypatch):
    monkeypatch.setattr(registry, "list_integration_packages", lambda: ["badint"]) 

    def fake_import(name, package=None):
        if name == "app.providers.badint":
            raise ImportError("nope")
        return importlib.import_module(name)

    monkeypatch.setattr(importlib, "import_module", fake_import)

    r = client.get("/api/v1/actions")
    assert r.status_code == 200
