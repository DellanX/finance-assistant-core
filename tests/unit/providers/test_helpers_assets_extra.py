from app.providers.helpers.assets import normalize_asset, normalize_assets


def test_normalize_asset_with_ticker_and_bad_price():
    raw = {"ticker": "ETH", "price": "not-a-number"}
    model = normalize_asset(raw)
    assert model.symbol == "ETH"
    assert model.current_price == 0.0


def test_normalize_assets_empty():
    assert normalize_assets(None) == []
    assert normalize_assets([]) == []
