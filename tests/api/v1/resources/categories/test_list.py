def test_list_categories(client):
    # create a couple of categories to ensure listing works
    client.post("/api/v1/categories", json={"id": "cat_list_1", "name": "C1"})
    client.post("/api/v1/categories", json={"id": "cat_list_2", "name": "C2"})

    res = client.get("/api/v1/categories")
    assert res.status_code == 200
    body = res.json()
    assert "categories" in body
    ids = [c.get("id") for c in body.get("categories", [])]
    assert "cat_list_1" in ids
    assert "cat_list_2" in ids
