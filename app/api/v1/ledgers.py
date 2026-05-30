from fastapi import APIRouter
from app.providers.registry import active_providers
from app.api.v1.schemas import LedgerResponse

router = APIRouter()


@router.get("")
async def get_ledgers(limit: int = None, offset: int = None, page: int = None, cursor: str = None, sort_by: str = None, order: str = "asc"):
    items: list[dict] = []
    for provider_id, provider in active_providers.items():
        accounts = await provider.discover_accounts()
        for acc in accounts:
            # acc may be a Pydantic model
            if hasattr(acc, "model_dump"):
                accd = acc.model_dump()
            elif isinstance(acc, dict):
                accd = acc
            else:
                try:
                    accd = dict(acc)
                except Exception:
                    accd = {}

            lr = {
                "id": accd.get("id", ""),
                "name": accd.get("name"),
                "currency": accd.get("currency"),
                "balance": accd.get("balance", 0.0),
                "accounts_count": 1,
                "provider_id": provider_id,
                "provider_name": provider.name,
            }
            items.append(lr)

    from app.api.utils.pagination import sort_items, normalize_pagination, paginate_items, build_paginated_response

    sorted_items = sort_items(items, sort_by, order)
    # Always return a LedgerListResponse envelope
    lim, off = normalize_pagination(limit, offset, page, cursor)
    slice_items = paginate_items(sorted_items, lim, off)
    pag = build_paginated_response(slice_items, total=len(sorted_items), limit=lim, offset=off)
    return {"ledgers": pag["items"], "total": pag["total"], "limit": pag["limit"], "offset": pag["offset"], "next_cursor": pag.get("next_cursor"), "prev_cursor": pag.get("prev_cursor")}

