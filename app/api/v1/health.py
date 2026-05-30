from fastapi import APIRouter, HTTPException
from app.providers import registry
from app.api.v1.types import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def api_health_check():
    """General API health including provider coordinator statuses."""
    provider_status = {}
    try:
        provider_status = registry.coordinator_statuses()
    except Exception:
        provider_status = {"error": "failed to collect provider statuses"}

    return HealthResponse(status="ok", providers=provider_status)
