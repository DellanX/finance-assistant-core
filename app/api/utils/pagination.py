from typing import Any, Dict, List, Tuple, Optional
import base64
import json


def normalize_pagination(limit: Optional[int], offset: Optional[int], page: Optional[int], cursor: Optional[str] = None, default_limit: int = 50, max_limit: int = 500) -> Tuple[int, int]:
    """Normalize pagination inputs into (limit, offset).

    Accepts either `offset` or `page`. If both are provided, `offset` takes precedence.
    Caps `limit` at `max_limit` and ensures non-negative values.
    """
    if limit is None:
        limit = default_limit
    try:
        limit = int(limit)
    except Exception:
        limit = default_limit
    if limit <= 0:
        limit = default_limit
    limit = min(limit, max_limit)

    # If a cursor is provided, decode it to determine the offset (cursor-based pagination)
    if cursor:
        try:
            offset = decode_cursor(cursor)
        except Exception:
            offset = None

    if offset is not None:
        try:
            offset = int(offset)
        except Exception:
            offset = 0
    elif page is not None:
        try:
            p = int(page)
            offset = max(0, (p - 1) * limit)
        except Exception:
            offset = 0
    else:
        offset = 0

    if offset < 0:
        offset = 0
    return limit, offset


def encode_cursor(offset: int) -> str:
    """Encode an integer offset into an opaque cursor string."""
    payload = {"offset": int(offset)}
    b = json.dumps(payload).encode()
    return base64.urlsafe_b64encode(b).decode()


def decode_cursor(cursor: str) -> int:
    """Decode an opaque cursor string into an integer offset.

    Returns 0 if decoding fails.
    """
    try:
        b = base64.urlsafe_b64decode(cursor.encode())
        payload = json.loads(b.decode())
        return int(payload.get("offset", 0))
    except Exception:
        return 0


def make_next_cursor(offset: int, limit: int) -> str:
    return encode_cursor(offset + limit)


def apply_filters(items: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Apply simple filters to a list of dict-like items.

    Supported filter value formats:
    - Exact match: value (string/number)
    - Comparison: ">10", "<5", ">=3", "<=2"
    - Contains: "*substr*" (case-insensitive)
    """
    def match(value, cond):
        if cond is None:
            return True
        s = str(cond)
        if isinstance(value, (int, float)):
            try:
                if s.startswith(">="):
                    return value >= float(s[2:])
                if s.startswith("<="):
                    return value <= float(s[2:])
                if s.startswith(">"):
                    return value > float(s[1:])
                if s.startswith("<"):
                    return value < float(s[1:])
                return value == float(s)
            except Exception:
                return False
        # string handling
        vs = str(value or "").lower()
        if s.startswith("*") and s.endswith("*") and len(s) >= 2:
            return s[1:-1].lower() in vs
        return vs == s.lower()

    out = items
    for k, v in (filters or {}).items():
        out = [it for it in out if match(it.get(k), v)]
    return out


def sort_items(items: List[Dict[str, Any]], sort_by: Optional[str], order: str = "asc") -> List[Dict[str, Any]]:
    """Sort items by a single field. `sort_by` may be None.

    If `order` is "desc" will reverse. Missing values sort last.
    """
    if not sort_by:
        return items

    rev = order.lower() in ("desc", "descending")

    # Keep items with missing values last regardless of order.
    non_none = [it for it in items if it.get(sort_by) is not None]
    none_vals = [it for it in items if it.get(sort_by) is None]

    try:
        non_none_sorted = sorted(non_none, key=lambda it: it.get(sort_by), reverse=rev)
    except Exception:
        # Fallback to original behavior if values are not comparable
        def keyfn(it):
            v = it.get(sort_by)
            return (v is None, v)
        non_none_sorted = sorted(items, key=keyfn, reverse=rev)
        # ensure None values still appear at the end
        non_none_sorted = [it for it in non_none_sorted if it.get(sort_by) is not None]

    return non_none_sorted + none_vals


def paginate_items(items: List[Dict[str, Any]], limit: int, offset: int) -> List[Dict[str, Any]]:
    return items[offset : offset + limit]


def build_paginated_response(items_slice: List[Dict[str, Any]], total: int, limit: int, offset: int) -> Dict[str, Any]:
    next_cursor = None
    prev_cursor = None
    if offset is not None:
        # next cursor calculated from offset+limit
        try:
            next_cursor = encode_cursor(offset + limit)
        except Exception:
            next_cursor = None
        try:
            prev_offset = max(0, offset - limit)
            prev_cursor = encode_cursor(prev_offset)
        except Exception:
            prev_cursor = None

    return {
        "items": items_slice,
        "total": total,
        "limit": limit,
        "offset": offset,
        "next_cursor": next_cursor,
        "prev_cursor": prev_cursor,
    }


__all__ = [
    "normalize_pagination",
    "apply_filters",
    "sort_items",
    "paginate_items",
    "build_paginated_response",
]
