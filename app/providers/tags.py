from typing import Dict, Any, List

# Predefined tag keys with descriptions and allowed values where applicable.
# Tags are semantic keys that carry meaning in the UI or automation rules.
PREDEFINED_TAGS: Dict[str, Dict[str, Any]] = {
    "environment": {
        "key": "environment",
        "description": "Logical environment of the provider (used for routing/filters).",
        "values": ["prod", "staging", "dev"],
    },
    "region": {
        "key": "region",
        "description": "Geographical region or deployment location.",
        "values": ["us-east", "us-west", "eu-west", "ap-south"],
    },
    "sensitivity": {
        "key": "sensitivity",
        "description": "Indicates sensitivity of data handled by provider.",
        "values": ["low", "medium", "high"],
    },
}


def list_tags() -> List[Dict[str, Any]]:
    return list(PREDEFINED_TAGS.values())


def get_tag(tag_key: str) -> Dict[str, Any]:
    return PREDEFINED_TAGS.get(tag_key)


def create_tag(tag_key: str, definition: Dict[str, Any]) -> Dict[str, Any]:
    if tag_key in PREDEFINED_TAGS:
        raise ValueError("tag already exists")
    entry = {"key": tag_key, "description": definition.get("description"), "values": definition.get("values", [])}
    PREDEFINED_TAGS[tag_key] = entry
    return entry


def update_tag(tag_key: str, definition: Dict[str, Any]) -> Dict[str, Any]:
    if tag_key not in PREDEFINED_TAGS:
        raise KeyError("tag not found")
    entry = PREDEFINED_TAGS[tag_key]
    entry["description"] = definition.get("description", entry.get("description"))
    entry["values"] = definition.get("values", entry.get("values"))
    PREDEFINED_TAGS[tag_key] = entry
    return entry


def delete_tag(tag_key: str) -> bool:
    if tag_key in PREDEFINED_TAGS:
        del PREDEFINED_TAGS[tag_key]
        return True
    return False
