from typing import Any, Dict
from app.providers import registry


async def async_setup_budget(provider) -> Dict[str, Any]:
    """Example budget platform for mock provider (no-op for now)."""
    cfg = None
    try:
        cfg = registry.get_provider_config(getattr(provider, "id", None))
    except Exception:
        cfg = None

    enabled = True
    if cfg is not None:
        enabled = bool(cfg.data.get("enable_budgets", False))

    if not enabled:
        return {"provider_id": getattr(provider, "id", None), "budgets": []}

    # If budgets were present in provider state, surface them; otherwise empty for mock
    budgets = []
    try:
        state = provider.get_state()
        budgets = state.get("budgets", [])
    except Exception:
        budgets = []

    return {"provider_id": getattr(provider, "id", None), "budgets": budgets}
