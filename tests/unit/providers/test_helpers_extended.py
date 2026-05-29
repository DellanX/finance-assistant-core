from app.providers.helpers import (
    normalize_account,
    normalize_accounts,
    normalize_asset,
    normalize_assets,
    normalize_ledger,
    normalize_ledgers,
    normalize_tranche,
    normalize_tranches,
)


def test_normalize_account():
    raw = {"id": "a1", "name": "Main", "type": "depository", "balance": "1000"}
    model = normalize_account(raw)
    assert model.id == "a1"
    assert model.balance == 1000.0


def test_normalize_accounts():
    raw = [{"id": "a1"}, {"id": "a2", "balance": 50}]
    res = normalize_accounts(raw)
    assert len(res) == 2


def test_normalize_asset():
    raw = {"symbol": "BTC", "name": "Bitcoin", "price": "65000", "currency": "USD"}
    model = normalize_asset(raw)
    assert model.symbol == "BTC"
    assert model.current_price == 65000.0


def test_normalize_ledgers():
    raw = [{"id": "l1", "balance": "500"}]
    res = normalize_ledgers(raw)
    assert res[0].id == "l1"
    assert res[0].balance == 500.0


def test_normalize_tranches():
    raw = [{"id": "t1", "total_amount": "2500"}]
    res = normalize_tranches(raw)
    assert res[0].total_amount == 2500.0
