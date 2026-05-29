def test_read_category(client):
    # ensure resource exists
    payload = {"id": "cat_test_r", "name": "Read Cat", "description": "desc"}
    client.post("/api/v1/categories", json=payload)

    res = client.get("/api/v1/categories/cat_test_r")
    assert res.status_code == 200
    body = res.json()
    assert body.get("id") == "cat_test_r"
