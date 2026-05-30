from app.api.v1.schemas import TransactionResponse, LedgerResponse, AccountResponse
from app.core.schemas import PortfolioResponse
from app.api.v1.types import MockStateResponse


def test_transactions_schema(client, mock_provider):
    res = client.get("/api/v1/transactions")
    assert res.status_code == 200
    txs = res.json()
    tx_list = txs.get("transactions") or txs
    for t in tx_list:
        # should validate against TransactionResponse
        obj = TransactionResponse(**t)
        assert obj.id is not None


def test_ledgers_schema(client, mock_provider):
    res = client.get("/api/v1/ledgers")
    assert res.status_code == 200
    items = res.json()
    ledger_list = items.get("ledgers") or items
    for it in ledger_list:
        obj = LedgerResponse(**it)
        assert obj.id is not None


def test_portfolio_schema(client, mock_provider):
    res = client.get("/api/v1/portfolios")
    assert res.status_code == 200
    body = res.json()
    # validate full response
    resp = PortfolioResponse(**body)
    assert hasattr(resp, "summary")


def test_provider_accounts_schema(client, mock_provider):
    pid = mock_provider["id"]
    res = client.get(f"/api/v1/providers/{pid}/accounts")
    assert res.status_code == 200
    items = res.json()
    accounts = items.get("accounts") or items
    for it in accounts:
        obj = AccountResponse(**it)
        assert obj.id is not None


def test_mock_state_schema(client, mock_provider):
    pid = mock_provider["id"]
    res = client.get(f"/api/v1/mock/state/{pid}")
    assert res.status_code == 200
    body = res.json()
    MockStateResponse(**{"state": body})
