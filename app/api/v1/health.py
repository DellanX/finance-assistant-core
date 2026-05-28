from fastapi import APIRouter
from app.providers import registry

router = APIRouter()


@router.get("/health")
def api_health_check():
    """General API health including provider coordinator statuses."""
    provider_status = {}
    try:
        provider_status = registry.coordinator_statuses()
    except Exception:
        provider_status = {"error": "failed to collect provider statuses"}

    return {"status": "ok", "providers": provider_status}


@router.get("/providers/{provider_id}/config")
def get_provider_config(provider_id: str):
    """Expose provider configuration for UI consumption."""
    try:
        cfg = registry.get_provider_config(provider_id)
        if cfg is None:
            return {"error": "not_found"}
        return {"config": cfg.to_dict()}
    except Exception:
        return {"error": "failed"}


@router.put("/providers/{provider_id}/config")
def update_provider_config(provider_id: str, payload: dict):
    """Update a provider's configuration and persist it where possible."""
    try:
        cfg = registry.get_provider_config(provider_id)
        if cfg is None:
            return {"error": "not_found"}

        # Merge updates
        cfg.update(payload)

        saved = registry.persist_provider_config(provider_id)
        return {"config": cfg.to_dict(), "persisted": bool(saved)}
    except Exception:
        return {"error": "failed"}
