def test_create_category(client):
    payload = {"id": "cat_test", "name": "Test Cat", "description": "desc"}
    res = client.post("/api/v1/categories", json=payload)
    assert res.status_code == 201
    body = res.json()
    assert body.get("id") == "cat_test"
