from dataclasses import dataclass
from typing import List, Dict


@dataclass
class AllocationRule:
    target: str
    percent: float  # 0-100
    priority: int = 0


def apply_allocations(amount: float, rules: List[AllocationRule]) -> List[Dict[str, float]]:
    """Apply percent-based allocation rules to `amount` deterministically.

    Returns list of dicts: {"target": str, "amount": float}.
    """
    if amount is None:
        return []
    total_pct = sum(max(0.0, r.percent) for r in rules)
    if total_pct <= 0:
        return []

    # Normalize percentages to sum to 100 if they don't already
    normalized = [r.percent / total_pct for r in rules]
    # Compute raw allocations
    raw_allocs = [amount * p for p in normalized]
    # Round to 2 decimals and adjust last item to ensure sum equals amount
    rounded = [round(v, 2) for v in raw_allocs]
    diff = round(amount - sum(rounded), 2)
    if rounded:
        rounded[-1] = round(rounded[-1] + diff, 2)

    return [{"target": r.target, "amount": rounded[i]} for i, r in enumerate(rules)]
