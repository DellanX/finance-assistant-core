from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from app.providers import registry
from app.providers import actions as core_actions_module
from .types import ActionDefinition, ActionListResponse
import inspect
import importlib
from .types import ActionExecuteRequest, ActionExecuteResponse
from fastapi import Body
from app.providers import actions as core_actions
from app.providers.registry import get_provider

router = APIRouter()


async def _collect_provider_defs(provider_id: str, provider) -> List[Dict[str, Any]]:
    result: List[Dict[str, Any]] = []
    # Provider may expose `get_action_definitions()` as async or sync
    try:
        getter = getattr(provider, "get_action_definitions", None)
        if callable(getter):
            if inspect.iscoroutinefunction(getter):
                defs = await getter()
            else:
                defs = getter()
            for d in defs or []:
                d = dict(d)
                d.setdefault("provider_id", provider_id)
                result.append(d)
    except Exception:
        # ignore provider errors when listing actions
        pass
    return result


@router.get("", response_model=ActionListResponse)
async def list_actions():
    """List all available actions: core + per-provider actions."""
    actions_by_id: Dict[str, Dict[str, Any]] = {}

    # core actions - copy into map
    for c in core_actions_module.list_core_actions():
        actions_by_id[c["id"]] = dict(c)

    # integration-level actions: query each integration package for action types
    for integration in registry.list_integration_packages():
        try:
            mod = importlib.import_module(f"app.providers.{integration}")
        except Exception:
            continue

        # Preferred API: integration package provides `get_action_types()` -> List[action_def]
        if hasattr(mod, "get_action_types"):
            try:
                types = mod.get_action_types()
                for d in types or []:
                    aid = d.get("id")
                    if not aid:
                        continue
                    # ensure entity_id param exists so callers can target instances
                    params = d.get("params") or {}
                    if "entity_id" not in params:
                        params["entity_id"] = {"type": "string", "description": "Target entity id (provider instance)"}
                        d["params"] = params
                    # store integration on the action type
                    d.setdefault("integration", integration)
                    # dedupe by id
                    if aid not in actions_by_id:
                        actions_by_id[aid] = dict(d)
            except Exception:
                continue

    return {"actions": list(actions_by_id.values())}



@router.post("/{action_id}/execute", response_model=ActionExecuteResponse)
async def execute_action(action_id: str, payload: ActionExecuteRequest = Body(...)):
    """Execute an action by id. `entity_id` should identify the provider instance when applicable."""
    # Accept a raw dict when called directly in tests
    if isinstance(payload, dict):
        payload = ActionExecuteRequest(**payload)

    # Normalize params
    params = payload.params or {}
    entity_id = payload.entity_id or params.get("entity_id")
    dry_run = bool(payload.dry_run)

    # 1) Core actions
    core = core_actions.get_core_action(action_id)
    if core is not None:
        # core actions operate on a provider instance (entity_id required)
        if not entity_id:
            raise HTTPException(status_code=400, detail="entity_id is required for core actions")
        provider = get_provider(entity_id)
        if not provider:
            raise HTTPException(status_code=404, detail="Provider not found")

        # dispatch known core actions
        try:
            if action_id == "refresh":
                coord = getattr(provider, "coordinator", None)
                if coord and hasattr(coord, "refresh"):
                    res = coord.refresh()
                    if inspect.iscoroutine(res):
                        await res
                    return {"status": "ok", "result": "refreshed"}
                raise HTTPException(status_code=400, detail="provider has no coordinator to refresh")

            if action_id == "export_state":
                getter = getattr(provider, "get_state", None)
                if callable(getter):
                    state = getter()
                    # if getter is coroutine
                    if inspect.iscoroutine(state):
                        state = await state
                    return {"status": "ok", "result": state}
                raise HTTPException(status_code=400, detail="provider does not support state export")

            if action_id == "force_reconcile":
                fn = getattr(provider, "force_reconcile", None) or getattr(provider, "reconcile", None)
                if callable(fn):
                    res = fn()
                    if inspect.iscoroutine(res):
                        res = await res
                    return {"status": "ok", "result": res}
                raise HTTPException(status_code=501, detail="provider does not implement reconciliation")

        except HTTPException:
            raise
        except Exception as exc:
            return {"status": "error", "error": str(exc)}

    # 2) Integration-level action types - find which integration provides this action
    # Search integrations for action type
    action_def = None
    action_integration = None
    for integration in registry.list_integration_packages():
        try:
            mod = importlib.import_module(f"app.providers.{integration}")
            if hasattr(mod, "get_action_types"):
                try:
                    types = mod.get_action_types()
                except Exception:
                    continue
                for d in types or []:
                    if d.get("id") == action_id:
                        action_def = d
                        action_integration = integration
                        break
            if action_def:
                break
        except Exception:
            continue

    if action_def is None:
        raise HTTPException(status_code=404, detail="action not found")

    # entity_id is required for integration-level actions too
    if not entity_id:
        raise HTTPException(status_code=400, detail="entity_id is required for integration actions")

    provider = get_provider(entity_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    # Call provider.execute_action(action_id, params_without_entity_id, dry_run)
    try:
        # remove entity_id from params passed to provider
        call_params = dict(params)
        if "entity_id" in call_params:
            del call_params["entity_id"]
        res = provider.execute_action(action_id, call_params, dry_run=dry_run)
        if inspect.iscoroutine(res):
            res = await res
        return {"status": "ok", "result": res}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@router.get("/categories")
async def list_categories():
    # moved to /api/v1/categories
    raise HTTPException(status_code=410, detail="moved to /api/v1/categories")


@router.get("/tags")
async def list_tags():
    # moved to /api/v1/tags
    raise HTTPException(status_code=410, detail="moved to /api/v1/tags")


@router.get("/providers/{provider_id}", response_model=ActionListResponse)
async def list_provider_actions(provider_id: str):
    provider = registry.get_provider(provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    actions_by_id: Dict[str, Dict[str, Any]] = {}
    for c in core_actions_module.list_core_actions():
        actions_by_id[c["id"]] = dict(c)

    # include integration-level actions for this provider's integration
    # Infer integration name from provider class module (e.g. app.providers.mock.provider)
    integration = None
    try:
        modname = getattr(provider.__class__, "__module__", "")
        marker = "app.providers."
        if marker in modname:
            integration = modname.split(marker, 1)[1].split(".", 1)[0]
        else:
            integration = getattr(provider, "integration", None)
    except Exception:
        integration = None

    if integration:
        try:
            mod = importlib.import_module(f"app.providers.{integration}")
            if hasattr(mod, "get_action_types"):
                types = mod.get_action_types()
                for d in types or []:
                    aid = d.get("id")
                    if not aid:
                        continue
                    params = d.get("params") or {}
                    # ensure entity_id param exists and default to this provider id
                    if "entity_id" not in params:
                        params["entity_id"] = {"type": "string", "description": "Target entity id (provider instance)", "default": provider_id}
                    else:
                        params["entity_id"]["default"] = provider_id
                    d["params"] = params
                    d.setdefault("integration", integration)
                    if aid not in actions_by_id:
                        actions_by_id[aid] = dict(d)
        except Exception:
            pass

    return {"actions": list(actions_by_id.values())}
