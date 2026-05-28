from fastapi import APIRouter
from app.providers.registry import active_providers
from typing import Optional

router = APIRouter()

@router.get("")
async def get_transactions(ledger_id: Optional[str] = None):
    all_txs = []
    for provider_id, provider in active_providers.items():
        accounts = await provider.discover_accounts()
        for acc in accounts:
            acc_id = acc.get("id")
            if ledger_id and acc_id != ledger_id:
                continue
            txs = await provider.sync_transactions(acc)
            for tx in txs:
                all_txs.append({
                    "id": tx.get("id"),
                    "date": tx.get("date"),
                    "amount": tx.get("amount"),
                    "merchant": tx.get("merchant"),
                    "status": tx.get("status"),
                    "ledger_id": acc_id,
                    "ledger_name": acc.get("name"),
                    "provider_id": provider_id,
                    "provider_name": provider.name
                })
    # Sort transactions by date descending
    all_txs.sort(key=lambda x: x["date"], reverse=True)
    return all_txs

