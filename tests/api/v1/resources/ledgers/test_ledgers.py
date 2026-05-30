import asyncio
from app.providers import registry


class PydanticLike:
    def __init__(self, data):
        self._data = data

    def model_dump(self):
        return self._data


class IterablePairs:
    def __init__(self, data):
        self._data = data

    def __iter__(self):
        return iter(self._data.items())


class BadAcc:
    def __iter__(self):
        raise RuntimeError("cant convert")


def make_provider(discover_result, name="Prov"):
    class Prov:
        def __init__(self):
            self.name = name

        async def discover_accounts(self):
            return discover_result

    return Prov()


def test_get_ledgers_with_dict_account(client):
    pid = "p-dict"
    prov = make_provider([{"id": "a1", "name": "A1", "currency": "USD", "balance": 10.0}], name="PD")
    registry.active_providers[pid] = prov
    try:
        r = client.get("/api/v1/ledgers")
        assert r.status_code == 200
        data = r.json()
        items = data.get("ledgers", data)
        assert any(l.get("id") == "a1" and l.get("provider_id") == pid for l in items)
    finally:
        registry.active_providers.pop(pid, None)


def test_get_ledgers_with_pydantic_model_and_iterable_and_bad(client):
    pid = "p-mix"
    acc1 = PydanticLike({"id": "p1", "name": "P1", "currency": "EUR", "balance": 5.0})
    acc2 = IterablePairs({"id": "p2", "name": "P2", "currency": "GBP", "balance": 7.5})
    acc3 = BadAcc()
    prov = make_provider([acc1, acc2, acc3], name="PM")
    registry.active_providers[pid] = prov
    try:
        r = client.get("/api/v1/ledgers")
        assert r.status_code == 200
        data = r.json()
        items = data.get("ledgers", data)
        # p1 and p2 should be present with proper ids
        ids = {l.get("id") for l in items}
        assert "p1" in ids
        assert "p2" in ids
        # bad account produces an entry with empty id
        assert any(l.get("id") == "" for l in items)
    finally:
        registry.active_providers.pop(pid, None)


def test_get_ledgers_pagination(client):
    pid = "p-pag"
    prov = make_provider([
        {"id": "a1", "name": "A1", "currency": "USD", "balance": 10.0},
        {"id": "a2", "name": "A2", "currency": "USD", "balance": 20.0},
    ], name="PP")
    old = registry.active_providers.copy()
    try:
        registry.active_providers.clear()
        registry.active_providers[pid] = prov
        r = client.get("/api/v1/ledgers?limit=1")
        assert r.status_code == 200
        data = r.json()
        assert "ledgers" in data
        assert data.get("limit") == 1
        assert data.get("offset") == 0
        assert isinstance(data.get("next_cursor"), (str, type(None)))
    finally:
        registry.active_providers.clear()
        registry.active_providers.update(old)
