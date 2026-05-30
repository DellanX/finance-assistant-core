import types
import importlib
from pathlib import Path

from fastapi.testclient import TestClient

from app import main as app_main
import app.providers.registry as registry


def test_create_provider_uses_integration_factory(monkeypatch, tmp_path):
    # Prepare a fake module with create_provider
    class FakeProvider:
        def __init__(self, pid=None, name=None, config_path=None):
            self.id = pid or "factory1"
            self.name = name or "factory"

    fake_mod = types.SimpleNamespace()

    def create_provider(cfg, provider_id=None, name=None):
        return FakeProvider(provider_id or "factory1", name=name)

    fake_mod.create_provider = create_provider

    real_import = importlib.import_module

    def _fake_import(name, package=None):
        if name == "app.providers.mock":
            return fake_mod
        return real_import(name, package=package)

    monkeypatch.setattr(importlib, "import_module", _fake_import)

    with TestClient(app_main.app) as client:
        r = client.post("/api/v1/providers", json={"integration": "mock", "name": "FromFactory", "config": {}})
        assert r.status_code == 200
        data = r.json()
        pid = data.get("id")
        assert pid is not None
        # cleanup
        registry.active_providers.pop(pid, None)
        registry.provider_configs.pop(pid, None)


def test_create_provider_no_provider_class_raises_500(monkeypatch):
    # Ensure that when provider class cannot be found, a 500 is returned
    real_import = importlib.import_module

    def _fake_import(name, package=None):
        if name == "app.providers.mock":
            return real_import(name)
        if name == "app.providers.mock.provider":
            # return an empty module with no classes
            return types.ModuleType("fake_provider_mod")
        return real_import(name, package=package)

    monkeypatch.setattr(importlib, "import_module", _fake_import)

    with TestClient(app_main.app) as client:
        r = client.post("/api/v1/providers", json={"integration": "mock", "name": "BadProvider", "config": {}})
        assert r.status_code == 500


def test_create_provider_constructor_fallbacks(monkeypatch, tmp_path):
    # Simulate ProviderClass that raises TypeError when called with config_path,
    # but works when called with no args.
    from app.providers.base import BaseProvider

    class WeirdProvider(BaseProvider):
        def __init__(self, *args, **kwargs):
            # if config_path provided, simulate TypeError for first signature
            if args or "config_path" in kwargs:
                raise TypeError("bad signature")
            self.id = "weird1"
            self.name = "weird"

        async def discover_accounts(self):
            return []

        async def sync_transactions(self, account, since):
            return []

        async def sync_positions(self, account):
            return []

        async def list_actions(self):
            return []

        async def execute_action(self, action_name: str, payload: dict, dry_run: bool = False):
            return {}

        async def match_transaction(self, optimistic_tx, provider_tx):
            return True

    provider_mod = types.ModuleType("fake_provider_mod")
    provider_mod.WeirdProvider = WeirdProvider

    real_import = importlib.import_module

    def _fake_import(name, package=None):
        if name == "app.providers.mock":
            return real_import(name)
        if name == "app.providers.mock.provider":
            return provider_mod
        return real_import(name, package=package)

    monkeypatch.setattr(importlib, "import_module", _fake_import)

    # call create provider; it should create a file and instantiate via fallback
    with TestClient(app_main.app) as client:
        r = client.post("/api/v1/providers", json={"integration": "mock", "name": "Weird", "config": {}})
        assert r.status_code == 200
        pid = r.json().get("id")
        # ensure file exists in mock_data
        providers_dir = Path(__file__).resolve().parents[3] / "app" / "providers" / "mock" / "mock_data"
        target = providers_dir / f"{pid}.json"
        assert target.exists()
        # cleanup
        registry.active_providers.pop(pid, None)
        registry.provider_configs.pop(pid, None)
        try:
            target.unlink()
        except Exception:
            pass
