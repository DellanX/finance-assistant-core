from app.reconciliation.core import reconcile_transactions


def test_reconcile_transactions_returns_payload():
    txs = [{"id": "t1", "amount": 100}, {"id": "t2", "amount": -50}]
    res = reconcile_transactions(txs)
    assert "reconciliation_id" in res
    assert isinstance(res["transactions"], list)
    assert len(res["transactions"]) == 2
