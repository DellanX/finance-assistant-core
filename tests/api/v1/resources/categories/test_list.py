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


def test_list_categories_pagination(client):
    # ensure multiple items exist
    client.post("/api/v1/categories", json={"id": "cat_page_1", "name": "P1"})
    client.post("/api/v1/categories", json={"id": "cat_page_2", "name": "P2"})
    res = client.get("/api/v1/categories?limit=1")
    assert res.status_code == 200
    body = res.json()
    assert "categories" in body
    assert "total" in body and body["total"] >= 1
    assert body.get("limit") == 1
    assert body.get("offset") == 0
    assert isinstance(body.get("next_cursor"), (str, type(None)))
    assert isinstance(body.get("prev_cursor"), (str, type(None)))
