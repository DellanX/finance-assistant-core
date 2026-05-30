def test_execute_simulate_failure_returns_error(client, mock_provider):
    pid = mock_provider.get("id")
    payload = {"entity_id": pid, "params": {}}
    r = client.post(f"/api/v1/actions/simulate_failure/execute", json=payload)
    assert r.status_code == 200
    assert r.json()["status"] == "error"
