def test_update_tag(client):
    client.post("/api/v1/tags", json={"key": "tag_u", "description": "u", "values": []})
    payload = {"key": "tag_u", "description": "u2", "values": ["x"]}
    res = client.put("/api/v1/tags/tag_u", json=payload)
    assert res.status_code == 200
    body = res.json()
    assert body.get("description") == "u2"
