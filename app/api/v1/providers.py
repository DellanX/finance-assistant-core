from fastapi import APIRouter, HTTPException
import app.providers.registry as registry
import os
import inspect
import importlib
import uuid
import json
from pathlib import Path
from app.providers.config import ProviderConfig
from app.providers.base import BaseProvider
from .types import (
    ProviderCreateRequest,
    ProviderResponse,
    ProviderListItem,
    ProviderConfigModel,
    ProviderSchemaResponse,
)
from .schemas import AccountResponse
from typing import List, Dict, Any
from fastapi import Response
from app.api.v1.schemas import AccountResponse
from app.providers.persistence import remove_file
from app.providers import devices as device_registry

router = APIRouter()

# Backwards-compatible aliases to registry internals. Tests and older callers
# may patch these names on this module, so keep them exported here.
get_provider = registry.get_provider
get_provider_config = registry.get_provider_config
list_integration_packages = registry.list_integration_packages
add_provider = registry.add_provider
register_provider_config = registry.register_provider_config
persist_provider_config = registry.persist_provider_config
active_providers = registry.active_providers
provider_configs = registry.provider_configs
list_provider_devices = device_registry.list_devices


@router.get("")
def get_providers(limit: int = None, offset: int = None, page: int = None, cursor: str = None, sort_by: str = None, order: str = "asc", name: str = None):
    """List providers. Backwards compatible: if no pagination/filter params provided,
    return a simple list. Otherwise return a paginated envelope with cursors.
    """
    # Build basic list
    all_items = []
    for pid, p in registry.active_providers.items():
        all_items.append({"id": pid, "name": getattr(p, "name", None), "integration": _provider_integration(p)})

    # Return envelope (Pydantic model) always
    if limit is None and offset is None and page is None and cursor is None and sort_by is None and name is None:
        return {"providers": all_items, "total": len(all_items), "limit": None, "offset": 0, "next_cursor": None, "prev_cursor": None}

    # apply filtering
    from app.api.utils.pagination import (
        normalize_pagination,
        apply_filters,
        sort_items,
        paginate_items,
        build_paginated_response,
    )

    filters = {}
    if name is not None:
        filters["name"] = f"*{name}*"

    filtered = apply_filters(all_items, filters)
    sorted_items = sort_items(filtered, sort_by, order)
    lim, off = normalize_pagination(limit, offset, page, cursor)
    slice_items = paginate_items(sorted_items, lim, off)
    pag = build_paginated_response(slice_items, total=len(sorted_items), limit=lim, offset=off)
    return {"providers": pag["items"], "total": pag["total"], "limit": pag["limit"], "offset": pag["offset"], "next_cursor": pag.get("next_cursor"), "prev_cursor": pag.get("prev_cursor")}


def _provider_integration(provider) -> str:
    """Try to infer the integration package name for a provider instance.

    Falls back to an `integration` attribute if present or None otherwise.
    """
    try:
        mod = getattr(provider.__class__, "__module__", "")
        marker = "app.providers."
        if marker in mod:
            rest = mod.split(marker, 1)[1]
            parts = rest.split(".")
            if parts:
                return parts[0]
    except Exception:
        pass
    return getattr(provider, "integration", None)


@router.get("/schemas")
def list_provider_schemas():
    # Deprecated here: schema endpoints moved to /api/v1/schemas/providers
    raise HTTPException(status_code=410, detail="moved to /api/v1/schemas/providers")


@router.get("/schemas/{integration}")
def get_integration_schema(integration: str):
    # Deprecated here: schema endpoints moved to /api/v1/schemas/providers/{integration}
    raise HTTPException(status_code=410, detail="moved to /api/v1/schemas/providers/{integration}")

