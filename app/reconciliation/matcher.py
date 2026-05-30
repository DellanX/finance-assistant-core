from typing import List, Dict, Tuple


def _normalize_payee(payee: str) -> str:
    if not payee:
        return ""
    return " ".join(payee.lower().strip().split())


def find_duplicates(transactions: List[Dict]) -> Dict[Tuple, List[Dict]]:
    """Group transactions by a simple fingerprint (date, amount, normalized payee).

    Returns mapping fingerprint -> list of transactions sharing it.
    """
    groups = {}
    for tx in transactions or []:
        date = tx.get("date")
        # use raw numeric amount if possible
        amount = tx.get("amount")
        payee = _normalize_payee(tx.get("payee") or tx.get("description") or "")
        key = (date, float(amount) if amount is not None else None, payee)
        groups.setdefault(key, []).append(tx)
    # return only groups with more than one member as duplicates
    return {k: v for k, v in groups.items() if len(v) > 1}


def dedupe_transactions(transactions: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
    """Return (deduped_list, duplicates_list).

    Deduplication picks the first occurrence as canonical and reports others
    as duplicates.
    """
    seen_keys = set()
    deduped = []
    duplicates = []
    for tx in transactions or []:
        key = (tx.get("date"), float(tx.get("amount")) if tx.get("amount") is not None else None, _normalize_payee(tx.get("payee") or tx.get("description") or ""))
        if key in seen_keys:
            duplicates.append(tx)
        else:
            seen_keys.add(key)
            deduped.append(tx)
    return deduped, duplicates


def apply_corrections(transactions: List[Dict], corrections: List[Dict]) -> List[Dict]:
    """Apply corrections to transactions in-place by matching `id`.

    Each correction should be {"id": tx_id, "updates": {..}}. Returns the
    updated transactions list.
    """
    if not corrections:
        return transactions or []
    tx_map = {tx.get("id"): tx for tx in transactions or []}
    for corr in corrections:
        tid = corr.get("id")
        updates = corr.get("updates") or {}
        if tid in tx_map:
            tx = tx_map[tid]
            tx.update(updates)
    return list(tx_map.values())
