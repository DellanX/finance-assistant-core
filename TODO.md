# TODO — Server Inventory & Next Steps

**Updated:** 2026-05-29

Refactor Tasks (high priority, prepend to roadmap/todo)
- Reorder static provider routes: move `/api/v1/providers/{id}/config/schema` and other static routes before the dynamic `/{id}` route in `app/api/v1/providers.py` to avoid route shadowing and make endpoints testable.
- Make `app.providers.coordinator` lifecycle injectable/testable: expose a pluggable loop/runner or provide sync wrappers so start/stop/refresh can be unit-tested without timing issues.
- Isolate provider persistence I/O: factor filesystem writes in `app/providers/registry.py` and `app/providers/mock/provider.py` into a small I/O helper so tests can monkeypatch or use a temporary directory without touching package files.

Summary
- Inventory of server endpoints completed: scanned `app/docs/FEATURES.md`, `app/main.py`, `app/api/router.py`, and `app/api/v1/*` to collect implemented modules.

API modules discovered
- app/api/v1/transactions
- app/api/v1/portfolios
- app/api/v1/tranches
- app/api/v1/ledgers
- app/api/v1/providers
- app/api/v1/actions
- app/api/v1/categories
- app/api/v1/tags
- app/api/v1/labels
- app/api/v1/strategies
- app/api/v1/snapshots
- app/api/v1/mock
- app/api/v1/health
- app/api/v1/schemas

Tasks
- [x] Inventory server endpoints — completed 2026-05-29
- [ ] Map features to FEATURES.md
- [ ] Update FEATURES.md
- [ ] Implement missing endpoints
- [ ] Add unit tests
- [ ] Add integration tests
- [ ] Add CI for tests
- [ ] Document API (OpenAPI / docs)

Next steps
- Scan each `app/api/v1/*.py` to list endpoints and supported operations.
- Map implemented endpoints to the feature list in `app/docs/FEATURES.md`.
- Produce a gap report (missing features vs implemented endpoints).
- Prioritize missing work and create focused tasks/PRs.

Notes
- Registry and provider coordinators are started from `app/main.py` on startup.
- Router registrations live in `app/api/router.py`.

API Endpoints Inventory (mapped to `/api`)
- `/health` (GET) — basic app health (from `app/main.py`).
- `/api/v1/health` (GET) — API health + provider statuses (`app/api/v1/health.py`).

- `/api/v1/transactions` (GET) — aggregate transactions across active providers; optional `ledger_id` query param (`app/api/v1/transactions.py`).
- `/api/v1/portfolios` (GET) — aggregated holdings, cash/investment balances, holdings list (`app/api/v1/portfolios.py`).
- `/api/v1/tranches` (GET) — placeholder (returns empty list) (`app/api/v1/tranches.py`).
- `/api/v1/ledgers` (GET) — list discovered accounts/ledgers from providers (`app/api/v1/ledgers.py`).

- `/api/v1/providers` (GET) — list active providers (`app/api/v1/providers.py`).
- `/api/v1/providers` (POST) — create provider instance for an integration (supports `mock` fallback) (`app/api/v1/providers.py`).
- `/api/v1/providers/{id}` (GET) — provider metadata (`app/api/v1/providers.py`).
- `/api/v1/providers/{id}/accounts` (GET) — provider accounts (`app/api/v1/providers.py`).
- `/api/v1/providers/{id}/config` (GET, PUT) — read/update provider config (`app/api/v1/providers.py`).
- `/api/v1/providers/{id}/config/schema` (GET) — provider config schema (pydantic models in `app/api/v1/schemas.py` / `app/providers/*/config`).
- `/api/v1/providers/{id}` (DELETE) — delete provider (stops coordinator and unregisters) (`app/api/v1/providers.py`).

- `/api/v1/actions` (GET) — list core + integration actions (`app/api/v1/actions.py`).
- `/api/v1/actions/{action_id}/execute` (POST) — execute an action (core or integration) (`app/api/v1/actions.py`).
- `/api/v1/actions/{provider_id}` (GET) — list actions available for a provider instance (registered integration+core) (`app/api/v1/actions.py`).

- `/api/v1/categories` (GET, POST, GET /{id}, PUT /{id}, DELETE /{id}) — CRUD for categories (`app/api/v1/categories.py`).
- `/api/v1/tags` (GET, POST, GET /{key}, PUT /{key}, DELETE /{key}) — CRUD for tags (`app/api/v1/tags.py`).
- `/api/v1/labels` (GET, POST, GET /{id}, PUT /{id}, DELETE /{id}) — CRUD for labels (`app/api/v1/labels.py`).

