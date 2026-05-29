def test_delete_label(client):
    client.post("/api/v1/labels", json={"id": "lbl_d", "name": "d", "description": "d"})
    res = client.delete("/api/v1/labels/lbl_d")
    assert res.status_code in (204,)
    res2 = client.get("/api/v1/labels/lbl_d")
    assert res2.status_code == 404
