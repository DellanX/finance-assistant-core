from fastapi import APIRouter
from fastapi import APIRouter
from app.api.v1.types import SnapshotListResponse

router = APIRouter()


@router.get("", response_model=SnapshotListResponse)
def get_snapshots(limit: int = None, offset: int = None, page: int = None, cursor: str = None, sort_by: str = None, order: str = "asc"):
    items = []
    from app.api.utils.pagination import sort_items, normalize_pagination, paginate_items, build_paginated_response

    sorted_items = sort_items(items, sort_by, order)
    lim, off = normalize_pagination(limit, offset, page, cursor)
    slice_items = paginate_items(sorted_items, lim, off)
    pag = build_paginated_response(slice_items, total=len(sorted_items), limit=lim, offset=off)
    return {"snapshots": pag["items"], "total": pag["total"], "limit": pag["limit"], "offset": pag["offset"], "next_cursor": pag.get("next_cursor"), "prev_cursor": pag.get("prev_cursor")}
