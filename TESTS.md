# Tests Folder Structure

Proposal: mirror the source tree under `tests/` so tests are easy to locate and map to code. Use `pytest` conventions and keep a single `conftest.py` at the repo root `tests/` for shared fixtures.

Layout
- tests/
  - conftest.py                # shared fixtures (TestClient, mock_provider, helpers)
  - unit/
    - providers/
      - mock/                  # provider-specific unit tests & fixtures
        - test_provider.py
      - alpaca/
      - coinbase/
    - core/                    # core logic (allocation, normalization, reconciliation)
      - test_allocation.py
      - test_normalizer.py
    - api/                     # small unit tests for api utilities / pydantic models
      - test_types.py
  - api/
    - v1/                      # tests that mirror `app/api/v1/` routes
      - test_transactions_api.py
      - test_providers_api.py
      - test_portfolios_api.py
  - integration/
    - providers/               # integration-style tests using the `mock` provider (filesystem fixtures)
      - test_provider_discovery.py
    - api/                     # TestClient end-to-end flows (register provider -> aggregate -> allocate)
      - test_end_to_end_flow.py
  - fixtures/
    - mock_data/               # committed small sample fixtures used by providers for deterministic tests
  - tools/                     # test helpers, e.g., factory functions to build provider states

Naming & Conventions
- Files: `test_*.py` or `*_test.py` (prefer `test_*.py`).
- Test classes optional; favor simple functions with fixtures.
- Use `pytest-asyncio` for async tests and `fastapi.testclient.TestClient` (or `httpx.AsyncClient`) for API tests.
- Keep test data under `tests/fixtures/mock_data` to avoid coupling to `app/providers/mock/mock_data` in CI — but keep some samples next to the provider implementation for local debugging.

Fixtures
- `tests/conftest.py` provides:
  - `client` fixture (FastAPI TestClient configured for tests)
  - `mock_provider` fixture (creates disposable mock provider JSON and registers it in `app.providers.registry`)
  - `tmp_path` usage for filesystem isolation

Coordinator lifecycle in tests
- The test suite includes a `coordinator_factory` fixture that returns a lightweight
  `TestCoordinator` suitable for tests. To avoid starting real background loops,
  production `BaseCoordinator` tasks are not started by default.
- Tests that need provider coordinators should opt in by using the `apply_coordinator_factory`
  fixture. Example:

  ```python
  def test_something_with_coordinator(apply_coordinator_factory, mock_provider):
      # apply_coordinator_factory attaches TestCoordinator instances to providers
      # and ensures they are stopped at test teardown.
      pid = mock_provider.get("id")
      # exercise coordinator-dependent behavior here
  ```

  Making `apply_coordinator_factory` opt-in keeps most tests fast and deterministic.

CI Notes
- Run `pytest -q` in CI on PRs. Use caching for dependencies.
- Use markers (`@pytest.mark.integration`) to gate longer integration tests.
