from typing import Any, Dict, List, Optional
from app.core.schemas import NormalizedAsset


def _to_float(v: Any) -> float:
    try:
        return float(v)
    except Exception:
        return 0.0


def normalize_asset(raw: Dict[str, Any]) -> NormalizedAsset:
    data = {
        "symbol": raw.get("symbol") or raw.get("ticker") or "",
        "name": raw.get("name") or None,
        "currency": raw.get("currency") or None,
        "current_price": _to_float(raw.get("current_price") or raw.get("price") or 0.0),
    }
    return NormalizedAsset(**data)


def normalize_assets(raw_list: Optional[List[Dict[str, Any]]]) -> List[NormalizedAsset]:
    if not raw_list:
        return []
    return [normalize_asset(r) for r in raw_list]
