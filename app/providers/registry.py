import importlib
import os
from typing import Dict
from app.providers.base import BaseProvider
import json
import inspect
from app.providers.config import ProviderConfig

# Global registry of active providers
active_providers: Dict[str, BaseProvider] = {}
# Optional per-provider configuration objects (used for UI/editable configs)
provider_configs: Dict[str, ProviderConfig] = {}

def _discover_integration_packages() -> Dict[str, str]:
    """Return mapping of package name -> filesystem path for each integration package found.
    An integration package is any subdirectory under this providers folder that contains an __init__.py file.
    """
    base_dir = os.path.dirname(__file__)
    integrations = {}
    for name in os.listdir(base_dir):
        path = os.path.join(base_dir, name)
        if not os.path.isdir(path):
            continue
        init_py = os.path.join(path, "__init__.py")
        if os.path.exists(init_py):
            integrations[name] = path
    return integrations


def list_integration_packages():
    """Return list of discovered integration package names."""
    return list(_discover_integration_packages().keys())


def add_provider(provider_instance: BaseProvider, config: ProviderConfig = None):
    """Register a provider instance and optional ProviderConfig in the registry.

    This will overwrite any existing provider with the same id.
    """
    pid = getattr(provider_instance, "id", None)
    if pid is None:
        raise ValueError("provider instance must have an `id` attribute")
    active_providers[pid] = provider_instance
    if config is not None:
        provider_configs[pid] = config
        # attempt persistence for the newly added config
        try:
            persist_provider_config(pid)
        except Exception:
            pass

def load_integrations():
    """Discover and load providers from integration packages.

    Each integration package may expose a `load_providers()` function which should return
    a mapping of provider_id -> BaseProvider instance. This keeps discovery extensible
    and allows each integration to provide platform-specific code and a coordinator.
    """
    base_pkg = "app.providers"
    integrations = _discover_integration_packages()
    base_dir = os.path.dirname(__file__)

    for pkg_name in integrations.keys():
        module_path = f"{base_pkg}.{pkg_name}"
        try:
            module = importlib.import_module(module_path)
        except Exception:
            # ignore integrations that fail to import for now
            continue

        # Preferred API: integration package provides `load_providers()` -> Dict[id, provider]
        if hasattr(module, "load_providers"):
            try:
                found = module.load_providers()
                if isinstance(found, dict):
                    for pid, provider in found.items():
                        active_providers[pid] = provider
            except Exception:
                continue

# NOTE: integrations are loaded at the end of this module to avoid circular-import
# issues where integration packages call back into registry during their import.

def get_provider(provider_id: str) -> BaseProvider:
    return active_providers.get(provider_id)

def register_provider_config(config: ProviderConfig):
    """Register or replace a provider configuration record."""
    provider_configs[config.provider_id] = config

def get_provider_config(provider_id: str) -> ProviderConfig:
    return provider_configs.get(provider_id)


def persist_provider_config(provider_id: str) -> bool:
    """Persist the in-memory ProviderConfig for `provider_id` to disk.

    Persistence strategy (best-effort):
    1. If the provider instance exposes `update_state(dict)`, call it (provider-specific save).
    2. Else if the provider has `config_path` attribute, write JSON there.
    3. Else, attempt to locate the provider module file and write `config.json` next to it.

    Returns True if a write was attempted without immediate error, False otherwise.
    """
    cfg = provider_configs.get(provider_id)
    if cfg is None:
        return False

    provider = active_providers.get(provider_id)
    # prefer letting provider handle persistence
    if provider is not None:
        # provider-specific save method
        save_fn = getattr(provider, "update_state", None)
        if callable(save_fn):
            try:
                save_fn(cfg.data)
                return True
            except Exception:
                # fall through to other methods
                pass

        # provider config_path attribute
        ppath = getattr(provider, "config_path", None)
        if ppath:
            try:
                with open(ppath, "w") as f:
                    json.dump(cfg.data, f, indent=4)
                return True
            except Exception:
                pass

    # Fallback: write next to provider class file
    try:
        if provider is not None:
            cls = provider.__class__
        else:
            # try to find module by provider_id (not reliable)
            return False
        path = inspect.getfile(cls)
        pkg_dir = os.path.dirname(path)
        target = os.path.join(pkg_dir, "config.json")
        with open(target, "w") as f:
            json.dump(cfg.data, f, indent=4)
        return True
    except Exception:
        return False


def list_providers():
    return list(active_providers.values())

def start_all_coordinators():
    """Start any provider coordinators that expose a `start()` method.

    This is intended to be called on application startup and is synchronous
    because coordinators manage their own asyncio tasks.
    """
    for provider_id, provider in active_providers.items():
        coord = getattr(provider, "coordinator", None)
        if coord and hasattr(coord, "start"):
            try:
                coord.start()
            except Exception:
                # ignore coordinator start failures to avoid crashing startup
                pass

async def stop_all_coordinators():
    """Stop any provider coordinators that expose an async `stop()` method.

    This should be awaited during application shutdown.
    """
    for provider_id, provider in active_providers.items():
        coord = getattr(provider, "coordinator", None)
        if coord and hasattr(coord, "stop"):
            try:
                await coord.stop()
            except Exception:
                pass

def coordinator_statuses():
    """Return a mapping of provider_id -> coordinator status info."""
    statuses = {}
    for provider_id, provider in active_providers.items():
        coord = getattr(provider, "coordinator", None)
        if coord is None:
            statuses[provider_id] = {"has_coordinator": False}
        else:
            statuses[provider_id] = {"has_coordinator": True, "is_running": bool(getattr(coord, "is_running", False))}
    return statuses


# Load integrations on import (deferred until registry helpers are available)
load_integrations()
