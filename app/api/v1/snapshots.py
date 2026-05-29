from fastapi import APIRouter
from fastapi import APIRouter
from app.api.v1.types import SnapshotListResponse

router = APIRouter()


@router.get("", response_model=SnapshotListResponse)
def get_snapshots():
    return SnapshotListResponse(snapshots=[])
