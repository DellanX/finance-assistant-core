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

router = APIRouter()


@router.get("", response_model=TagListResponse)
async def list_tags():
    tags = tags_module.list_tags()
    return {"tags": tags}
