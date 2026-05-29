from typing import Any, Dict, List, Optional
from app.core.schemas import NormalizedLedger


def _to_float(v: Any) -> float:
    try:
        return float(v)
    except Exception:
        return 0.0


def normalize_ledger(raw: Dict[str, Any]) -> NormalizedLedger:
    data = {
        "id": raw.get("id") or raw.get("ledger_id") or "",
        "name": raw.get("name") or raw.get("label") or None,
        "currency": raw.get("currency") or None,
        "balance": _to_float(raw.get("balance") or 0.0),
        "accounts_count": int(raw.get("accounts_count") or raw.get("account_count") or 0),
    }
    return NormalizedLedger(**data)


def normalize_ledgers(raw_list: Optional[List[Dict[str, Any]]]) -> List[NormalizedLedger]:
    if not raw_list:
        return []
    return [normalize_ledger(r) for r in raw_list]
