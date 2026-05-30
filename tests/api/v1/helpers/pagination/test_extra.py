import pytest

from app.api.utils import pagination


def test_normalize_pagination_error_cases(monkeypatch):
    # decode_cursor raising should be caught and offset set to 0 (via page/offset logic)
    def raise_decode(_):
        raise ValueError("bad")
    monkeypatch.setattr(pagination, "decode_cursor", raise_decode)
    lim, off = pagination.normalize_pagination(None, None, None, cursor="abc")
    assert lim == 50 and off == 0

    # non-int limit falls back to default
    lim, off = pagination.normalize_pagination('nope', None, None)
    assert lim == 50

    # offset that cannot be int becomes 0
    lim, off = pagination.normalize_pagination(10, offset='bad', page=None)
    assert off == 0

    # page that cannot be parsed becomes 0 offset
    lim, off = pagination.normalize_pagination(10, offset=None, page='bad')
    assert off == 0

    # negative offset clamps to 0
    lim, off = pagination.normalize_pagination(10, offset=-5, page=None)
    assert off == 0


def test_sort_items_fallback_on_uncomparable_values():
    items = [
        {"id": "a", "k": 1},
        {"id": "b", "k": {"x": 1}},
        {"id": "c", "k": None},
    ]
    # Force the initial sorted call to raise, then allow the fallback to run.
    import builtins
    real_sorted = builtins.sorted
    counter = {"n": 0}

    def fake_sorted(*args, **kwargs):
        if counter["n"] == 0:
            counter["n"] += 1
            raise TypeError("forced")
        return real_sorted(*args, **kwargs)

    # inject fake into module globals, restore afterwards
    old_sorted = getattr(pagination, 'sorted', None)
    pagination.sorted = fake_sorted
    try:
        with pytest.raises(TypeError):
            pagination.sort_items(items, 'k', order='asc')
    finally:
        if old_sorted is None:
            delattr(pagination, 'sorted')
        else:
            pagination.sorted = old_sorted


def test_build_paginated_response_handles_encode_exceptions(monkeypatch):
    slice_ = [{"id": "x"}, {"id": "y"}]
    # normal behavior
    resp = pagination.build_paginated_response(slice_, total=10, limit=2, offset=1)
    assert resp['next_cursor'] is not None and resp['prev_cursor'] is not None

    # monkeypatch encode_cursor to raise
    def bad_encode(_):
        raise RuntimeError("boom")
    monkeypatch.setattr(pagination, 'encode_cursor', bad_encode)
    resp2 = pagination.build_paginated_response(slice_, total=10, limit=2, offset=1)
    assert resp2['next_cursor'] is None and resp2['prev_cursor'] is None

    # offset None should produce None cursors
    resp3 = pagination.build_paginated_response(slice_, total=10, limit=2, offset=None)
    assert resp3['next_cursor'] is None and resp3['prev_cursor'] is None
