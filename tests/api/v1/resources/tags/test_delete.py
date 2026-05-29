def test_delete_tag(client):
    client.post("/api/v1/tags", json={"key": "tag_d", "description": "d", "values": []})
    res = client.delete("/api/v1/tags/tag_d")
    assert res.status_code in (204,)
    res2 = client.get("/api/v1/tags/tag_d")
    assert res2.status_code == 404
