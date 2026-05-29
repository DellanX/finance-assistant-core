from fastapi import APIRouter
from fastapi import APIRouter
from app.api.v1.types import StrategyListResponse, StrategyDefinition

router = APIRouter()


@router.get("", response_model=StrategyListResponse)
def get_strategies():
    # placeholder: no strategies implemented
    return StrategyListResponse(strategies=[])
