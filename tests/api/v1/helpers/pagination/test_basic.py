import base64
import json

from app.api.utils import pagination


def test_encode_decode_cursor_and_next():
    cur = pagination.encode_cursor(5)
    assert isinstance(cur, str)
    assert pagination.decode_cursor(cur) == 5
    nxt = pagination.make_next_cursor(5, 10)
    assert pagination.decode_cursor(nxt) == 15
    # invalid decode returns 0
    assert pagination.decode_cursor('not-a-cursor') == 0


def test_normalize_pagination_basic():
    # defaults
    lim, off = pagination.normalize_pagination(None, None, None)
    assert lim == 50 and off == 0

    # explicit limit as string
    lim, off = pagination.normalize_pagination('100', None, None)
    assert lim == 100 and off == 0

    # negative or zero limit resets to default
    lim, off = pagination.normalize_pagination(0, None, None)
    assert lim == 50

    # cap at max_limit
    lim, off = pagination.normalize_pagination(10000, None, None, default_limit=50, max_limit=200)
    assert lim == 200

    # page calculation
    lim, off = pagination.normalize_pagination(10, None, 3)
    assert lim == 10 and off == 20

    # offset precedence over page
    lim, off = pagination.normalize_pagination(10, 7, 3)
    assert lim == 10 and off == 7


def test_normalize_with_cursor():
    cur = pagination.encode_cursor(42)
    lim, off = pagination.normalize_pagination(10, None, None, cursor=cur)
    assert off == 42


def test_apply_filters_various():
    items = [
        {"a": 1, "b": "Hello"},
        {"a": 5, "b": "World"},
        {"a": 10, "b": "hello world"},
    ]
    # numeric comparison
    out = pagination.apply_filters(items, {"a": ">=5"})
    assert len(out) == 2

    # contains (case-insensitive)
    out = pagination.apply_filters(items, {"b": "*hello*"})
    assert len(out) == 2

    # exact numeric match (string)
    out = pagination.apply_filters(items, {"a": "5"})
    assert len(out) == 1 and out[0]["a"] == 5

    # invalid comparison should not match
    out = pagination.apply_filters(items, {"a": ">=x"})
    assert len(out) == 0


def test_sort_and_paginate_and_build_response():
    items = [
        {"id": "i1", "val": 2},
        {"id": "i2", "val": 1},
        {"id": "i3", "val": None},
        {"id": "i4", "val": 3},
    ]
    sorted_asc = pagination.sort_items(items, "val", order="asc")
    assert [i["id"] for i in sorted_asc] == ["i2", "i1", "i4", "i3"]

    sorted_desc = pagination.sort_items(items, "val", order="desc")
    assert [i["id"] for i in sorted_desc] == ["i4", "i1", "i2", "i3"]

    # paginate
    slice_ = pagination.paginate_items(sorted_asc, limit=2, offset=1)
    assert [s["id"] for s in slice_] == ["i1", "i4"]

    # build response cursors
    resp = pagination.build_paginated_response(slice_, total=4, limit=2, offset=1)
    assert resp["total"] == 4 and resp["limit"] == 2 and resp["offset"] == 1
    assert pagination.decode_cursor(resp["next_cursor"]) == 3
    assert pagination.decode_cursor(resp["prev_cursor"]) == 0

# end of file
