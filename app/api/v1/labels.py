from fastapi import APIRouter
from app.providers import labels as labels_module
from .types import LabelListResponse
from fastapi import HTTPException
from .types import LabelDefinition

router = APIRouter()


@router.post("", response_model=LabelDefinition, status_code=201)
async def create_label(payload: LabelDefinition):
    try:
        lbl = labels_module.create_label({"id": payload.id, "name": payload.name, "description": payload.description})
        return lbl
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{label_id}", response_model=LabelDefinition)
async def get_label(label_id: str):
    lbl = labels_module.get_label(label_id)
    if not lbl:
        raise HTTPException(status_code=404, detail="label not found")
    return lbl


@router.put("/{label_id}", response_model=LabelDefinition)
async def update_label(label_id: str, payload: LabelDefinition):
    try:
        lbl = labels_module.update_label(label_id, {"name": payload.name, "description": payload.description})
        return lbl
    except KeyError:
        raise HTTPException(status_code=404, detail="label not found")


@router.delete("/{label_id}", status_code=204)
async def delete_label(label_id: str):
    ok = labels_module.delete_label(label_id)
    if not ok:
        raise HTTPException(status_code=404, detail="label not found")


@router.get("", response_model=LabelListResponse)
async def list_labels(limit: int = None, offset: int = None, page: int = None, cursor: str = None, sort_by: str = None, order: str = "asc"):
    labels = labels_module.list_labels()
    items = labels
    from app.api.utils.pagination import sort_items, normalize_pagination, paginate_items, build_paginated_response

    sorted_items = sort_items(items, sort_by, order)
    lim, off = normalize_pagination(limit, offset, page, cursor)
    slice_items = paginate_items(sorted_items, lim, off)
    pag = build_paginated_response(slice_items, total=len(sorted_items), limit=lim, offset=off)
    return {"labels": pag["items"], "total": pag["total"], "limit": pag["limit"], "offset": pag["offset"], "next_cursor": pag.get("next_cursor"), "prev_cursor": pag.get("prev_cursor")}
