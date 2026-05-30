import app.providers.tags as tags_module


def test_create_tag_conflict(client, monkeypatch):
    def bad_create(key, data):
        raise ValueError("exists")

    monkeypatch.setattr(tags_module, "create_tag", bad_create)
    payload = {"key": "tk", "description": "d", "values": []}
    r = client.post("/api/v1/tags", json=payload)
    assert r.status_code == 400


def test_update_tag_not_found(client, monkeypatch):
    def bad_update(key, data):
        raise KeyError("nope")

    monkeypatch.setattr(tags_module, "update_tag", bad_update)
    r = client.put("/api/v1/tags/not-there", json={"key": "not-there", "description": "d", "values": []})
    assert r.status_code == 404


def test_delete_tag_not_found(client, monkeypatch):
    monkeypatch.setattr(tags_module, "delete_tag", lambda key: False)
    r = client.delete("/api/v1/tags/not-there")
    assert r.status_code == 404
