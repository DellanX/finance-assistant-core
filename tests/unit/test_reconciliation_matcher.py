from app.reconciliation.matcher import find_duplicates, dedupe_transactions, apply_corrections


def _make_tx(tid, date, amount, payee=None):
    return {"id": tid, "date": date, "amount": amount, "payee": payee}


def test_find_duplicates_groups_similar_transactions():
    txs = [
        _make_tx("t1", "2026-05-01", 100.0, "Alice"),
        _make_tx("t2", "2026-05-01", 100.0, "alice  "),
        _make_tx("t3", "2026-05-02", 50.0, "Bob"),
    ]
    dups = find_duplicates(txs)
    assert len(dups) == 1
    group = next(iter(dups.values()))
    ids = {t["id"] for t in group}
    assert ids == {"t1", "t2"}


def test_dedupe_transactions_returns_canonical_and_duplicates():
    txs = [
        _make_tx("t1", "2026-05-01", 10.0, "Store"),
        _make_tx("t2", "2026-05-01", 10.0, "store"),
        _make_tx("t3", "2026-05-01", 5.0, "Other"),
    ]
    deduped, duplicates = dedupe_transactions(txs)
    assert len(deduped) == 2
    assert len(duplicates) == 1
    assert duplicates[0]["id"] == "t2"


def test_apply_corrections_updates_transactions_by_id():
    txs = [
        _make_tx("a", "2026-05-01", 1.0, "X"),
        _make_tx("b", "2026-05-02", 2.0, "Y"),
    ]
    corrections = [{"id": "b", "updates": {"amount": 2.5, "payee": "Y Corp"}}]
    res = apply_corrections(txs, corrections)
    m = {t["id"]: t for t in res}
    assert m["b"]["amount"] == 2.5
    assert m["b"]["payee"] == "Y Corp"
