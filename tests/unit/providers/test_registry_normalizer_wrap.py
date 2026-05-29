import pytest

from app.providers.registry import add_provider, get_provider
from app.providers.base import BaseProvider
from app.core.schemas import (
    NormalizedTransaction,
    NormalizedPosition,
    NormalizedAccount,
)


class DummyProvider(BaseProvider):
    def __init__(self, id_):
        self.id = id_

    async def discover_accounts(self):
        return [{"id": "a1", "name": "Main"}]

    async def sync_transactions(self, account, since):
        return [{"id": "tx1", "date": "2026-01-01", "amount": "100", "merchant": "X"}]

    async def sync_positions(self, account):
        return [{"symbol": "BTC", "quantity": "1", "cost_basis": "30000", "current_price": "60000"}]

    async def list_actions(self):
        return []

    async def execute_action(self, action_name: str, payload: dict, dry_run: bool = False):
        return {}

    async def match_transaction(self, optimistic_tx, provider_tx):
        return False


def test_registry_wraps_provider_methods():
    import asyncio

    pid = "dummy:wrap:1"
    p = DummyProvider(pid)
    add_provider(p)
    prov = get_provider(pid)

    accts = asyncio.run(prov.discover_accounts())
    assert isinstance(accts, list)
    a0 = accts[0]
    if hasattr(a0, "model_dump"):
        a0d = a0.model_dump()
    else:
        a0d = a0
    acct_model = NormalizedAccount(**{k: a0d[k] for k in a0d if k in NormalizedAccount.model_fields})
    assert acct_model.id == "a1"

    txs = asyncio.run(prov.sync_transactions(None, None))
    assert isinstance(txs, list)
    t0 = txs[0]
    if hasattr(t0, "model_dump"):
        t0d = t0.model_dump()
    else:
        t0d = t0
    tx_model = NormalizedTransaction(**{k: t0d[k] for k in t0d if k in NormalizedTransaction.model_fields})
    assert tx_model.id == "tx1"

    pos = asyncio.run(prov.sync_positions(None))
    assert isinstance(pos, list)
    p0 = pos[0]
    if hasattr(p0, "model_dump"):
        p0d = p0.model_dump()
    else:
        p0d = p0
    pos_model = NormalizedPosition(**{k: p0d[k] for k in p0d if k in NormalizedPosition.model_fields})
    assert pos_model.symbol == "BTC"
