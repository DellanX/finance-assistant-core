from fastapi import APIRouter, HTTPException
from app.providers import registry
from app.api.v1.types import HealthResponse, ProviderConfigModel, SimpleStatusResponse

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


@router.get("/providers/{provider_id}/config", response_model=ProviderConfigModel)
def get_provider_config(provider_id: str):
    """Expose provider configuration for UI consumption."""
    try:
        cfg = registry.get_provider_config(provider_id)
        if cfg is None:
            raise HTTPException(status_code=404, detail="not_found")
        return ProviderConfigModel(config=cfg.to_dict())
    except Exception:
        raise HTTPException(status_code=500, detail="failed")


@router.put("/providers/{provider_id}/config", response_model=ProviderConfigModel)
def update_provider_config(provider_id: str, payload: ProviderConfigModel):
    """Update a provider's configuration and persist it where possible."""
    try:
        cfg = registry.get_provider_config(provider_id)
        if cfg is None:
            raise HTTPException(status_code=404, detail="not_found")

        # Merge updates
        cfg.update(payload.config)

        saved = registry.persist_provider_config(provider_id)
        return ProviderConfigModel(config=cfg.to_dict())
    except Exception:
        raise HTTPException(status_code=500, detail="failed")
