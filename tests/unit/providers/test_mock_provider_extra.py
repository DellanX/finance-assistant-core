import sys
import types
import pytest
import asyncio

from app.providers.mock.provider import MockProvider


def make_provider(tmp_path):
    state_file = tmp_path / "mock_state.json"
    prov = MockProvider(str(state_file))
    return prov


def test_discover_accounts_returns_models(tmp_path):
    prov = make_provider(tmp_path)
    # ensure there is at least one account in state
    prov._state = {"accounts": [{"id": "a1", "name": "A", "type": "depository"}]}
    accounts = asyncio.run(prov.discover_accounts())
    assert isinstance(accounts, list)
    assert len(accounts) == 1
    item = accounts[0]
    # when NormalizedAccount present, provider wraps into a pydantic model
    assert hasattr(item, "model_dump") or hasattr(item, "dict")


def test_discover_accounts_falls_back_when_normalized_missing(tmp_path, monkeypatch):
    prov = make_provider(tmp_path)
    prov._state = {"accounts": [{"id": "b1", "name": "B", "type": "depository"}]}

    # inject a fake module without NormalizedAccount to force ImportError
    fake = types.ModuleType("app.core.schemas")
    monkeypatch.setitem(sys.modules, "app.core.schemas", fake)

    accounts = asyncio.run(prov.discover_accounts())
    assert isinstance(accounts, list)
    assert isinstance(accounts[0], dict)


def test_sync_transactions_normalizer_exception_returns_raw(tmp_path, monkeypatch):
    prov = make_provider(tmp_path)
    prov._state = {"transactions": {"acct": [{"id": "t1", "amount": 100}]}}

    # monkeypatch normalize_transactions to raise
    import app.providers.normalizers as normalizers

    def boom(items, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(normalizers, "normalize_transactions", boom)

    tx = asyncio.run(prov.sync_transactions({"id": "acct"}))
    assert isinstance(tx, list)
    assert tx[0]["id"] == "t1"


def test_sync_positions_normalizer_exception_returns_raw(tmp_path, monkeypatch):
    prov = make_provider(tmp_path)
    prov._state = {"positions": {"acct": [{"id": "p1", "qty": 5}]}}

    import app.providers.normalizers as normalizers

    def boom(items, **kwargs):
        raise RuntimeError("boompos")

    monkeypatch.setattr(normalizers, "normalize_positions", boom)

    pos = asyncio.run(prov.sync_positions({"id": "acct"}))
    assert isinstance(pos, list)
    assert pos[0]["id"] == "p1"
