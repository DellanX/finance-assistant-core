def test_read_label(client):
    client.post("/api/v1/labels", json={"id": "lbl_r", "name": "r", "description": "d"})
    res = client.get("/api/v1/labels/lbl_r")
    assert res.status_code == 200
    body = res.json()
    assert body.get("id") == "lbl_r"
