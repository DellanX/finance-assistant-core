from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.providers.registry import get_provider
from app.api.v1.types import MockStateResponse, SimpleStatusResponse

router = APIRouter()


@router.get("/state/{provider_id}", response_model=MockStateResponse)
def get_mock_state(provider_id: str):
    provider = get_provider(provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    if not hasattr(provider, "get_state"):
        raise HTTPException(status_code=400, detail="Provider is not a mock provider")
    state = provider.get_state()
    return MockStateResponse(state=state)


@router.post("/state/{provider_id}", response_model=SimpleStatusResponse)
def update_mock_state(provider_id: str, updates: Dict[str, Any]):
    provider = get_provider(provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    if not hasattr(provider, "update_state"):
        raise HTTPException(status_code=400, detail="Provider is not a mock provider")
    provider.update_state(updates)
    return SimpleStatusResponse(status="success", message="Mock state updated")
