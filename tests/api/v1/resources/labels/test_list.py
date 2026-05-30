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


def test_list_labels_pagination(client):
    client.post("/api/v1/labels", json={"id": "lbl_page_1", "name": "lp1", "description": "d"})
    client.post("/api/v1/labels", json={"id": "lbl_page_2", "name": "lp2", "description": "d"})
    res = client.get("/api/v1/labels?limit=1")
    assert res.status_code == 200
    body = res.json()
    assert "labels" in body
    assert "total" in body and body["total"] >= 1
    assert body.get("limit") == 1
    assert body.get("offset") == 0
    assert isinstance(body.get("next_cursor"), (str, type(None)))
    assert isinstance(body.get("prev_cursor"), (str, type(None)))
