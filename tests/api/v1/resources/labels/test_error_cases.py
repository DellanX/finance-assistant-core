import app.providers.labels as labels_module


def test_create_label_conflict(client, monkeypatch):
    def bad_create(payload):
        raise ValueError("exists")

    monkeypatch.setattr(labels_module, "create_label", bad_create)
    payload = {"id": "lbl_x", "name": "X", "description": "d"}
    r = client.post("/api/v1/labels", json=payload)
    assert r.status_code == 400


def test_update_label_not_found(client, monkeypatch):
    def bad_update(lid, data):
        raise KeyError("nope")

    monkeypatch.setattr(labels_module, "update_label", bad_update)
    r = client.put("/api/v1/labels/not-there", json={"id": "not-there", "name": "n", "description": "d"})
    assert r.status_code == 404


def test_delete_label_not_found(client, monkeypatch):
    monkeypatch.setattr(labels_module, "delete_label", lambda lid: False)
    r = client.delete("/api/v1/labels/not-there")
    assert r.status_code == 404
