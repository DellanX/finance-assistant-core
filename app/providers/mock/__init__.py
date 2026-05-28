import os
from typing import Dict
from .provider import MockProvider
from app.providers.config import ProviderConfig
from app.providers import registry
from .config import get_default_config, get_schema, MockProviderConfig

def load_providers() -> Dict[str, MockProvider]:
    """Discover mock provider JSON configs in the `mock_data` folder and return
    a mapping of provider_id -> MockProvider instance.
    """
    base_dir = os.path.dirname(__file__)
    mock_data_dir = os.path.join(base_dir, "mock_data")
    providers = {}

    if os.path.exists(mock_data_dir):
        for filename in os.listdir(mock_data_dir):
            if filename.endswith(".json"):
                path = os.path.join(mock_data_dir, filename)
                provider = MockProvider(config_path=path)
                providers[provider.id] = provider

                # Register a ProviderConfig record so UIs can discover editable settings
                try:
                    state = provider.get_state()
                    defaults = get_default_config()
                    config_data = state.get("config", defaults)
                    # Merge defaults for any missing keys
                    for k, v in defaults.items():
                        config_data.setdefault(k, v)

                    schema = get_schema()

                    # Prefer the integration-specific ProviderConfig subclass
                    try:
                        config = MockProviderConfig(provider_id=provider.id, data=config_data)
                    except Exception:
                        config = ProviderConfig(provider_id=provider.id, data=config_data, schema=schema)

                    registry.register_provider_config(config)
                except Exception:
                    # best-effort; don't fail loading providers if config registration fails
                    pass

    return providers


def get_action_types():
    """Return integration-level action type definitions for the mock integration.

    These definitions are not bound to a specific provider instance and should
    accept an `entity_id` parameter used to target a provider instance at execution time.
    """
    return [
        {
            "id": "simulate_transfer",
            "name": "Simulate Transfer",
            "description": "Simulate moving funds between mock accounts for testing UI flows.",
            "integration": "mock",
            "params": {
                "entity_id": {"type": "string", "description": "Target provider instance id"},
                "from_account": {"type": "string"},
                "to_account": {"type": "string"},
                "amount": {"type": "number"},
            },
            "supports_dry_run": True,
            "is_async": False,
        },
        {
            "id": "simulate_failure",
            "name": "Simulate Failure",
            "description": "Trigger a simulated failing action to test error handling paths.",
            "integration": "mock",
            "params": {"entity_id": {"type": "string", "description": "Target provider instance id"}},
            "supports_dry_run": False,
            "is_async": False,
        },
    ]
