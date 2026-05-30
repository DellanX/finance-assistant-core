import json
import asyncio
from pathlib import Path

import pytest

from app.providers.mock.provider import MockProvider


def test_load_state_missing_file(tmp_path):
    p = tmp_path / "missing.json"
    mp = MockProvider(config_path=str(p))
    state = mp.get_state()
    assert state.get("id") == "error"


def test_update_state_writes_file(tmp_path):
    src = tmp_path / "state.json"
    src.write_text(json.dumps({"id": "m1", "name": "mock", "accounts": []}))
    mp = MockProvider(config_path=str(src))
    # update and ensure file changed
    mp.update_state({"name": "changed", "extra": 1})
    data = json.loads(src.read_text())
    assert data.get("name") == "changed"
    assert data.get("extra") == 1


def test_discover_accounts_respects_enable_balances(tmp_path):
    src = tmp_path / "state2.json"
    state = {"id": "m2", "accounts": [{"id": "a1", "balance": 100}], "config": {"enable_balances": False}}
    src.write_text(json.dumps(state))
    mp = MockProvider(config_path=str(src))

    accounts = asyncio.run(mp.discover_accounts())
    assert isinstance(accounts, list)
    assert "balance" not in accounts[0]


def test_sync_transactions_disabled(tmp_path):
    src = tmp_path / "state3.json"
    state = {"id": "m3", "transactions": {"a1": [{"id": "t1"}]}, "config": {"enable_transactions": False}}
    src.write_text(json.dumps(state))
    mp = MockProvider(config_path=str(src))

    res = asyncio.run(mp.sync_transactions({"id": "a1"}))
    assert res == []


def test_sync_transactions_normalizer_exception_returns_raw(tmp_path, monkeypatch):
    src = tmp_path / "state4.json"
    state = {"id": "m4", "transactions": {"a1": [{"id": "t1"}]}, "config": {"enable_transactions": True}}
    src.write_text(json.dumps(state))
    mp = MockProvider(config_path=str(src))

    # monkeypatch normalize_transactions to raise
    import app.providers.normalizers as norms

    def _bad(raw):
        raise RuntimeError("bad")

    monkeypatch.setattr(norms, "normalize_transactions", _bad)

    res = asyncio.run(mp.sync_transactions({"id": "a1"}))
    assert isinstance(res, list)
    assert res and res[0].get("id") == "t1"
