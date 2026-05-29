from fastapi.testclient import TestClient
import pytest
from app import main as app_main
from app.providers import registry
from app.providers.mock.provider import MockProvider
import shutil
from pathlib import Path


@pytest.fixture(autouse=True)
def noop_registry_start_stop(monkeypatch):
    """Prevent real coordinators from starting/stopping during tests."""
    # No-op the startup/shutdown hooks that would start coordinators
    monkeypatch.setattr(registry, "start_all_coordinators", lambda: None)

    async def _noop_stop():
        return None

    monkeypatch.setattr(registry, "stop_all_coordinators", _noop_stop)
    yield


@pytest.fixture
def client():
    """TestClient for the FastAPI app."""
    with TestClient(app_main.app) as client:
        yield client


@pytest.fixture
def mock_provider(tmp_path):
    """Register a temporary MockProvider using the volatile_crypto fixture copy."""
    src = Path("/workspace/app/providers/mock/mock_data/volatile_crypto.json")
    dest = tmp_path / "volatile_copy.json"
    shutil.copy(src, dest)
    provider = MockProvider(config_path=str(dest))
    # register in registry
    registry.add_provider(provider)
    try:
        yield provider.get_state()
    finally:
        # cleanup
        try:
            del registry.active_providers[provider.id]
        except Exception:
            pass
        try:
            del registry.provider_configs[provider.id]
        except Exception:
            pass
