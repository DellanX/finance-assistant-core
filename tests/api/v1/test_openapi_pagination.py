from fastapi.testclient import TestClient
from app import main as app_main


def test_openapi_includes_pagination_params_for_providers():
    with TestClient(app_main.app) as client:
        r = client.get("/openapi.json")
        assert r.status_code == 200
        spec = r.json()
        path = spec.get("paths", {}).get("/api/v1/providers")
        assert path is not None
        get_op = path.get("get")
        assert get_op is not None
        params = [p.get("name") for p in get_op.get("parameters", [])]
        # ensure cursor and limit params documented
        assert "cursor" in params or "limit" in params
