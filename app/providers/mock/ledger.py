from typing import Any, Dict

async def async_setup_ledger(provider) -> Dict[str, Any]:
    """Example platform setup for ledgers."""
    # Return a snapshot of positions or transactions as a simple example
    accounts = await provider.discover_accounts()
    ledgers = {}
    for acc in accounts:
        txs = await provider.sync_transactions(acc)
        ledgers[acc.get("id")] = txs
    return {"provider_id": getattr(provider, "id", None), "ledgers": ledgers}
