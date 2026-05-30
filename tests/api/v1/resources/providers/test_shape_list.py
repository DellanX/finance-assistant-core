from fastapi.testclient import TestClient
from app import main as app_main
from app.providers import registry
from app.api.v1.types import ProviderListItem


def test_providers_shape_no_pagination():
    # Ensure at least one provider exists
    old = registry.active_providers.copy()
    try:
        registry.active_providers.clear()
        # add two simple providers
        class P:
            def __init__(self, pid, name=None):
                self.id = pid
                self.name = name or pid

        registry.active_providers["p1"] = P("p1", "One")
        registry.active_providers["p2"] = P("p2", "Two")

        with TestClient(app_main.app) as client:
            r = client.get("/api/v1/providers")
            assert r.status_code == 200
            data = r.json()
            # envelope checks
            assert isinstance(data, dict)
            assert "providers" in data and isinstance(data["providers"], list)
            assert "total" in data and "limit" in data and "offset" in data
            assert "next_cursor" in data and "prev_cursor" in data

            # validate items against ProviderListItem model
            for it in data["providers"]:
                ProviderListItem(**it)
    finally:
        registry.active_providers.clear()
        registry.active_providers.update(old)


def test_providers_shape_with_pagination():
    old = registry.active_providers.copy()
    try:
        registry.active_providers.clear()
        # add 3 providers
        class P:
            def __init__(self, pid, name=None):
                self.id = pid
                self.name = name or pid

        for i in range(3):
            pid = f"pp{i}"
            registry.active_providers[pid] = P(pid, name=pid)

        with TestClient(app_main.app) as client:
            r = client.get("/api/v1/providers?limit=1")
            assert r.status_code == 200
            data = r.json()
            assert isinstance(data, dict)
            assert data.get("limit") == 1
            assert isinstance(data.get("providers"), list)
            # items length should be <= limit
            assert len(data.get("providers")) <= 1
            # cursors present
            assert data.get("next_cursor") is not None
    finally:
        registry.active_providers.clear()
        registry.active_providers.update(old)
