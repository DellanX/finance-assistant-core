from typing import Any, Dict, List, Optional


def _to_float(v: Any) -> float:
    try:
        return float(v)
    except Exception:
        return 0.0


def normalize_position(raw: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "symbol": raw.get("symbol") or raw.get("ticker") or "",
        "quantity": _to_float(raw.get("quantity") or raw.get("qty") or 0.0),
        "cost_basis": _to_float(raw.get("cost_basis") or raw.get("cost") or 0.0),
        "current_price": _to_float(raw.get("current_price") or raw.get("price") or 0.0),
        "raw": raw,
    }


def normalize_positions(raw_list: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    if not raw_list:
        return []
    return [normalize_position(r) for r in raw_list]
