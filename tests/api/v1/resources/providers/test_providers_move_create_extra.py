import importlib
import types
import uuid

from app.api.v1 import providers as prov_api
from app.api.v1.types import ProviderCreateRequest
from app.providers import registry


def test_create_provider_with_integration_factory(monkeypatch):
    integration = "fakeint"
    # expose integration as available
    monkeypatch.setattr(registry, "list_integration_packages", lambda: [integration])

    class FakeProvider:
        def __init__(self):
            self.id = "fp1"
            self.name = "Fake Provider"

    def create_provider(cfg, provider_id=None, name=None):
        return FakeProvider()

    fake_mod = types.ModuleType("app.providers.fakeint")
    fake_mod.create_provider = create_provider

    real_import = importlib.import_module

    def fake_import(name, package=None):
        if name == f"app.providers.{integration}":
            return fake_mod
        return real_import(name)

    monkeypatch.setattr(importlib, "import_module", fake_import)

    payload = ProviderCreateRequest(integration=integration, id=None, name="FP", config={})
    res = prov_api.create_provider(payload)
    assert res.id == "fp1"
    assert res.integration == integration
    # cleanup registry
    if "fp1" in registry.active_providers:
        del registry.active_providers["fp1"]


def test_create_provider_mock_constructor_fallback(monkeypatch, tmp_path):
    # Ensure 'mock' is discoverable
    monkeypatch.setattr(registry, "list_integration_packages", lambda: ["mock"])

    # Create a fake provider class that fails first two constructor forms
    class WeirdProvider:
        def __init__(self, *args, **kwargs):
            # succeed only if provider_id in kwargs
            if "provider_id" in kwargs:
                self.id = kwargs.get("provider_id")
                self.name = kwargs.get("name")
                self.config_path = kwargs.get("config_path")
                return
            # If called with single arg string, simulate TypeError
            if len(args) == 1 and isinstance(args[0], str):
                raise TypeError("bad signature")
            # If called with no args, simulate TypeError
            if len(args) == 0:
                raise TypeError("no-arg bad")

    # Patch provider module import to return our class under MockProvider
    fake_provider_mod = types.ModuleType("app.providers.mock.provider")
    fake_provider_mod.MockProvider = WeirdProvider

    real_import = importlib.import_module

    def fake_import(name, package=None):
        if name == "app.providers.mock.provider":
            return fake_provider_mod
        return real_import(name)

    monkeypatch.setattr(importlib, "import_module", fake_import)

    # Call create_provider with mock integration
    payload = ProviderCreateRequest(integration="mock", id=None, name="WP", config={})
    res = prov_api.create_provider(payload)
    # provider id should be present
    assert res.integration == "mock"
    assert res.id is not None
    # cleanup registry
    if res.id in registry.active_providers:
        del registry.active_providers[res.id]
