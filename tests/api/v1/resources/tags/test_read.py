def test_read_tag(client):
    client.post("/api/v1/tags", json={"key": "tag_r", "description": "r", "values": []})
    res = client.get("/api/v1/tags/tag_r")
    assert res.status_code == 200
    body = res.json()
    assert body.get("key") == "tag_r"
