import json
from pathlib import Path

from app.providers.config import ProviderConfig
import app.providers.registry as registry
from app.providers.registry import persist_provider_config


class DummyProvider:
    def __init__(self, pid, config_path=None, should_fail=False):
        self.id = pid
        self.config_path = config_path
        self._saved = None
        self._should_fail = should_fail

    def update_state(self, data):
        if self._should_fail:
            raise RuntimeError("fail")
        self._saved = data


def test_persist_no_config_returns_false():
    # ensure no config present
    import app.providers.registry as registry
    registry.provider_configs.clear()
    assert persist_provider_config("nonexistent") is False


def test_persist_calls_update_state(tmp_path):
    # ensure clean registry
    registry.active_providers.clear()
    registry.provider_configs.clear()
    pid = "p1"
    prov = DummyProvider(pid)
    registry.active_providers[pid] = prov
    cfg = ProviderConfig(provider_id=pid, data={"a": 1})
    registry.register_provider_config(cfg)

    ok = persist_provider_config(pid)
    assert ok is True
    assert prov._saved == {"a": 1}


def test_persist_writes_config_path_on_failure(tmp_path):
    # ensure clean registry
    registry.active_providers.clear()
    registry.provider_configs.clear()

    pid = "p2"
    path = tmp_path / "cfg.json"
    prov = DummyProvider(pid, config_path=str(path), should_fail=True)
    registry.active_providers[pid] = prov
    cfg = ProviderConfig(provider_id=pid, data={"x": 2})
    registry.register_provider_config(cfg)

    # update_state will fail, but persist should write to config_path
    ok = persist_provider_config(pid)
    assert ok is True
    assert path.exists()
    data = json.loads(path.read_text())
    assert data.get("x") == 2
