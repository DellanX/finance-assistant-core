def test_update_category(client):
    payload = {"id": "cat_test_u", "name": "Up Cat", "description": "desc"}
    client.post("/api/v1/categories", json=payload)

    payload2 = {"id": "cat_test_u", "name": "Updated", "description": "d2"}
    res = client.put("/api/v1/categories/cat_test_u", json=payload2)
    assert res.status_code == 200
    body = res.json()
    assert body.get("name") == "Updated"
