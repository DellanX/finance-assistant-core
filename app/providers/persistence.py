import json
import os
from typing import Any


def write_json_file(path: str, data: Any) -> bool:
    """Write `data` as JSON to `path`. Returns True on success, False on error."""
    try:
        dirname = os.path.dirname(path)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=4)
        return True
    except Exception:
        return False


def remove_file(path: str) -> bool:
    """Remove a file if it exists. Returns True if removed or not present, False on error."""
    try:
        if not path:
            return False
        if os.path.exists(path):
            os.remove(path)
        return True
    except Exception:
        return False
