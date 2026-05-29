import asyncio
import json
from pathlib import Path

from app.providers import registry
from app.providers.config import ProviderConfig


class FakeCoordinator:
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


class DummyProvider:
    def __init__(self, pid, config_path):
        self.id = pid
        self.config_path = config_path
        self.coordinator = FakeCoordinator()

    def update_state(self, data):
        # write data to config_path as JSON
        Path(self.config_path).write_text(json.dumps(data))


def test_persist_provider_config(tmp_path):
    pid = "test_dummy"
    cfg_path = tmp_path / "cfg.json"
    provider = DummyProvider(pid, str(cfg_path))
    registry.add_provider(provider)

    cfg = ProviderConfig(provider_id=pid, data={"a": 1, "b": "x"})
    registry.register_provider_config(cfg)

    ok = registry.persist_provider_config(pid)
    assert ok is True
    assert cfg_path.exists()
    content = json.loads(cfg_path.read_text())
    assert content.get("a") == 1


def test_coordinator_lifecycle(tmp_path):
    import importlib

    # Reload registry module to avoid the test autouse monkeypatch which no-ops starts
    reg = importlib.reload(registry)

    pid = "coord_dummy"
    provider = DummyProvider(pid, str(tmp_path / "nope.json"))
    reg.add_provider(provider)

    # start coordinators should call start()
    reg.start_all_coordinators()
    coord = provider.coordinator
    assert coord.started is True
    assert coord.is_running is True

    # stop_all_coordinators should call stop() (async)
    asyncio.run(reg.stop_all_coordinators())
    assert coord.stopped is True
    assert coord.is_running is False
