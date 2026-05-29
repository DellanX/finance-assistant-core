def test_transactions_list(client, mock_provider):
    resp = client.get("/api/v1/transactions")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    # Expect the known transaction from the mock volatile_crypto fixture
    ids = [tx.get("id") for tx in data]
    assert "tx_c1" in ids


def test_transactions_filter_by_ledger(client, mock_provider):
    resp = client.get("/api/v1/transactions", params={"ledger_id": "account_crypto_1"})
    assert resp.status_code == 200
    data = resp.json()
    assert all(tx["ledger_id"] == "account_crypto_1" for tx in data)
