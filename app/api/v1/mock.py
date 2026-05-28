from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.providers.registry import get_provider

router = APIRouter()

@router.get("/state/{provider_id}")
def get_mock_state(provider_id: str):
    provider = get_provider(provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    if not hasattr(provider, "get_state"):
        raise HTTPException(status_code=400, detail="Provider is not a mock provider")
    return provider.get_state()

@router.post("/state/{provider_id}")
def update_mock_state(provider_id: str, updates: Dict[str, Any]):
    provider = get_provider(provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    if not hasattr(provider, "update_state"):
        raise HTTPException(status_code=400, detail="Provider is not a mock provider")
    provider.update_state(updates)
    return {"status": "success", "message": "Mock state updated"}
