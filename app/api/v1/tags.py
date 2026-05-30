from fastapi import APIRouter
from app.providers import tags as tags_module
from .types import TagListResponse
from fastapi import HTTPException
from .types import TagDefinition

router = APIRouter()


@router.post("", response_model=TagDefinition, status_code=201)
async def create_tag(payload: TagDefinition):
    key = payload.key
    try:
        tag = tags_module.create_tag(key, {"description": payload.description, "values": payload.values})
        return tag
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{tag_key}", response_model=TagDefinition)
async def get_tag(tag_key: str):
    tag = tags_module.get_tag(tag_key)
    if not tag:
        raise HTTPException(status_code=404, detail="tag not found")
    return tag


@router.put("/{tag_key}", response_model=TagDefinition)
async def update_tag(tag_key: str, payload: TagDefinition):
    try:
        tag = tags_module.update_tag(tag_key, {"description": payload.description, "values": payload.values})
        return tag
    except KeyError:
        raise HTTPException(status_code=404, detail="tag not found")


@router.delete("/{tag_key}", status_code=204)
async def delete_tag(tag_key: str):
    ok = tags_module.delete_tag(tag_key)
    if not ok:
        raise HTTPException(status_code=404, detail="tag not found")


@router.get("", response_model=TagListResponse)
async def list_tags(limit: int = None, offset: int = None, page: int = None, cursor: str = None, sort_by: str = None, order: str = "asc"):
    tags = tags_module.list_tags()
    items = tags
    from app.api.utils.pagination import sort_items, normalize_pagination, paginate_items, build_paginated_response

    sorted_items = sort_items(items, sort_by, order)
    lim, off = normalize_pagination(limit, offset, page, cursor)
    slice_items = paginate_items(sorted_items, lim, off)
    pag = build_paginated_response(slice_items, total=len(sorted_items), limit=lim, offset=off)
    return {"tags": pag["items"], "total": pag["total"], "limit": pag["limit"], "offset": pag["offset"], "next_cursor": pag.get("next_cursor"), "prev_cursor": pag.get("prev_cursor")}
