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

router = APIRouter()


@router.get("", response_model=LabelListResponse)
async def list_labels():
    labels = labels_module.list_labels()
    return {"labels": labels}
