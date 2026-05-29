def test_list_tags(client):
    client.post("/api/v1/tags", json={"key": "tag_l1", "description": "l1", "values": []})
    client.post("/api/v1/tags", json={"key": "tag_l2", "description": "l2", "values": []})
    res = client.get("/api/v1/tags")
    assert res.status_code == 200
    body = res.json()
    assert "tags" in body
    keys = [t.get("key") for t in body.get("tags", [])]
    assert "tag_l1" in keys
    assert "tag_l2" in keys
