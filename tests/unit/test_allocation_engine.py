from app.allocation.engine import AllocationRule, apply_allocations


def test_apply_allocations_simple_split():
    rules = [AllocationRule(target="A", percent=70), AllocationRule(target="B", percent=30)]
    res = apply_allocations(100.0, rules)
    assert len(res) == 2
    assert res[0]["target"] == "A"
    assert res[1]["target"] == "B"
    assert sum(r["amount"] for r in res) == 100.0
    assert res[0]["amount"] == 70.0
    assert res[1]["amount"] == 30.0


def test_apply_allocations_rounding():
    rules = [AllocationRule(target="X", percent=33), AllocationRule(target="Y", percent=33), AllocationRule(target="Z", percent=34)]
    res = apply_allocations(100.0, rules)
    assert sum(r["amount"] for r in res) == 100.0
