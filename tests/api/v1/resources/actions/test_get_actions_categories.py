def test_get_actions_categories_returns_410(client):
    r = client.get("/api/v1/actions/categories")
    assert r.status_code == 410
