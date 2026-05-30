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

API tests: endpoint-per-file guideline
- For API/resource tests under `tests/api/v1/resources/`, prefer one test file per endpoint or route-action.
  - Example: `tests/api/v1/resources/actions/test_get_actions.py` for `GET /api/v1/actions`
    and `tests/api/v1/resources/actions/test_execute_refresh.py` for `POST /api/v1/actions/refresh/execute`.
  - This makes it easier to map failing tests to individual endpoints and supports focused reviews.

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

OpenAPI documentation requirements
- All API changes that introduce or modify endpoints MUST include OpenAPI documentation (Pydantic models and path/operation descriptions). Tests should exercise the OpenAPI spec generation (e.g., load `/openapi.json` and assert the new paths and schemas exist).
- Tests should validate response shapes against the operation schemas where practical (e.g., ensure `response_model` matches actual output structures).

OpenAPI tests guidance
- For every resource that exposes list endpoints (providers, transactions, ledgers, provider accounts, categories, tags, labels, actions, tranches, strategies, snapshots, portfolios, reconciliation, etc.), add an OpenAPI-focused test file that verifies:
  - The path appears in `/openapi.json` and the `GET` operation is present.
  - The `GET` operation documents pagination query parameters (`limit`, `offset`/`page`, `cursor`) — at least `limit` or `cursor` must be present.
  - The `GET` response for `200` is defined (has a schema) so clients can generate typed bindings.

- Naming: prefer `test_openapi.py` next to the resource's `test_list.py`. If the test becomes large (>~300-500 lines) split into `test_openapi_params.py`, `test_openapi_responses.py`, etc., or use `test_openapi_{resource}.py`.

Example location:
- `tests/api/v1/test_openapi_resources.py` — asserts common pagination params for all list endpoints.

These tests are lightweight (parse JSON OpenAPI spec) and are fast to run in CI; they ensure schema documentation keeps parity with implementation.

Response shape tests (requirements)
- All API list and CRUD endpoints MUST have automated tests that validate the runtime JSON shape of successful responses against the intended Pydantic models / envelope shapes. These tests complement OpenAPI spec tests and guard against regressions in serialization or response construction.

- Canonical list envelope shape:
  - All list endpoints SHOULD return an object with pagination metadata and a resource array. At minimum include:
    - pagination metadata: `total` (int), `limit` (int|null), `offset` (int), `next_cursor` (string|null), `prev_cursor` (string|null)
    - resource array: either a generic `items` property or a resource-keyed array (e.g., `providers`, `transactions`, `ledgers`).
  - Example minimal envelope:

    ```json
    {
      "providers": [ {"id": "p1", "name": "One"} ],
      "total": 1,
      "limit": 50,
      "offset": 0,
      "next_cursor": null,
      "prev_cursor": null
    }
    ```

- Test types to include for each endpoint:
  - OpenAPI schema presence: `/openapi.json` documents the operation and response schema (already covered by OpenAPI tests).
  - Runtime response conformance: call the endpoint with `TestClient` and assert the JSON body contains the expected envelope keys and that the resource objects validate against the corresponding Pydantic model (e.g., `ProviderResponse`, `TransactionResponse`).
  - No-pagination case: assert that calling the list endpoint with no pagination params still returns a valid envelope (populated `limit` may be `null` or defaulted depending on implementation), so clients receive consistent shapes.
  - Paginated case: call the endpoint with `limit` (and/or `cursor`) and assert `limit`, `offset`, `next_cursor`/`prev_cursor` are present and `items`/resource-array length matches `limit` (or fewer on last page).
  - Error cases: invalid pagination or filter params should return documented error codes (400/422) and not produce mismatched shapes.

- Direct function compatibility tests:
  - Some internal callers or unit tests may import and call endpoint functions directly (bypassing FastAPI serialization). Add compatibility tests where such direct calls are used, asserting the function either returns an envelope-shaped dict or the legacy shape expected by the caller. If necessary, update callers to accept the envelope shape and mark legacy acceptance tests accordingly.

- Test organization & naming
  - Place shape tests next to the resource tests (`tests/api/v1/resources/<resource>/test_list_shape.py`), or group small shape assertions into `test_list.py` for the resource. For many endpoints, a single file `test_openapi.py` + `test_shape.py` per resource is sufficient.

These requirements ensure both documentation parity and runtime compatibility for clients and internal callers.


Pagination, filtering, sorting — testing guidelines
- All list-style endpoints (resource listing, provider accounts, transactions, ledgers, etc.) MUST be covered by tests that verify pagination, filtering and sorting behavior.
- Tests should assert:
  - presence of pagination query parameters (`limit`, `offset` or `page`) and that responses include pagination metadata (e.g., `total`, `limit`, `offset`/`page`).
  - filtering returns a subset matching filters and combined filters behave as expected.
  - sorting by fields produces a stable order; tests should verify ascending/descending order and that paging across sorted results is stable (no duplicates or missing items when stepping pages).
  - edge cases: `limit=0`, out-of-range `page`/`offset`, invalid filter values — endpoints should return appropriate HTTP errors (400) or empty results as documented.

Example test locations:
- `tests/api/v1/resources/transactions/test_list_pagination.py`
- `tests/api/v1/resources/providers/test_accounts_pagination.py`

