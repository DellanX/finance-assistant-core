def test_mock_provider_basic(mock_provider):
    from app.providers.registry import get_provider

    pid = mock_provider["id"]
    provider = get_provider(pid)
    assert provider is not None

    # state inspection
    state = provider.get_state()
    assert state["id"] == pid
    assert isinstance(state.get("accounts"), list)

    # discover accounts
    import asyncio
    accounts = asyncio.run(provider.discover_accounts())
    assert isinstance(accounts, list)
    # Ensure at least one account exists
    assert len(accounts) > 0

    # sync transactions for first account
    txs = asyncio.run(provider.sync_transactions(accounts[0]))
    assert isinstance(txs, list)
    # some fixtures include 'tx_c1' or similar ids
    def _tx_id(t):
        if hasattr(t, "model_dump"):
            return t.model_dump().get("id")
        if isinstance(t, dict):
            return t.get("id")
        return getattr(t, "id", None)

    assert any(isinstance(_tx_id(t), str) for t in txs) or txs == []

    # sync positions
    pos = asyncio.run(provider.sync_positions(accounts[0]))
    assert isinstance(pos, list)
    # if positions exist, ensure they have a symbol
    def _pos_symbol(p):
        if hasattr(p, "model_dump"):
            return p.model_dump().get("symbol")
        if isinstance(p, dict):
            return p.get("symbol")
        return getattr(p, "symbol", None)

    if pos:
        assert any(isinstance(_pos_symbol(p), str) for p in pos)
