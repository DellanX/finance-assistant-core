from typing import Dict, Any
from app.providers.config import ProviderConfig


DEFAULT_CONFIG: Dict[str, Any] = {
    "enable_balances": True,
    "enable_transactions": True,
    "enable_budgets": False,
}


SCHEMA = {
    "enable_balances": {
        "type": "boolean",
        "default": True,
        "title": "Enable Balances",
        "description": "Show account balances and positions when enabled",
    },
    "enable_transactions": {
        "type": "boolean",
        "default": True,
        "title": "Enable Transactions",
        "description": "Allow querying and displaying transaction lists",
    },
    "enable_budgets": {
        "type": "boolean",
        "default": False,
        "title": "Enable Budgets",
        "description": "Expose budget data from the provider when enabled",
    },
}


class MockProviderConfig(ProviderConfig):
    """ProviderConfig subclass for the mock provider exposing defaults and schema."""

    def __init__(self, provider_id: str, data: Dict[str, Any] | None = None):
        cfg = dict(DEFAULT_CONFIG)
        if data:
            # merge provided data over defaults
            cfg.update(data)
        super().__init__(provider_id=provider_id, data=cfg, schema=SCHEMA)


def get_default_config() -> Dict[str, Any]:
    return dict(DEFAULT_CONFIG)


def get_schema() -> Dict[str, Any]:
    return dict(SCHEMA)
