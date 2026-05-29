def test_delete_category(client):
    payload = {"id": "cat_test_d", "name": "Del Cat", "description": "desc"}
    client.post("/api/v1/categories", json=payload)

    res = client.delete("/api/v1/categories/cat_test_d")
    assert res.status_code in (204,)

    # ensure gone
    res2 = client.get("/api/v1/categories/cat_test_d")
    assert res2.status_code == 404
