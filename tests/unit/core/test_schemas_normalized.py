from app.providers.normalizers import normalize_transaction, normalize_position
from app.core.schemas import NormalizedTransaction, NormalizedPosition


def test_normalized_transaction_model():
    raw = {"id": "tx1", "date": "2026-01-01", "amount": "10.5", "merchant": "Shop"}
    d = normalize_transaction(raw)
    if hasattr(d, "model_dump"):
        dd = d.model_dump()
    else:
        dd = d
    model = NormalizedTransaction(**{k: dd[k] for k in dd if k in NormalizedTransaction.model_fields})
    assert model.id == "tx1"
    assert model.amount == 10.5


def test_normalized_position_model():
    raw = {"symbol": "BTC", "quantity": "0.5", "cost_basis": "30000", "current_price": "65000"}
    d = normalize_position(raw)
    if hasattr(d, "model_dump"):
        dd = d.model_dump()
    else:
        dd = d
    model = NormalizedPosition(**{k: dd[k] for k in dd if k in NormalizedPosition.model_fields})
    assert model.symbol == "BTC"
    assert model.quantity == 0.5
