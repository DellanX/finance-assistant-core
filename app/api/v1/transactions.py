from fastapi import APIRouter
from app.providers.registry import active_providers
from typing import Optional
from pydantic import BaseModel
from app.api.v1.schemas import TransactionResponse

router = APIRouter()


from app.api.v1.schemas import TransactionResponse


@router.get("")
async def get_transactions(ledger_id: Optional[str] = None, limit: int = None, offset: int = None, page: int = None, cursor: str = None, sort_by: str = "date", order: str = "desc"):
    all_txs: list[dict] = []
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

                tr = {
                    "id": t.get("id"),
                    "date": t.get("date"),
                    "amount": t.get("amount", 0.0),
                    "merchant": t.get("merchant"),
                    "status": t.get("status", "unknown"),
                    "ledger_id": acc_id,
                    "ledger_name": accd.get("name"),
                    "provider_id": provider_id,
                    "provider_name": provider.name,
                }
                all_txs.append(tr)

    # Sort transactions by requested sort (default date desc)
    from app.api.utils.pagination import sort_items, apply_filters, normalize_pagination, paginate_items, build_paginated_response

    # convert date to string if None for stable sorting
    sorted_items = sort_items(all_txs, sort_by, order)

    # If no pagination params provided, preserve legacy behavior and return list of TransactionResponse
    # Always return envelope-shaped TransactionListResponse
    lim, off = normalize_pagination(limit, offset, page, cursor)
    slice_items = paginate_items(sorted_items, lim, off)
    pag = build_paginated_response(slice_items, total=len(sorted_items), limit=lim, offset=off)
    return {"transactions": pag["items"], "total": pag["total"], "limit": pag["limit"], "offset": pag["offset"], "next_cursor": pag.get("next_cursor"), "prev_cursor": pag.get("prev_cursor")}

