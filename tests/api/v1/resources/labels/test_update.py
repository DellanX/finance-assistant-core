def test_update_label(client):
    client.post("/api/v1/labels", json={"id": "lbl_u", "name": "u", "description": "d"})
    payload = {"id": "lbl_u", "name": "u2", "description": "d2"}
    res = client.put("/api/v1/labels/lbl_u", json=payload)
    assert res.status_code == 200
    body = res.json()
    assert body.get("name") == "u2"
