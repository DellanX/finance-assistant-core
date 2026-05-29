from fastapi import APIRouter
from app.providers import categories as categories_module
from .types import CategoryListResponse
from fastapi import HTTPException
from .types import CategoryDefinition

router = APIRouter()


@router.post("", response_model=CategoryDefinition, status_code=201)
async def create_category(payload: CategoryDefinition):
    cid = payload.id
    try:
        cat = categories_module.create_category(cid, {"name": payload.name, "description": payload.description})
        return cat
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{category_id}", response_model=CategoryDefinition)
async def get_category(category_id: str):
    cat = categories_module.get_category(category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="category not found")
    return cat


@router.put("/{category_id}", response_model=CategoryDefinition)
async def update_category(category_id: str, payload: CategoryDefinition):
    try:
        cat = categories_module.update_category(category_id, {"name": payload.name, "description": payload.description})
        return cat
    except KeyError:
        raise HTTPException(status_code=404, detail="category not found")


@router.delete("/{category_id}", status_code=204)
async def delete_category(category_id: str):
    ok = categories_module.delete_category(category_id)
    if not ok:
        raise HTTPException(status_code=404, detail="category not found")


@router.get("", response_model=CategoryListResponse)
async def list_categories():
    cats = categories_module.list_categories()
    return {"categories": cats}
