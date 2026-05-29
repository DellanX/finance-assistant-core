def test_create_label(client):
    payload = {"id": "lbl_test", "name": "L", "description": "d"}
    res = client.post("/api/v1/labels", json=payload)
    assert res.status_code == 201
    body = res.json()
    assert body.get("id") == "lbl_test"
