import base64
import json
import pytest

from app.api.utils import pagination as pag


def test_cursor_encode_decode_roundtrip():
    for offset in (0, 1, 10, 12345):
        c = pag.encode_cursor(offset)
        assert isinstance(c, str)
        d = pag.decode_cursor(c)
        assert d == offset


def test_normalize_pagination_basic_and_page():
    # default when None
    lim, off = pag.normalize_pagination(None, None, None, None)
    assert lim == 50 and off == 0

    # page conversion
    lim, off = pag.normalize_pagination(10, None, 2, None)
    assert lim == 10 and off == 10

    # offset precedence
    lim, off = pag.normalize_pagination(5, 3, 2, None)
    assert lim == 5 and off == 3

    # cursor decoding
    c = pag.encode_cursor(7)
    lim, off = pag.normalize_pagination(5, None, None, c)
    assert off == 7


def test_apply_filters_contains_and_comparisons():
    items = [
        {"id": "a", "val": 1, "name": "Alpha"},
        {"id": "b", "val": 10, "name": "Beta"},
        {"id": "c", "val": 5, "name": "Alphabet"},
    ]

    # contains
    out = pag.apply_filters(items, {"name": "*pha*"})
    assert {i["id"] for i in out} == {"a", "c"}

    # greater than
    out = pag.apply_filters(items, {"val": ">5"})
    assert {i["id"] for i in out} == {"b"}

    # less than or equal
    out = pag.apply_filters(items, {"val": "<=5"})
    assert {i["id"] for i in out} == {"a", "c"}


def test_sort_items_with_none_and_order():
    items = [{"k": None, "id": "n"}, {"k": 2, "id": "b"}, {"k": 1, "id": "a"}]
    s = pag.sort_items(items, "k", "asc")
    assert [i["id"] for i in s] == ["a", "b", "n"]
    s2 = pag.sort_items(items, "k", "desc")
    assert [i["id"] for i in s2] == ["b", "a", "n"]


def test_paginate_items_and_build_response():
    items = [{"id": f"i{i}"} for i in range(5)]
    slice_ = pag.paginate_items(items, limit=2, offset=1)
    assert [s["id"] for s in slice_] == ["i1", "i2"]

    resp = pag.build_paginated_response(slice_, total=5, limit=2, offset=1)
    # next cursor should encode offset+limit
    assert pag.decode_cursor(resp["next_cursor"]) == 3
    assert pag.decode_cursor(resp["prev_cursor"]) == 0

from app.api.utils.pagination import (
    normalize_pagination,
    apply_filters,
    sort_items,
    paginate_items,
    build_paginated_response,
    encode_cursor,
    decode_cursor,
)


def _make_items():
    return [
        {"id": 1, "name": "Alice", "amount": 10},
        {"id": 2, "name": "Bob", "amount": 20},
        {"id": 3, "name": "Carol", "amount": 15},
        {"id": 4, "name": "Dave", "amount": 5},
    ]


def test_normalize_pagination_page_and_offset():
    limit, offset = normalize_pagination(limit=10, offset=None, page=2, default_limit=5)
    assert limit == 10
    assert offset == 10


def test_cursor_encode_decode_and_normalize():
    # encode a cursor for offset 20
    cur = encode_cursor(20)
    assert isinstance(cur, str)
    dec = decode_cursor(cur)
    assert dec == 20

    # normalize using cursor
    limit, offset = normalize_pagination(limit=5, offset=None, page=None, cursor=cur, default_limit=5)
    assert limit == 5
    assert offset == 20


def test_apply_filters_exact_and_contains_and_comparison():
    items = _make_items()
    # exact
    res = apply_filters(items, {"name": "Bob"})
    assert len(res) == 1 and res[0]["name"] == "Bob"

    # contains
    res2 = apply_filters(items, {"name": "*a*"})
    assert {r["name"] for r in res2} == {"Alice", "Carol", "Dave"}

    # comparison
    res3 = apply_filters(items, {"amount": ">=15"})
    assert {r["id"] for r in res3} == {2, 3}


def test_sort_and_paginate_stable():
    items = _make_items()
    s = sort_items(items, "amount", order="asc")
    assert [i["id"] for i in s] == [4, 1, 3, 2]

    limit, offset = 2, 1
    page = paginate_items(s, limit, offset)
    resp = build_paginated_response(page, total=len(s), limit=limit, offset=offset)
    assert resp["total"] == 4
    assert len(resp["items"]) == 2
