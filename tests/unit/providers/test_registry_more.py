import types
import importlib
import asyncio

import pytest

import app.providers.registry as registry
from app.providers.config import ProviderConfig


def test_persist_provider_config_fallback_to_file(tmp_path, monkeypatch):
    pid = "persist1"

    class Prov:
        def __init__(self):
            self.id = pid

        def update_state(self, data):
            raise RuntimeError("can't save")

    prov = Prov()
    old_active = registry.active_providers.copy()
    old_configs = registry.provider_configs.copy()
    try:
        registry.active_providers.clear()
        registry.provider_configs.clear()
        registry.active_providers[pid] = prov
        registry.provider_configs[pid] = ProviderConfig(provider_id=pid, data={"x": 1})

        # Simulate failure of provider.update_state and ensure fallback writing
        written = {"ok": False}

        def fake_write(path, data):
            written["ok"] = True
            return True

        # Patch registry's write_json_file reference and inspect.getfile to point into tmp
        monkeypatch.setattr(registry, "write_json_file", fake_write)
        monkeypatch.setattr(registry.inspect, "getfile", lambda cls: str(tmp_path / "mod.py"))

        res = registry.persist_provider_config(pid)
        assert res is True
        assert written["ok"] is True
    finally:
        registry.active_providers.clear()
        registry.active_providers.update(old_active)
        registry.provider_configs.clear()
        registry.provider_configs.update(old_configs)


def test_wrap_provider_normalizers_applies(monkeypatch):
    pid = "wrap1"

    class Prov:
        def __init__(self):
            self.id = pid

        def discover_accounts(self):
            return [{"id": "a"}]

    # fake normalizer
    def norm_accounts(items):
        return [{"normalized": True}]

    # ensure helpers expose normalize_accounts
    import app.providers.helpers as helpers
    monkeypatch.setattr(helpers, "normalize_accounts", norm_accounts, raising=False)

    prov = Prov()
    old_active = registry.active_providers.copy()
    try:
        registry.active_providers.clear()
        registry.add_provider(prov)
        p = registry.get_provider(pid)
        # discover_accounts was wrapped; it's async wrapper so run it
        res = asyncio.run(p.discover_accounts())
        assert isinstance(res, list)
        assert res and res[0].get("normalized") is True
    finally:
        registry.active_providers.clear()
        registry.active_providers.update(old_active)


def test_load_integrations_with_load_providers(monkeypatch):
    # Simulate a discovered integration package
    monkeypatch.setattr(registry, "_discover_integration_packages", lambda: {"fakepkg": "/tmp"})

    class FakeProv:
        def __init__(self):
            self.id = "from_load"

    fake_mod = types.SimpleNamespace()

    def load_providers():
        return {"from_load": FakeProv()}

    fake_mod.load_providers = load_providers

    real_import = importlib.import_module

    def fake_import(name, package=None):
        if name == "app.providers.fakepkg":
            return fake_mod
        return real_import(name, package=package)

    monkeypatch.setattr(importlib, "import_module", fake_import)

    old_active = registry.active_providers.copy()
    try:
        registry.active_providers.clear()
        registry.load_integrations()
        assert "from_load" in registry.active_providers
    finally:
        registry.active_providers.clear()
        registry.active_providers.update(old_active)
