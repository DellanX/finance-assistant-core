from fastapi.testclient import TestClient
from app.main import app


def test_openapi_contains_pagination_params_for_list_endpoints():
    client = TestClient(app)
    res = client.get("/openapi.json")
    assert res.status_code == 200
    spec = res.json()

    paths_to_check = [
        "/api/v1/providers",
        "/api/v1/transactions",
        "/api/v1/ledgers",
        "/api/v1/providers/{id}/accounts",
        "/api/v1/categories",
        "/api/v1/tags",
        "/api/v1/labels",
        "/api/v1/actions",
        "/api/v1/tranches",
        "/api/v1/strategies",
        "/api/v1/snapshots",
    ]

    for path in paths_to_check:
        assert path in spec.get("paths", {}), f"{path} missing from OpenAPI spec"
        get_op = spec["paths"][path].get("get")
        assert get_op is not None, f"GET operation missing for {path}"
        params = get_op.get("parameters", [])
        names = {p.get("name") for p in params}
        assert "limit" in names, f"limit param missing for {path}"
        assert "cursor" in names, f"cursor param missing for {path}"
