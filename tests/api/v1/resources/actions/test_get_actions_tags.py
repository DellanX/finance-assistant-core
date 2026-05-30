def test_get_actions_tags_returns_410(client):
    r = client.get("/api/v1/actions/tags")
    assert r.status_code == 410
