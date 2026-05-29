from fastapi import APIRouter
from fastapi import APIRouter
from app.api.v1.schemas import TrancheResponse

router = APIRouter()


@router.get("", response_model=list[TrancheResponse])
def get_tranches():
    # no tranches implemented yet
    return []
