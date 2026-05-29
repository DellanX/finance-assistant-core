import asyncio
import shutil
import json
from pathlib import Path

from app.providers.mock.provider import MockProvider


def _make_state_copy(tmp_path, fixture_name="volatile_crypto.json"):
    src = Path("/workspace/app/providers/mock/mock_data") / fixture_name
    dest = tmp_path / "state.json"
    shutil.copy(src, dest)
    # ensure unique provider id to avoid colliding with registry-loaded fixtures
    data = json.loads(dest.read_text())
    data["id"] = f"test_mock_{tmp_path.name}"
    dest.write_text(json.dumps(data))
    return str(dest)


def test_mock_provider_discover_accounts_respects_balance_flag(tmp_path):
    ppath = _make_state_copy(tmp_path)
    provider = MockProvider(config_path=ppath)

    # default config enable_balances True -> accounts include balance
    accounts = asyncio.run(provider.discover_accounts())
    assert any("balance" in a for a in [a if isinstance(a, dict) else a.model_dump() for a in accounts])

    # toggle config to disable balances
    state = provider.get_state()
    state.setdefault("config", {})["enable_balances"] = False
    provider.update_state(state)
    accounts2 = asyncio.run(provider.discover_accounts())
    assert all("balance" not in (a if isinstance(a, dict) else a.model_dump()) for a in accounts2)


def test_mock_provider_sync_transactions_disabled(tmp_path):
    ppath = _make_state_copy(tmp_path)
    provider = MockProvider(config_path=ppath)
    state = provider.get_state()
    state.setdefault("config", {})["enable_transactions"] = False
    provider.update_state(state)

    # pick an account id from state
    acct = state.get("accounts", [])[0]
    res = asyncio.run(provider.sync_transactions(acct))
    assert res == []


def test_mock_execute_actions(tmp_path):
    ppath = _make_state_copy(tmp_path)
    provider = MockProvider(config_path=ppath)

    ok = asyncio.run(provider.execute_action("simulate_transfer", {}, dry_run=False))
    assert isinstance(ok, dict)

    try:
        asyncio.run(provider.execute_action("simulate_failure", {}, dry_run=False))
    except Exception as e:
        assert "Simulated failure" in str(e)
