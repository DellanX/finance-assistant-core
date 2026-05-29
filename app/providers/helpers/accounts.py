from typing import Any, Dict, List, Optional
from app.core.schemas import NormalizedAccount


def _to_float(v: Any) -> float:
    try:
        return float(v)
    except Exception:
        return 0.0


def normalize_account(raw: Dict[str, Any]) -> NormalizedAccount:
    data = {
        "id": raw.get("id") or raw.get("account_id") or "",
        "name": raw.get("name") or raw.get("label") or None,
        "type": raw.get("type") or raw.get("account_type") or None,
        "balance": _to_float(raw.get("balance") or raw.get("available") or 0.0),
    }
    return NormalizedAccount(**data)


def normalize_accounts(raw_list: Optional[List[Dict[str, Any]]]) -> List[NormalizedAccount]:
    if not raw_list:
        return []
    return [normalize_account(r) for r in raw_list]
