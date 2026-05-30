import asyncio
import pytest

import importlib
from app.providers import registry
from app.providers.coordinator import TestCoordinator


@pytest.fixture(autouse=True)
def clear_registry():
    # snapshot and clear global registries for test isolation
    orig_active = dict(registry.active_providers)
    orig_configs = dict(registry.provider_configs)
    registry.active_providers.clear()
    registry.provider_configs.clear()
    try:
        yield
    finally:
        registry.active_providers.clear()
        registry.active_providers.update(orig_active)
        registry.provider_configs.clear()
        registry.provider_configs.update(orig_configs)


def test_start_all_coordinators_injects_factory():
    # reload registry to avoid test-suite monkeypatching in conftest
    importlib.reload(registry)
    class FakeProvider:
        pass

    p = FakeProvider()
    p.id = "p1"
    registry.active_providers[p.id] = p

    def factory(provider):
        return TestCoordinator()

    registry.start_all_coordinators(coordinator_factory=factory)

    assert hasattr(p, "coordinator")
    assert isinstance(p.coordinator, TestCoordinator)
    assert p.coordinator.is_running is True


def test_start_calls_existing_coordinator_start():
    importlib.reload(registry)

    class C:
        def __init__(self):
            self.started = False

        def start(self):
            self.started = True

        async def stop(self):
            self.started = False

    provider = type("P", (), {"id": "p2"})()
    provider.coordinator = C()
    registry.active_providers[provider.id] = provider

    registry.start_all_coordinators()

    assert provider.coordinator.started is True


def test_stop_all_coordinators_awaits_stop():
    importlib.reload(registry)

    class AsyncCoord:
        def __init__(self):
            self.is_running = True

        async def stop(self):
            # emulate async cleanup
            await asyncio.sleep(0)
            self.is_running = False

    provider = type("P", (), {"id": "p3"})()
    provider.coordinator = AsyncCoord()
    registry.active_providers[provider.id] = provider

    asyncio.run(registry.stop_all_coordinators())

    assert provider.coordinator.is_running is False


def test_coordinator_statuses_reports_running_and_missing():
    # provider with no coordinator
    p1 = type("P1", (), {"id": "p4"})()
    registry.active_providers[p1.id] = p1

    # provider with running coordinator
    p2 = type("P2", (), {"id": "p5"})()
    coord = TestCoordinator()
    p2.coordinator = coord
    registry.active_providers[p2.id] = p2

    # start the coord to mark it running
    coord.start()

    statuses = registry.coordinator_statuses()
    assert statuses[p1.id]["has_coordinator"] is False
    assert statuses[p2.id]["has_coordinator"] is True
    assert statuses[p2.id]["is_running"] is True
