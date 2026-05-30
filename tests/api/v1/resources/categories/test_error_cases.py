import app.providers.categories as categories_module


def test_create_category_conflict(client, monkeypatch):
    def bad_create(cid, data):
        raise ValueError("already exists")

    monkeypatch.setattr(categories_module, "create_category", bad_create)
    payload = {"id": "cat_x", "name": "X", "description": "x"}
    r = client.post("/api/v1/categories", json=payload)
    assert r.status_code == 400


def test_update_category_not_found(client, monkeypatch):
    def bad_update(cid, data):
        raise KeyError("nope")

    monkeypatch.setattr(categories_module, "update_category", bad_update)
    r = client.put("/api/v1/categories/not-there", json={"id": "not-there", "name": "n", "description": "d"})
    assert r.status_code == 404


def test_delete_category_not_found(client, monkeypatch):
    monkeypatch.setattr(categories_module, "delete_category", lambda cid: False)
    r = client.delete("/api/v1/categories/not-there")
    assert r.status_code == 404
