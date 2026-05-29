def test_transactions_and_portfolio_values(client, mock_provider):
    # Ensure transactions endpoint returns the known transaction
    tx_res = client.get('/api/v1/transactions')
    assert tx_res.status_code == 200
    txs = tx_res.json()
    assert any(t.get('id') == 'tx_c1' for t in txs)

    # Fetch portfolio summary and holdings
    pf_res = client.get('/api/v1/portfolios')
    assert pf_res.status_code == 200
    body = pf_res.json()
    summary = body.get('summary', {})
    holdings = body.get('holdings', [])

    # Cash balance comes from the mock volatile_crypto account: 12500.0
    assert abs(summary.get('cash_balance', 0) - 12500.0) < 0.001

    # Investment balance: BTC 0.5*65000 + ETH 4*3500 = 32500 + 14000 = 46500
    assert abs(summary.get('investment_balance', 0) - 46500.0) < 0.001

    # Total value = cash + investment
    assert abs(summary.get('total_value', 0) - 59000.0) < 0.001

    # Verify holdings contain BTC and ETH with expected quantities
    syms = {h['symbol']: h for h in holdings}
    assert 'BTC' in syms
    assert 'ETH' in syms
    assert abs(syms['BTC']['quantity'] - 0.5) < 0.0001
    assert abs(syms['ETH']['quantity'] - 4.0) < 0.0001
