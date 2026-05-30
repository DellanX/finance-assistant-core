import asyncio
from app.providers import registry


def test_execute_force_reconcile_not_implemented(client, mock_provider):
    pid = mock_provider.get("id")
    r = client.post(f"/api/v1/actions/force_reconcile/execute", json={"entity_id": pid})
    assert r.status_code == 501


def test_execute_force_reconcile_sync_and_async(client, mock_provider):
    pid = mock_provider.get("id")
    provider = registry.get_provider(pid)

    provider.reconcile = lambda: "done"
    r = client.post(f"/api/v1/actions/force_reconcile/execute", json={"entity_id": pid})
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

    async def areconcile():
        await asyncio.sleep(0)
        return "async-done"

    provider.reconcile = areconcile
    r = client.post(f"/api/v1/actions/force_reconcile/execute", json={"entity_id": pid})
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
