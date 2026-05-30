import json
import os
import asyncio
import tempfile
import pytest

from app.providers.mock.provider import MockProvider
from app.providers.config import ProviderConfig
from app.providers import registry


def make_state(tmp_path, pid="mock_test", accounts=None, transactions=None, positions=None):
    data = {
        "id": pid,
        "name": f"Mock {pid}",
        "config": {},
        "accounts": accounts or [],
        "transactions": transactions or {},
        "positions": positions or {},
    }
    path = tmp_path / f"{pid}.json"
    with open(path, "w") as f:
        json.dump(data, f)
    return str(path), data


def test_load_state_missing_file():
    # Pass a non-existent path
    p = MockProvider(config_path="/nonexistent/path.json")
    # _load_state returns an 'error' id when file missing
    assert p.id == "error"
    assert isinstance(p.get_state(), dict)


def test_get_and_update_state_and_persistence(tmp_path):
    path, state = make_state(tmp_path, pid="m1", accounts=[{"id": "a1", "balance": 10.0}])
    p = MockProvider(config_path=path)
    assert p.get_state()["id"] == "m1"

    # update state and ensure file is updated
    p.update_state({"name": "Renamed", "newkey": 123})
    with open(path, "r") as f:
        on_disk = json.load(f)
    assert on_disk["name"] == "Renamed"
    assert on_disk["newkey"] == 123


def test_discover_accounts_hides_balance_when_disabled(tmp_path):
    path, state = make_state(tmp_path, pid="m2", accounts=[{"id": "a1", "balance": 50}])
    p = MockProvider(config_path=path)
    # register provider config disabling balances
    cfg = ProviderConfig(provider_id=p.id, data={"enable_balances": False})
    registry.provider_configs[p.id] = cfg

    res = asyncio.run(p.discover_accounts())
    assert isinstance(res, list)
    assert "balance" not in res[0]


def test_sync_transactions_disabled_and_normalization(tmp_path, monkeypatch):
    path, state = make_state(tmp_path, pid="m3", transactions={"a1": [{"id": "t1", "amount": 5}]})
    p = MockProvider(config_path=path)
    # disable transactions
    registry.provider_configs[p.id] = ProviderConfig(provider_id=p.id, data={"enable_transactions": False})
    res = asyncio.run(p.sync_transactions({"id": "a1"}))
    assert res == []

    # enable and monkeypatch normalizer to ensure branch
    registry.provider_configs[p.id] = ProviderConfig(provider_id=p.id, data={"enable_transactions": True})

    def fake_normalize(raw):
        return [{"normalized": True}]

    monkeypatch.setitem(__import__("app.providers.normalizers", fromlist=["normalize_transactions"]).__dict__, "normalize_transactions", fake_normalize)
    res2 = asyncio.run(p.sync_transactions({"id": "a1"}))
    assert res2 == [{"normalized": True}]


def test_sync_positions_disabled_and_normalization(tmp_path, monkeypatch):
    path, state = make_state(tmp_path, pid="m4", positions={"a1": [{"symbol": "X", "quantity": 1}]})
    p = MockProvider(config_path=path)
    registry.provider_configs[p.id] = ProviderConfig(provider_id=p.id, data={"enable_balances": False})
    res = asyncio.run(p.sync_positions({"id": "a1"}))
    assert res == []

    registry.provider_configs[p.id] = ProviderConfig(provider_id=p.id, data={"enable_balances": True})

    def fake_norm(raw):
        return [{"symbol": "NORM"}]

    monkeypatch.setitem(__import__("app.providers.normalizers", fromlist=["normalize_positions"]).__dict__, "normalize_positions", fake_norm)
    res2 = asyncio.run(p.sync_positions({"id": "a1"}))
    assert res2 == [{"symbol": "NORM"}]


def test_actions_and_execute_behavior(tmp_path):
    path, state = make_state(tmp_path, pid="m5")
    p = MockProvider(config_path=path)
    defs = asyncio.run(p.get_action_definitions())
    ids = [d.get("id") for d in defs]
    assert "simulate_transfer" in ids and "simulate_failure" in ids

    act = asyncio.run(p.list_actions())
    assert "simulate_transfer" in act

    res = asyncio.run(p.execute_action("simulate_transfer", {}))
    assert res.get("status") == "success"

    with pytest.raises(Exception):
        asyncio.run(p.execute_action("simulate_failure", {}))


def teardown_function(func):
    # clean registry entries created during tests
    try:
        for k in list(registry.provider_configs.keys()):
            if k.startswith("m"):
                del registry.provider_configs[k]
    except Exception:
        pass