- `/api/v1/strategies` (GET) — placeholder (returns empty list) (`app/api/v1/strategies.py`).
- `/api/v1/snapshots` (GET) — placeholder (returns empty list) (`app/api/v1/snapshots.py`).
- `/api/v1/mock/state/{provider_id}` (GET, POST) — inspect/update mock provider state (`app/api/v1/mock.py`).

- `/api/v1/schemas/providers` (GET) — list available integration schemas (`app/api/v1/schemas.py`).
- `/api/v1/schemas/providers/{integration}` (GET) — get a specific integration's schema (`app/api/v1/schemas.py`).

Coverage notes
- Several endpoints are implemented with concrete logic (`transactions`, `portfolios`, `ledgers`, `providers`, `actions`, `categories`, `tags`, `labels`, `schemas`, `mock`).
- Many higher-level features from `app/docs/FEATURES.md` are currently placeholders: `tranches`, `strategies`, `snapshots` are stubs.
- Business logic such as allocation engine, policy evaluation, cost-basis reconstruction, and budgeting do not appear implemented in the API layer yet.

Test Plan (detailed)
Goal: provide unit, integration, and API tests to validate provider adapters, normalization, allocation, and strategy behavior.

Structure
- `tests/unit/` — unit tests for small modules (provider adapters, `app.providers.*`, `app.core.*` if present).
- `tests/integration/` — integration tests using the `mock` provider and filesystem fixtures to simulate provider state files.
- `tests/api/` — API-level tests using `fastapi.testclient.TestClient` to exercise routes and validate JSON shapes and error conditions.

Priority test cases (start here)
- Provider adapter unit tests
	- `app.providers.mock.provider`: test `discover_accounts`, `sync_transactions`, `sync_positions`, `get_state`, `update_state` behaviors using the `mock_data` fixtures.
	- Any other provider adapters (alpaca, coinbase) should have smoke tests for parsing their sample/manifest data.

- Registry and coordinator tests
	- `app.providers.registry`: test provider registration, `active_providers`, `get_provider_config`, `persist_provider_config`, and `coordinator` lifecycle (start/stop/refresh) using mocks.

- Normalization and aggregation
	- `app.api.v1.transactions`: unit tests ensuring transactions are aggregated and filtered by `ledger_id`.
	- `app.api.v1/portfolios` and `ledgers`: tests for balances and position value calculations (mock provider positions).

- Actions API
	- `app.api.v1.actions`: tests for listing core and integration actions and executing core actions like `refresh`, `export_state`, and integration-level execute paths (use `mock` provider that has action handlers or `execute_action` implemented).

- CRUD resources
	- `categories`, `tags`, `labels`: full CRUD tests, including error branches (404, 400) and validation using the Pydantic models in `app/api/v1/types.py`.

- Schemas and provider creation
	- `schemas` endpoints: test listing and fetching integration schemas.
	- `providers` POST endpoint: test creating a `mock` provider via POST and cleanup (file creation in `app/providers/mock/mock_data`).

- API integration tests
	- Full flow tests: start app in TestClient, register a `mock` provider with known transactions/positions, call `/api/v1/transactions`, `/api/v1/portfolios`, assert expected shapes and derived fields.

Test infra and tooling
- Use `pytest` as the test runner.
- Add `pytest` and `httpx` / `starlette` test clients to `pyproject.toml` or `requirements-dev.txt`.
- Provide fixtures:
	- `app` — FastAPI app instance from `app.main:app` configured for tests (override registry to avoid starting real coordinators).
	- `mock_provider` — fixture that creates temporary `mock` provider JSON files and registers the provider in `app.providers.registry` for the test duration.
	- `tmp_path` / `tmpdir` — filesystem isolation for provider files.

CI
- Add a GitHub Actions workflow `ci/python-tests.yml` to run `pytest`, linting, and optional coverage reporting.

Deliverables (first pass)
- `tests/` skeleton with key fixtures and example tests for `mock` provider and `transactions` endpoint.
- `pyproject.toml` dev dependencies or `requirements-dev.txt` with `pytest`, `pytest-asyncio`, `httpx`.
- `ci/python-tests.yml` GitHub Actions workflow.

