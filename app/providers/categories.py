from typing import Dict, Any, List

# Predefined categories used to classify provider actions and other resources.
PREDEFINED_CATEGORIES: Dict[str, Dict[str, Any]] = {
    "management": {"id": "management", "name": "Management", "description": "Operational actions for managing providers."},
    "diagnostic": {"id": "diagnostic", "name": "Diagnostic", "description": "Diagnostics and export/import actions."},
    "data": {"id": "data", "name": "Data", "description": "Data processing or reconciliation actions."},
    "testing": {"id": "testing", "name": "Testing", "description": "Testing utilities and simulations."},
}


def list_categories() -> List[Dict[str, Any]]:
    return list(PREDEFINED_CATEGORIES.values())


def get_category(cat_id: str) -> Dict[str, Any]:
    return PREDEFINED_CATEGORIES.get(cat_id)


def create_category(cat_id: str, definition: Dict[str, Any]) -> Dict[str, Any]:
    if cat_id in PREDEFINED_CATEGORIES:
        raise ValueError("category already exists")
    entry = {"id": cat_id, "name": definition.get("name"), "description": definition.get("description")}
    PREDEFINED_CATEGORIES[cat_id] = entry
    return entry


def update_category(cat_id: str, definition: Dict[str, Any]) -> Dict[str, Any]:
    if cat_id not in PREDEFINED_CATEGORIES:
        raise KeyError("category not found")
    entry = PREDEFINED_CATEGORIES[cat_id]
    entry["name"] = definition.get("name", entry.get("name"))
    entry["description"] = definition.get("description", entry.get("description"))
    PREDEFINED_CATEGORIES[cat_id] = entry
    return entry


def delete_category(cat_id: str) -> bool:
    if cat_id in PREDEFINED_CATEGORIES:
        del PREDEFINED_CATEGORIES[cat_id]
        return True
    return False
