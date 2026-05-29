from typing import Any, Dict, List, Optional
from app.core.schemas import NormalizedTranche


def _to_float(v: Any) -> float:
    try:
        return float(v)
    except Exception:
        return 0.0


def normalize_tranche(raw: Dict[str, Any]) -> NormalizedTranche:
    data = {
        "id": raw.get("id") or raw.get("tranche_id") or "",
        "name": raw.get("name") or None,
        "type": raw.get("type") or None,
        "total_amount": _to_float(raw.get("total_amount") or raw.get("amount") or 0.0),
    }
    return NormalizedTranche(**data)


def normalize_tranches(raw_list: Optional[List[Dict[str, Any]]]) -> List[NormalizedTranche]:
    if not raw_list:
        return []
    return [normalize_tranche(r) for r in raw_list]