@router.get("/{id}/accounts")
async def get_provider_accounts(id: str, limit: int = None, offset: int = None, page: int = None, cursor: str = None, sort_by: str = None, order: str = "asc"):
    provider = registry.get_provider(id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    accounts = await provider.discover_accounts()
    items = []
    for acc in accounts:
        if hasattr(acc, "model_dump"):
            accd = acc.model_dump()
        elif isinstance(acc, dict):
            accd = acc
        else:
            try:
                accd = dict(acc)
            except Exception:
                accd = {}

        items.append({
            "id": accd.get("id", ""),
            "name": accd.get("name"),
            "type": accd.get("type"),
            "balance": accd.get("balance", 0.0),
            "provider_id": id,
            "provider_name": provider.name,
        })

    from app.api.utils.pagination import sort_items, normalize_pagination, paginate_items, build_paginated_response

    sorted_items = sort_items(items, sort_by, order)
    lim, off = normalize_pagination(limit, offset, page, cursor)
    slice_items = paginate_items(sorted_items, lim, off)
    pag = build_paginated_response(slice_items, total=len(sorted_items), limit=lim, offset=off)
    return {"accounts": pag["items"], "total": pag["total"], "limit": pag["limit"], "offset": pag["offset"], "next_cursor": pag.get("next_cursor"), "prev_cursor": pag.get("prev_cursor")}



@router.get("/{id}/config/schema", response_model=ProviderSchemaResponse)
def get_provider_schema(id: str):
    cfg = registry.get_provider_config(id)
    if cfg is None:
        raise HTTPException(status_code=404, detail="Provider config not found")
    return {"provider_id": id, "schema": cfg.schema}


@router.get("/{id}/config", response_model=ProviderConfigModel)
def get_provider_config_endpoint(id: str):
    cfg = registry.get_provider_config(id)
    if cfg is None:
        raise HTTPException(status_code=404, detail="Provider config not found")
    return ProviderConfigModel(config=cfg.data)


@router.put("/{id}/config", response_model=ProviderConfigModel)
def update_provider_config(id: str, payload: ProviderConfigModel):
    cfg = get_provider_config(id)
    if cfg is None:
        raise HTTPException(status_code=404, detail="Provider config not found")

    # merge top-level keys from payload.config into existing config
    updates = payload.config or {}
    cfg.data.update(updates)
    # register and attempt persistence
    try:
        register_provider_config(cfg)
    except Exception:
        pass
    persisted = False
    try:
        persisted = persist_provider_config(id)
    except Exception:
        persisted = False

    return ProviderConfigModel(config=cfg.data)



# Move the simple metadata endpoint after the more-specific config/schema endpoints
@router.get("/{id}", response_model=ProviderResponse)
def get_provider_metadata(id: str):
    """Return basic provider metadata matching the list representation."""
    provider = get_provider(id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return ProviderResponse(id=id, name=getattr(provider, "name", None), integration=_provider_integration(provider))


@router.delete("/{id}", status_code=204)
async def delete_provider(id: str):
    provider = registry.get_provider(id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    # stop coordinator if present
    coord = getattr(provider, "coordinator", None)
    if coord and hasattr(coord, "stop"):
        try:
            # coord.stop may be async
            res = coord.stop()
            if inspect.iscoroutine(res):
                await res
        except Exception:
            pass

    # provider-specific cleanup: remove config file if exists
    try:
        ppath = getattr(provider, "config_path", None)
        if ppath:
            remove_file(ppath)
    except Exception:
        pass

    # remove from registry collections
    try:
        if id in registry.active_providers:
            del registry.active_providers[id]
    except Exception:
        pass
    try:
        if id in registry.provider_configs:
            del registry.provider_configs[id]
    except Exception:
        pass

    return Response(status_code=204)


@router.post("", response_model=ProviderResponse)
def create_provider(payload: ProviderCreateRequest):
    """Create a new provider instance for an integration.

    Expected payload: { "integration": "mock", "id": "optional-id", "name": "Optional Name", "config": { ... } }
    For integrations that provide a `create_provider` helper (package-level), that will be used.
    Otherwise, we currently support a fallback for the `mock` integration which writes a JSON
    file under its `mock_data` folder and instantiates a `MockProvider`.
    """
    integration = payload.integration
    if not integration:
        raise HTTPException(status_code=400, detail="integration is required")

    if integration not in registry.list_integration_packages():
        raise HTTPException(status_code=404, detail="integration not found")

    cfg = payload.config or {}
    provided_id = payload.id
    name = payload.name or cfg.get("name")

    # Try to use integration-provided factory
    try:
        importer = getattr(registry, "_import_module_fn", None) or importlib.import_module
        mod = importer(f"app.providers.{integration}")
        if hasattr(mod, "create_provider"):
            provider = mod.create_provider(cfg, provider_id=provided_id, name=name)
            # if provider factory also returned config info, try to register
            pid = getattr(provider, "id", None)
            config_obj = ProviderConfig(provider_id=pid, data=cfg)
            registry.add_provider(provider, config_obj)
            # Return typed ProviderResponse
            return ProviderResponse(id=pid, name=getattr(provider, "name", name), integration=integration)
    except Exception:
        # fallback to integration-specific handling below
        pass

    # Fallback: handle `mock` integration explicitly
    if integration == "mock":
        try:
            # Prepare id and file path
            pid = provided_id or f"mock_custom_{uuid.uuid4().hex[:8]}"
            if not name:
                name = f"Mock Provider {pid}"

            providers_dir = Path(__file__).resolve().parents[3] / "app" / "providers" / "mock" / "mock_data"
            providers_dir.mkdir(parents=True, exist_ok=True)
            target = providers_dir / f"{pid}.json"

            # Compose base state
            state = {
                "id": pid,
                "name": name,
                "config": cfg,
                "accounts": cfg.get("accounts", []),
                "transactions": cfg.get("transactions", {}),
                "positions": cfg.get("positions", {}),
            }
            with open(target, "w") as f:
                json.dump(state, f, indent=4)

            # instantiate provider
            importer = getattr(registry, "_import_module_fn", None) or importlib.import_module
            provider_mod = importer("app.providers.mock.provider")
            ProviderClass = None
            for v in vars(provider_mod).values():
                try:
                    if isinstance(v, type) and issubclass(v, BaseProvider) and v is not BaseProvider:
                        ProviderClass = v
                        break
                except Exception:
                    continue
            if ProviderClass is None:
                # fallback: look for MockProvider symbol
                ProviderClass = getattr(provider_mod, "MockProvider", None)

            if ProviderClass is None:
                raise HTTPException(status_code=500, detail="provider class not found")

            # Try several constructor signatures to accommodate different providers
            provider = None
            try:
                provider = ProviderClass(config_path=str(target))
            except TypeError:
                try:
                    provider = ProviderClass()
                except TypeError:
                    try:
                        provider = ProviderClass(provider_id=pid, name=name, config_path=str(target))
                    except Exception as e:
                        raise HTTPException(status_code=500, detail=f"failed to instantiate provider: {e}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"failed to instantiate provider: {e}")

            # Register config object
            # prefer integration-specific config class if present
            try:
                importer = getattr(registry, "_import_module_fn", None) or importlib.import_module
                cfg_mod = importer("app.providers.mock.config")
                if hasattr(cfg_mod, "MockProviderConfig"):
                    config_obj = cfg_mod.MockProviderConfig(provider_id=pid, data=cfg)
                else:
                    config_obj = ProviderConfig(provider_id=pid, data=cfg)
            except Exception:
                config_obj = ProviderConfig(provider_id=pid, data=cfg)

            registry.add_provider(provider, config_obj)

            # Return typed ProviderResponse
            return ProviderResponse(id=pid, name=getattr(provider, "name", name), integration=integration)
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    raise HTTPException(status_code=400, detail="creation for this integration is not supported")


@router.get("/{id}/devices")
def get_provider_devices(id: str):
    provider = registry.get_provider(id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    devices = device_registry.list_devices(id)

    def to_dict(m):
        if hasattr(m, "model_dump"):
            return m.model_dump()
        try:
            return m.dict()
        except Exception:
            return {}

    return {"devices": [to_dict(d) for d in devices]}
