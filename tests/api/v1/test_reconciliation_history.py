from fastapi.testclient import TestClient
from app import main as app_main
from app import reconciliation
import time


def test_reconciliation_history_and_corrections():
    with TestClient(app_main.app) as client:
        # run a reconciliation
        payload = {"reconciler": "simple", "transactions": [{"id":"t1","date":"2026-05-01","amount":10},{"id":"t2","date":"2026-05-01","amount":10}]}
        r = client.post("/api/v1/reconciliation", json=payload)
        assert r.status_code == 200
        data = r.json()
        rid = data.get("reconciliation_id")
        assert rid

        # list history
        r2 = client.get("/api/v1/reconciliation/history")
        assert r2.status_code == 200
        hist = r2.json()
        ids = {h.get("reconciliation_id") for h in hist}
        assert rid in ids

        # get specific run
        r3 = client.get(f"/api/v1/reconciliation/history/{rid}")
        assert r3.status_code == 200
        rec = r3.json()
        assert rec.get("reconciliation_id") == rid

        # post a correction
        corr = {"id": "t2", "updates": {"amount": 12}}
        r4 = client.post(f"/api/v1/reconciliation/{rid}/corrections", json={"corrections": [corr]})
        assert r4.status_code == 200
        updated = r4.json()
        # ensure corrections recorded and transactions updated
        assert any(c.get("id") == "t2" for c in updated.get("corrections", []))
        txs = updated.get("transactions", [])
        assert any(tx.get("id") == "t2" and tx.get("amount") == 12 for tx in txs)

        # cleanup: remove persisted file(s)
        try:
            import shutil
            from pathlib import Path
            d = Path(reconciliation.store.DATA_DIR)
            if d.exists():
                shutil.rmtree(d)
        except Exception:
            pass
