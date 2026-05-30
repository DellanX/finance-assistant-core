import asyncio
from app.providers import registry


def test_execute_refresh_ok(client, mock_provider):
    pid = mock_provider.get("id")
    r = client.post(f"/api/v1/actions/refresh/execute", json={"entity_id": pid})
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    assert r.json()["result"] == "refreshed"


def test_execute_core_missing_entity_id(client):
    r = client.post(f"/api/v1/actions/refresh/execute", json={})
    assert r.status_code == 400


def test_execute_refresh_no_coordinator(client, mock_provider):
    pid = mock_provider.get("id")
    provider = registry.get_provider(pid)
    provider.coordinator = None
    r = client.post(f"/api/v1/actions/refresh/execute", json={"entity_id": pid})
    assert r.status_code == 400


def test_execute_refresh_async_coord(client, mock_provider):
    pid = mock_provider.get("id")
    provider = registry.get_provider(pid)

    async def async_refresh():
        await asyncio.sleep(0)
        return None

    provider.coordinator.refresh = async_refresh
    r = client.post(f"/api/v1/actions/refresh/execute", json={"entity_id": pid})
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_execute_refresh_raised_exception_sync_and_async(client, mock_provider):
    pid = mock_provider.get("id")
    prov = registry.get_provider(pid)

    def bad_refresh():
        raise RuntimeError("boom-sync")

    prov.coordinator.refresh = bad_refresh
    r = client.post(f"/api/v1/actions/refresh/execute", json={"entity_id": pid})
    assert r.status_code == 200
    assert r.json()["status"] == "error"
    assert "boom-sync" in r.json()["error"]

    async def abad():
        raise RuntimeError("boom-async")

    prov.coordinator.refresh = abad
    r = client.post(f"/api/v1/actions/refresh/execute", json={"entity_id": pid})
    assert r.status_code == 200
    assert r.json()["status"] == "error"
    assert "boom-async" in r.json()["error"]
