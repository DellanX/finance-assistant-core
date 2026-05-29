import os
from app.providers import registry


def test_create_and_delete_mock_provider(client, tmp_path):
    payload = {
        "integration": "mock",
        "name": "api-test-mock",
        "config": {
            "accounts": [],
            "transactions": {},
            "positions": {}
        }
    }

    res = client.post("/api/v1/providers", json=payload)
    assert res.status_code == 200
    body = res.json()
    assert "id" in body
    pid = body["id"]
    assert body.get("integration") == "mock"

    # Provider should be registered
    provider = registry.get_provider(pid)
    assert provider is not None

    # Ensure config file exists on disk
    ppath = getattr(provider, "config_path", None)
    assert ppath is not None and os.path.exists(ppath)

    # Delete the provider via API
    del_res = client.delete(f"/api/v1/providers/{pid}")
    assert del_res.status_code == 204

    # Provider should be removed from registry
    assert registry.get_provider(pid) is None

    # Config file should be removed
    if ppath and os.path.exists(ppath):
        os.remove(ppath)
