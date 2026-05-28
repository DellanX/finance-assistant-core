from typing import Dict, Any, List

# Core-provided action definitions. Each action provides a stable `id` and a
# small metadata blob describing parameters and whether it's a core action.
# UI can use `params` as a JSON Schema-ish map for simple form generation.
CORE_ACTIONS: Dict[str, Dict[str, Any]] = {
    "refresh": {
        "id": "refresh",
        "name": "Refresh Provider",
        "description": "Trigger an immediate refresh/poll for the provider's coordinator.",
        "integration": "core",
        "params": {},
        "supports_dry_run": False,
        "is_async": True,
    },
    "export_state": {
        "id": "export_state",
        "name": "Export State",
        "description": "Request the provider to export its current state for debugging or import.",
        "integration": "core",
        "params": {"format": {"type": "string", "enum": ["json"], "default": "json"}},
        "supports_dry_run": True,
        "is_async": False,
    },
    "force_reconcile": {
        "id": "force_reconcile",
        "name": "Force Reconciliation",
        "description": "Run a reconciliation pass for the provider's data (if supported).",
        "integration": "core",
        "params": {},
        "supports_dry_run": False,
        "is_async": True,
    },
}


def list_core_actions() -> List[Dict[str, Any]]:
    return list(CORE_ACTIONS.values())


def get_core_action(action_id: str) -> Dict[str, Any]:
    return CORE_ACTIONS.get(action_id)
