def test_list_labels(client):
    client.post("/api/v1/labels", json={"id": "lbl_l1", "name": "l1", "description": "d"})
    client.post("/api/v1/labels", json={"id": "lbl_l2", "name": "l2", "description": "d"})
    res = client.get("/api/v1/labels")
    assert res.status_code == 200
    body = res.json()
    assert "labels" in body
    ids = [l.get("id") for l in body.get("labels", [])]
    assert "lbl_l1" in ids
    assert "lbl_l2" in ids
