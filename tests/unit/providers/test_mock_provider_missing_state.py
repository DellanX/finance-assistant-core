import asyncio

from app.providers.mock.provider import MockProvider


def test_mock_provider_missing_state_file(tmp_path):
    path = tmp_path / "nope.json"
    # ensure file does not exist
    if path.exists():
        path.unlink()

    prov = MockProvider(str(path))
    # id should be 'error' as per fallback
    assert prov.id == "error"
    state = prov.get_state()
    assert isinstance(state, dict)
    # discover_accounts should return empty list (async)
    res = asyncio.run(prov.discover_accounts())
    assert res == []
