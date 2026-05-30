from app.reconciliation.base import load_plugins, list_reconcilers, get_reconciler


def test_load_plugins_and_instantiate():
    # ensure plugins are loaded and the sample 'simple' reconciler is available
    load_plugins()
    names = list_reconcilers()
    assert "simple" in names

    cls = get_reconciler("simple")
    assert cls is not None
    inst = cls()
    txs = [
        {"id": "t1", "date": "2026-05-01", "amount": 100, "payee": "A"},
        {"id": "t2", "date": "2026-05-01", "amount": 100, "payee": "A"},
    ]
    res = inst.reconcile(txs)
    assert "reconciliation_id" in res
    assert "duplicates" in res
    assert res.get("reconciler") == "simple"
