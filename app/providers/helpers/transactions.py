from typing import Any, Dict, List, Optional
from app.core.schemas import NormalizedTransaction


def _to_float(v: Any) -> float:
    try:
        return float(v)
    except Exception:
        return 0.0


def normalize_transaction(raw: Dict[str, Any]) -> NormalizedTransaction:
    data = {
        "id": raw.get("id") or raw.get("transaction_id") or "",
        "date": raw.get("date") or raw.get("timestamp") or None,
        "amount": _to_float(raw.get("amount") or raw.get("value") or 0.0),
        "merchant": raw.get("merchant") or raw.get("description") or None,
        "status": raw.get("status") or "unknown",
    }
    return NormalizedTransaction(**data)


def normalize_transactions(raw_list: Optional[List[Dict[str, Any]]]) -> List[NormalizedTransaction]:
    if not raw_list:
        return []
    return [normalize_transaction(r) for r in raw_list]
