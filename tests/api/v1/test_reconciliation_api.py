from fastapi.testclient import TestClient
from app import main as app_main


def test_list_reconcilers():
    with TestClient(app_main.app) as client:
        r = client.get("/api/v1/reconciliation")
        assert r.status_code == 200
        data = r.json()
        assert "reconcilers" in data and isinstance(data["reconcilers"], list)
        assert "simple" in data["reconcilers"]


def test_run_simple_reconciler():
    with TestClient(app_main.app) as client:
        payload = {"reconciler": "simple", "transactions": [{"id":"t1","date":"2026-05-01","amount":10},{"id":"t2","date":"2026-05-01","amount":10}]}
        r = client.post("/api/v1/reconciliation", json=payload)
        assert r.status_code == 200
        data = r.json()
        assert data.get("reconciler") == "simple"
        assert "reconciliation_id" in data
        assert "duplicates" in data
