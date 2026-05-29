from app.providers import normalizers


def test_normalize_transaction_basic():
    raw = {"id": "t1", "date": "2026-01-01", "amount": "12.34", "merchant": "Store", "status": "settled"}
    out = normalizers.normalize_transaction(raw)
    assert out.id == "t1"
    assert out.date == "2026-01-01"
    assert abs(out.amount - 12.34) < 1e-6
    assert out.merchant == "Store"
    assert out.status == "settled"


def test_normalize_transaction_missing_fields():
    raw = {"transaction_id": "txx", "value": None}
    out = normalizers.normalize_transaction(raw)
    assert out.id == "txx"
    assert out.date is None
    assert out.merchant is None
    assert out.status == "unknown"


def test_normalize_positions_and_types():
    raw_pos = [{"symbol": "BTC", "quantity": "0.5", "cost_basis": "30000", "current_price": 65000},
               {"ticker": "ETH", "qty": 4, "cost": 2000, "price": "3500"}]

    out = normalizers.normalize_positions(raw_pos)
    assert len(out) == 2
    btc = out[0]
    eth = out[1]
    assert btc.symbol == "BTC"
    assert abs(btc.quantity - 0.5) < 1e-9
    assert abs(btc.cost_basis - 30000.0) < 1e-6
    assert abs(btc.current_price - 65000.0) < 1e-6

    assert eth.symbol == "ETH"
    assert abs(eth.quantity - 4.0) < 1e-9
    assert abs(eth.current_price - 3500.0) < 1e-6
