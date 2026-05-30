import os
import asyncio
import inspect
import types
import pytest

from app.providers import registry
from app.providers.config import ProviderConfig


def test_add_provider_requires_id():
    class NoId:
        pass

    with pytest.raises(ValueError):
        registry.add_provider(NoId())


def test_persist_provider_config_calls_update_state(tmp_path):
    pid = "reg1"

    class Prov:
        def __init__(self):
            self.id = pid
            self.saved = False

        def update_state(self, data):
            # simulate persistence
            self.saved = True

    prov = Prov()
    old_active = registry.active_providers.copy()
    old_configs = registry.provider_configs.copy()
    try:
        registry.active_providers.clear()
        registry.provider_configs.clear()
        registry.active_providers[pid] = prov
        registry.provider_configs[pid] = ProviderConfig(provider_id=pid, data={"k": 1})

        res = registry.persist_provider_config(pid)
        assert res is True
        assert prov.saved is True
    finally:
        registry.active_providers.clear()
        registry.active_providers.update(old_active)
        registry.provider_configs.clear()
        registry.provider_configs.update(old_configs)


def test_persist_provider_config_writes_file_fallback(tmp_path, monkeypatch):
    pid = "reg2"

    class Prov2:
        def __init__(self, path):
            self.id = pid
            self.config_path = path

    path = tmp_path / "cfg.json"
    prov = Prov2(str(path))
    old_active = registry.active_providers.copy()
    old_configs = registry.provider_configs.copy()
    try:
        registry.active_providers.clear()
        registry.provider_configs.clear()
        registry.active_providers[pid] = prov
        registry.provider_configs[pid] = ProviderConfig(provider_id=pid, data={"x": 2})

        # should attempt to write file and return True
        res = registry.persist_provider_config(pid)
        assert res is True
        assert path.exists()
    finally:
        registry.active_providers.clear()
        registry.active_providers.update(old_active)
        registry.provider_configs.clear()
        registry.provider_configs.update(old_configs)


def test_start_and_stop_coordinators_with_factory(monkeypatch):
    pid = "reg-coord"

    class Prov:
        def __init__(self):
            self.id = pid
            self.coordinator = None

    prov = Prov()
    old_active = registry.active_providers.copy()
    try:
        registry.active_providers.clear()
        registry.active_providers[pid] = prov

        class FakeCoord:
            def __init__(self):
                self.started = False
                self.stopped = False
                self.is_running = False

            def start(self):
                self.started = True
                self.is_running = True

            async def stop(self):
                self.stopped = True
                self.is_running = False

        def factory(provider):
            return FakeCoord()

        # reload registry to bypass test autouse monkeypatch in conftest
        import importlib
        importlib.reload(registry)
        # re-register provider into reloaded registry
        registry.active_providers.clear()
        registry.active_providers[pid] = prov

        # start coordinators using factory
        registry.start_all_coordinators(coordinator_factory=factory)
        # provider should now have a coordinator
        coord = registry.active_providers[pid].coordinator
        assert coord is not None and coord.started is True

        # stop coordinators
        asyncio.run(registry.stop_all_coordinators())
        assert coord.stopped is True
    finally:
        registry.active_providers.clear()
        registry.active_providers.update(old_active)