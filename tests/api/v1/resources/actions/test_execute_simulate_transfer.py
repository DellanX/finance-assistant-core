import importlib
from app.providers import registry


def test_execute_integration_simulate_transfer_success(client, mock_provider):
    pid = mock_provider.get("id")
    payload = {"entity_id": pid, "params": {"from_account": "a1", "to_account": "a2", "amount": 1}}
    r = client.post(f"/api/v1/actions/simulate_transfer/execute", json=payload)
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_execute_integration_simulate_transfer_failure(client, mock_provider):
    pid = mock_provider.get("id")
    payload = {"entity_id": pid, "params": {}}
    r = client.post(f"/api/v1/actions/simulate_failure/execute", json=payload)
    assert r.status_code == 200
    assert r.json()["status"] == "error"


def test_integration_action_missing_entity_id(client):
    r = client.post(f"/api/v1/actions/simulate_transfer/execute", json={"params": {"a": 1}})
    assert r.status_code == 400


def test_integration_execute_action_async_exception(client, mock_provider):
    import asyncio
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


def test_execute_integration_action_sync_and_async(client, monkeypatch, mock_provider):
    pid = mock_provider.get("id")
    prov = registry.get_provider(pid)

    def sync_exec(action, params, dry_run=False):
        return {"ok": "sync"}

    prov.execute_action = sync_exec
    payload = {"entity_id": pid, "params": {"from_account": "a1", "to_account": "a2", "amount": 1}}
    r = client.post("/api/v1/actions/simulate_transfer/execute", json=payload)
    assert r.status_code == 200
    assert r.json().get("status") == "ok"

    async def async_exec(action, params, dry_run=False):
        return {"ok": "async"}

    prov.execute_action = async_exec
    r = client.post("/api/v1/actions/simulate_transfer/execute", json=payload)
    assert r.status_code == 200
    assert r.json().get("status") == "ok"
