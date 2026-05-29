def test_create_tag(client):
    payload = {"key": "tag_test", "description": "t", "values": ["a"]}
    res = client.post("/api/v1/tags", json=payload)
    assert res.status_code == 201
    body = res.json()
    assert body.get("key") == "tag_test"
