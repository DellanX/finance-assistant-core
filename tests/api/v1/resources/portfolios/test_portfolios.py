from app.providers import registry
import pytest


class PydanticLike:
    def __init__(self, data):
        self._data = data

    def model_dump(self):
        return self._data


class IterablePairs:
    def __init__(self, data):
        self._data = data

    def __iter__(self):
        return iter(self._data.items())


def make_provider(accounts, positions_map, name="PF"):
    class Prov:
        def __init__(self):
            self.name = name

        async def discover_accounts(self):
            return accounts

        async def sync_positions(self, acc):
            try:
                if hasattr(acc, "model_dump"):
                    accd = acc.model_dump()
                elif isinstance(acc, dict):
                    accd = acc
                else:
                    try:
                        accd = dict(acc)
                    except Exception:
                        accd = {}
            except Exception:
                accd = {}

            key = accd.get("id") or accd.get("name") or ""
            return positions_map.get(key, [])

    return Prov()


def test_get_portfolio_with_depository_account(client):
    pid = "pf-1"
    accounts = [{"id": "a1", "name": "Cash", "type": "depository", "balance": 100.0}]
    prov = make_provider(accounts, positions_map={}, name="P1")
    # isolate active_providers for deterministic results
    old = registry.active_providers.copy()
    try:
        registry.active_providers.clear()
        registry.active_providers[pid] = prov
        r = client.get("/api/v1/portfolios")
        assert r.status_code == 200
        data = r.json()
        assert data["summary"]["cash_balance"] == 100.0
        assert data["summary"]["investment_balance"] == 0.0
        assert data["summary"]["total_value"] == 100.0
        assert data["holdings"] == []
    finally:
        registry.active_providers.clear()
        registry.active_providers.update(old)


def test_get_portfolio_with_bad_account_conversion(client):
    pid = "pf-bad"

    class BadAcc:
        def __iter__(self):
            raise RuntimeError("nope")

    prov = make_provider([BadAcc()], positions_map={}, name="PBAD")
    old = registry.active_providers.copy()
    try:
        registry.active_providers.clear()
        registry.active_providers[pid] = prov
        r = client.get("/api/v1/portfolios")
        assert r.status_code == 200
        data = r.json()
        # bad account conversion results in no balances and no holdings
        assert data["summary"]["cash_balance"] == 0.0
        assert data["summary"]["investment_balance"] == 0.0
        assert data["holdings"] == []
    finally:
        registry.active_providers.clear()
        registry.active_providers.update(old)


def test_positions_dict_exception_branch(client, monkeypatch):
    # Exercise the dict(pos) exception branch by calling the function
    # directly; the Pydantic response construction will raise ValidationError.

    pid = "pf-posbad"

    class BadPos:
        def __iter__(self):
            raise RuntimeError("nope")

    accounts = [{"id": "a1", "name": "A1", "type": "investment", "balance": 0.0}]
    positions_map = {"a1": [BadPos()]}
    prov = make_provider(accounts, positions_map=positions_map, name="PBADPOS")

    old = registry.active_providers.copy()
    try:
        registry.active_providers.clear()
        registry.active_providers[pid] = prov
        # call the function directly to exercise internal branches; the
        # Pydantic response construction will raise ValidationError because
        # symbol will be None — that's expected for this branch.
        from pydantic import ValidationError
        from app.api.v1.portfolios import get_portfolio
        import asyncio

        with pytest.raises(ValidationError):
            asyncio.run(get_portfolio())
    finally:
        registry.active_providers.clear()
        registry.active_providers.update(old)


def test_get_portfolio_with_mixed_accounts_and_positions(client):
    pid = "pf-mix"
    acc1 = PydanticLike({"id": "p1", "name": "Inv", "type": "investment", "balance": 50.0})
    acc2 = {"id": "p2", "name": "A2", "type": "investment", "balance": 25.0}
    acc3 = IterablePairs({"id": "p3", "name": "A3", "type": "depository", "balance": 10.0})

    pos1 = {"symbol": "ABC", "quantity": 2.0, "current_price": 10.0, "cost_basis": 5.0}
    pos2 = PydanticLike({"symbol": "XYZ", "quantity": 1.0, "current_price": 5.0, "cost_basis": 0.0})

    positions_map = {
        "p1": [pos1],
        "p2": [pos2],
        "A3": [],
    }

    prov = make_provider([acc1, acc2, acc3], positions_map=positions_map, name="PMIX")
    old = registry.active_providers.copy()
    try:
        registry.active_providers.clear()
        registry.active_providers[pid] = prov
        r = client.get("/api/v1/portfolios")
        assert r.status_code == 200
        data = r.json()
        # cash_balance adds all depository and (per current code) also investment balances
        assert data["summary"]["cash_balance"] == 50.0 + 25.0 + 10.0
        # investment_balance is sum of position values: ABC -> 20, XYZ -> 5
        assert data["summary"]["investment_balance"] == 20.0 + 5.0
        assert data["summary"]["total_value"] == data["summary"]["cash_balance"] + data["summary"]["investment_balance"]

        symbols = {h["symbol"] for h in data["holdings"]}
        assert "ABC" in symbols and "XYZ" in symbols
        # find ABC holding and assert gain and gain_pct
        abc = next(h for h in data["holdings"] if h["symbol"] == "ABC")
        assert abc["value"] == 20.0
        assert abc["gain"] == 10.0
        assert abc["gain_pct"] == 100.0
    finally:
        registry.active_providers.clear()
        registry.active_providers.update(old)
