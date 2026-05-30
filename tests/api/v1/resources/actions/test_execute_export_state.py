from app.providers import registry


def test_execute_export_state_ok(client, mock_provider):
    pid = mock_provider.get("id")
    r = client.post(f"/api/v1/actions/export_state/execute", json={"entity_id": pid})
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    assert isinstance(r.json()["result"], dict)


def test_execute_export_state_missing_getter(client, mock_provider):
    pid = mock_provider.get("id")
    provider = registry.get_provider(pid)
    provider.get_state = None
    r = client.post(f"/api/v1/actions/export_state/execute", json={"entity_id": pid})
    assert r.status_code == 400


def test_execute_export_state_async_getter(client, mock_provider):
    pid = mock_provider.get("id")
    prov = registry.get_provider(pid)

    async def aget():
        return {"x": 1}

    prov.get_state = aget
    r = client.post(f"/api/v1/actions/export_state/execute", json={"entity_id": pid})
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    assert r.json()["result"]["x"] == 1
