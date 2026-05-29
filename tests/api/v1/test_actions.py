from fastapi.testclient import TestClient
import pytest

from app import main as app_main
from app.providers import registry


@pytest.fixture(autouse=True)
def client():
    with TestClient(app_main.app) as c:
        yield c


def test_list_actions_includes_core_and_integration(client, mock_provider):
    r = client.get("/api/v1/actions")
    assert r.status_code == 200
    data = r.json()
    ids = {a["id"] for a in data.get("actions", [])}
    assert "refresh" in ids
    assert "simulate_transfer" in ids


def test_execute_refresh_ok(client, mock_provider):
    pid = mock_provider.get("id")
    r = client.post(f"/api/v1/actions/refresh/execute", json={"entity_id": pid})
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    assert r.json()["result"] == "refreshed"


def test_execute_export_state_ok(client, mock_provider):
    pid = mock_provider.get("id")
    r = client.post(f"/api/v1/actions/export_state/execute", json={"entity_id": pid})
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    # result should be a dict (provider state)
    assert isinstance(r.json()["result"], dict)


def test_execute_force_reconcile_not_implemented(client, mock_provider):
    pid = mock_provider.get("id")
    r = client.post(f"/api/v1/actions/force_reconcile/execute", json={"entity_id": pid})
    assert r.status_code == 501


def test_execute_core_missing_entity_id(client):
    r = client.post(f"/api/v1/actions/refresh/execute", json={})
    assert r.status_code == 400


def test_execute_integration_action_success(client, mock_provider):
    pid = mock_provider.get("id")
    payload = {"entity_id": pid, "params": {"from_account": "a1", "to_account": "a2", "amount": 1}}
    r = client.post(f"/api/v1/actions/simulate_transfer/execute", json=payload)
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_execute_integration_action_failure(client, mock_provider):
    pid = mock_provider.get("id")
    payload = {"entity_id": pid, "params": {}}
    r = client.post(f"/api/v1/actions/simulate_failure/execute", json=payload)
    assert r.status_code == 200
    assert r.json()["status"] == "error"


def test_list_provider_actions_not_found(client):
    r = client.get("/api/v1/actions/providers/nonexistent")
    assert r.status_code == 404


def test_list_provider_actions_includes_defaults(client, mock_provider):
    pid = mock_provider.get("id")
    r = client.get(f"/api/v1/actions/providers/{pid}")
    assert r.status_code == 200
    data = r.json()
    ids = {a["id"] for a in data.get("actions", [])}
    assert "simulate_transfer" in ids


def test_moved_endpoints_return_410(client):
    r = client.get("/api/v1/actions/categories")
    assert r.status_code == 410
    r = client.get("/api/v1/actions/tags")
    assert r.status_code == 410


def test_execute_action_not_found(client, mock_provider):
    pid = mock_provider.get("id")
    r = client.post(f"/api/v1/actions/does_not_exist/execute", json={"entity_id": pid})
    assert r.status_code == 404


def test_execute_refresh_no_coordinator(client, mock_provider):
    # provider exists but has no coordinator -> 400
    from app.providers import registry
    pid = mock_provider.get("id")
    provider = registry.get_provider(pid)
    # remove coordinator
    provider.coordinator = None
    r = client.post(f"/api/v1/actions/refresh/execute", json={"entity_id": pid})
    assert r.status_code == 400


def test_execute_refresh_async_coord(client, mock_provider):
    # coordinator.refresh returns a coroutine
    import asyncio
    from app.providers import registry

    pid = mock_provider.get("id")
    provider = registry.get_provider(pid)

    async def async_refresh():
        await asyncio.sleep(0)
        return None

    provider.coordinator.refresh = async_refresh
    r = client.post(f"/api/v1/actions/refresh/execute", json={"entity_id": pid})
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_execute_export_state_missing_getter(client, mock_provider):
    from app.providers import registry
    pid = mock_provider.get("id")
    provider = registry.get_provider(pid)
    # make get_state non-callable to trigger the 400 branch
    provider.get_state = None
    r = client.post(f"/api/v1/actions/export_state/execute", json={"entity_id": pid})
    assert r.status_code == 400


def test_execute_force_reconcile_sync_and_async(client, mock_provider):
    import asyncio
    from app.providers import registry

    pid = mock_provider.get("id")
    provider = registry.get_provider(pid)

    # sync reconcile
    provider.reconcile = lambda: "done"
    r = client.post(f"/api/v1/actions/force_reconcile/execute", json={"entity_id": pid})
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

    # async reconcile
    async def areconcile():
        await asyncio.sleep(0)
        return "async-done"

    provider.reconcile = areconcile
    r = client.post(f"/api/v1/actions/force_reconcile/execute", json={"entity_id": pid})
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_integration_action_missing_entity_id(client):
    # integration-level action requires entity_id
    r = client.post(f"/api/v1/actions/simulate_transfer/execute", json={"params": {"a": 1}})
    assert r.status_code == 400


def test_integration_execute_action_async_exception(client, mock_provider):
    import asyncio
    from app.providers import registry

    pid = mock_provider.get("id")
    provider = registry.get_provider(pid)

    async def failing(action_id, params, dry_run=False):
        await asyncio.sleep(0)
        raise RuntimeError("boom")

    provider.execute_action = failing
    payload = {"entity_id": pid, "params": {"from_account": "a1", "to_account": "a2", "amount": 1}}
    r = client.post(f"/api/v1/actions/simulate_transfer/execute", json=payload)
    assert r.status_code == 200
    assert r.json()["status"] == "error"
