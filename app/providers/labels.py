from typing import Dict, Any, List

# Labels are simple, UI-friendly short tags that users can assign.
# For now we expose a set of predefined labels; this can be made dynamic later.
PREDEFINED_LABELS: List[Dict[str, Any]] = [
    {"id": "manual", "name": "Manual", "description": "Requires manual invocation"},
    {"id": "dangerous", "name": "Dangerous", "description": "May cause data loss or side-effects"},
    {"id": "scheduled", "name": "Scheduled", "description": "Intended for scheduled runs"},
]


def list_labels() -> List[Dict[str, Any]]:
    return PREDEFINED_LABELS


def get_label(label_id: str) -> Dict[str, Any]:
    for l in PREDEFINED_LABELS:
        if l.get("id") == label_id:
            return l
    return None


def create_label(definition: Dict[str, Any]) -> Dict[str, Any]:
    lid = definition.get("id")
    if not lid:
        raise ValueError("label id is required")
    if get_label(lid) is not None:
        raise ValueError("label already exists")
    entry = {"id": lid, "name": definition.get("name"), "description": definition.get("description")}
    PREDEFINED_LABELS.append(entry)
    return entry


def update_label(label_id: str, definition: Dict[str, Any]) -> Dict[str, Any]:
    for i, l in enumerate(PREDEFINED_LABELS):
        if l.get("id") == label_id:
            PREDEFINED_LABELS[i]["name"] = definition.get("name", l.get("name"))
            PREDEFINED_LABELS[i]["description"] = definition.get("description", l.get("description"))
            return PREDEFINED_LABELS[i]
    raise KeyError("label not found")


def delete_label(label_id: str) -> bool:
    for i, l in enumerate(PREDEFINED_LABELS):
        if l.get("id") == label_id:
            PREDEFINED_LABELS.pop(i)
            return True
    return False
