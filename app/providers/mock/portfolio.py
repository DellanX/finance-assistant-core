from typing import Any, Dict

async def async_setup_portfolio(provider) -> Dict[str, Any]:
    """Example platform setup for portfolios."""
    # Platform-specific initialization can go here. For mock, just expose state.
    return {"provider_id": getattr(provider, "id", None), "portfolios": await provider.discover_accounts()}
