from fastapi.testclient import TestClient

from app import main as app_main


def test_config_and_schema_routes_resolve_before_dynamic_id():
    with TestClient(app_main.app) as client:
        # static schema route should respond with 410 (deprecated)
        r = client.get("/api/v1/providers/schemas")
        assert r.status_code == 410

        # requesting config for a non-existent provider should return 404
        r2 = client.get("/api/v1/providers/no-such-provider/config")
        assert r2.status_code == 404
