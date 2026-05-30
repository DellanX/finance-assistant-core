from app.api.utils import pagination


def test_make_and_encode_decode_and_negative():
    cur = pagination.make_next_cursor(2, 3)
    assert pagination.decode_cursor(cur) == 5
    # negative offset
    cur2 = pagination.encode_cursor(-1)
    assert pagination.decode_cursor(cur2) == -1


def test_apply_filters_none_and_string_and_less_than():
    items = [
        {"a": 1, "b": "Foo"},
        {"a": 2, "b": "Bar"},
        {"a": 3, "b": "foobar"},
    ]
    # filters None => return same
    out = pagination.apply_filters(items, None)
    assert out == items

    # string equality case-insensitive
    out = pagination.apply_filters(items, {"b": "foo"})
    assert len(out) == 1 and out[0]["a"] == 1

    # less-than comparison
    out = pagination.apply_filters(items, {"a": "<3"})
    assert len(out) == 2

    # less-than-or-equal
    out = pagination.apply_filters(items, {"a": "<=2"})
    assert len(out) == 2

    # cond is explicitly None should match all
    out = pagination.apply_filters(items, {"a": None})
    assert len(out) == 3

    # greater-than
    out = pagination.apply_filters(items, {"a": ">1"})
    assert len(out) == 2


def test_sort_items_no_sort_by_and_fallback_success(monkeypatch):
    items = [
        {"id": "a", "k": 1},
        {"id": "b", "k": 2},
        {"id": "c", "k": None},
    ]
    # when sort_by is falsy, returns original list
    res = pagination.sort_items(items, None)
    assert res is items

    # Force initial sorted to raise once, fallback should succeed
    import builtins
    real_sorted = builtins.sorted
    counter = {"n": 0}

    def fake_sorted(*args, **kwargs):
        if counter["n"] == 0:
            counter["n"] += 1
            raise TypeError("forced")
        return real_sorted(*args, **kwargs)

    old = getattr(pagination, 'sorted', None)
    pagination.sorted = fake_sorted
    try:
        res2 = pagination.sort_items(items, 'k', order='asc')
    finally:
        if old is None:
            delattr(pagination, 'sorted')
        else:
            pagination.sorted = old

    # ensure None-valued items are last and non-none sorted asc
    assert [i['id'] for i in res2] == ['a', 'b', 'c']


def test_paginate_items_bounds():
    items = [{"id": i} for i in range(5)]
    # offset beyond list returns empty
    slice_ = pagination.paginate_items(items, limit=2, offset=10)
    assert slice_ == []
    # offset near end
    slice2 = pagination.paginate_items(items, limit=3, offset=3)
    assert len(slice2) == 2
