from fastapi import APIRouter
from app.providers.registry import active_providers
from typing import Optional
from pydantic import BaseModel
from app.api.v1.schemas import TransactionResponse

router = APIRouter()


@router.get("", response_model=list[TransactionResponse])
async def get_transactions(ledger_id: Optional[str] = None):
    all_txs: list[TransactionResponse] = []
    for provider_id, provider in active_providers.items():
        accounts = await provider.discover_accounts()
        for acc in accounts:
            # normalize account to dict for consistent access
            if hasattr(acc, "model_dump"):
                accd = acc.model_dump()
            elif isinstance(acc, dict):
                accd = acc
            else:
                try:
                    accd = dict(acc)
                except Exception:
                    accd = {}

            acc_id = accd.get("id")
            if ledger_id and acc_id != ledger_id:
                continue
            txs = await provider.sync_transactions(acc)
            for tx in txs:
                # tx is expected to be a NormalizedTransaction (Pydantic model)
                if hasattr(tx, "model_dump"):
                    t = tx.model_dump()
                elif isinstance(tx, dict):
                    t = tx
                else:
                    try:
                        t = dict(tx)
                    except Exception:
                        t = {"id": getattr(tx, "id", ""), "amount": getattr(tx, "amount", 0)}

                tr = TransactionResponse(
                    id=t.get("id"),
                    date=t.get("date"),
                    amount=t.get("amount", 0.0),
                    merchant=t.get("merchant"),
                    status=t.get("status", "unknown"),
                    ledger_id=acc_id,
                    ledger_name=accd.get("name"),
                    provider_id=provider_id,
                    provider_name=provider.name,
                )
                all_txs.append(tr)
    # Sort transactions by date descending
    all_txs.sort(key=lambda x: x.date or "", reverse=True)
    return all_txs

