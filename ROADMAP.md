# ROADMAP — Finance Assistant Backend

**Created:** 2026-05-29

Refactor Tasks (prepend)
- Reorder `app/api/v1/providers.py` routes so static schema/config routes appear before the dynamic `/{id}` route to avoid accidental route shadowing and make intent explicit.
- Make `app.providers.coordinator` behavior injectable: allow tests to supply a coordinator stub or run coordinators behind a test-friendly adapter so lifecycle methods can be unit tested reliably.
- Extract provider persistence file I/O (writes to `config.json` or provider `config_path`) into a helper module to permit safe mocking and temporary-path injections during tests.

Note: assume no completed features (no tests yet). This roadmap prioritizes building reliable, test-covered primitives first so higher-level automation is safe to implement.

Phase 0 — Foundation (Immediate)
- Objectives: establish test infra, CI, coding standards, and a minimal provider mock harness.
- Deliverables:
  - `pytest` + fixtures, `TestClient` fixtures, `mock` provider fixtures
  - `pyproject.toml` dev deps (pytest, pytest-asyncio, httpx), linting config
  - GitHub Actions workflow for tests and lint
  - Conventions doc: API style (CRUD + action endpoints), naming, module layout
- Success criteria: tests run in CI; new PRs must include tests for changed behavior.

Phase 1 — Core API & Provider Layer
- Objectives: implement full CRUD for primary resources and stabilize provider registry APIs.
- Resources (CRUD): `accounts/ledgers`, `transactions`, `portfolios`, `assets`, `tranches`, `categories`, `labels`, `tags`, `policies`, `strategies` (meta), `providers`.
- Deliverables:
  - Consistent REST CRUD endpoints and OpenAPI models for each resource
  - Provider registry features: register, persist config, create mock provider via API
  - End-to-end tests for provider discovery, account listing, transactions aggregation
- Success criteria: all resources have list/get/create/update/delete and are covered by unit+API tests.

Phase 2 — Normalization, Correction & Allocation Engine
- Objectives: implement data normalization, reconciliation (correction layer), and allocation engine.
- Deliverables:
  - Normalizers/adapters per-provider with unit tests and sample fixtures
  - Reconciliation layer: optimistic transactions, patching API, and cost-basis reconstruction
  - Allocation engine: declarative rules (percentage/priority), allocation records, allocation history API
  - Tests: allocation rules unit tests, allocation integration test (income -> allocations)
- Success criteria: allocation engine passes deterministic unit tests and preserves traceability of dollars.

Phase 3 — Strategy System & Execution Engine
- Objectives: YAML-based strategies with triggers/conditions/actions, dry-run, execution logs, and conflict handling.
- Deliverables:
  - Strategy parser + schema validation (Pydantic/JSON Schema)
  - Strategy executor service with dry-run and logs
  - API endpoints: CRUD for strategies, execute/dryrun endpoints, execution history
  - Tests: strategy parser, action execution, conflict resolution scenarios
- Success criteria: strategies can be authored, validated, dry-run, and executed deterministically in tests.

Phase 4 — Integrations & Home Assistant Add-on
- Objectives: add production integrations (Alpaca, Coinbase, Actual), add Home Assistant addon support and entity/event model.
- Deliverables:
  - Integration adapters with config schemas and integration tests (or recorded fixtures)
  - Home Assistant add-on Docker image and mapping to HA entities/events
  - Websocket channel for live events and strategy previews
- Success criteria: at least two production integrations with CI-verified adapters and HA add-on artifact.

Phase 5 — Frontend & UX
- Objectives: dashboard, strategy editor, provider management UI.
- Deliverables:
  - Dashboard: net worth, portfolio performance, allocation visualizer
  - Strategy editor: YAML editor with validation and dry-run panel
  - Provider management UI: add/remove providers, view sync status, view provider schemas
- Success criteria: core user flows are usable and validated by user acceptance tests.

Phase 6 — Hardening, Performance & Release
- Objectives: optimize for target hardware, add observability, finalize docs and release pipeline.
- Deliverables:
  - Performance testing harness, profiling, memory/CPU budgets for Raspberry Pi 4
  - Observability: structured logs, metrics endpoints, tracing hooks
  - Documentation: API docs, contributor guide, deployment guides (docker, add-on)
  - Release automation and tagging

Roadmap Notes & Priorities
- Always ship tests with behavior changes — tests are the source of truth for "done".
- Prioritize provider adapters + normalization early — they enable everything else.
- Keep API resources CRUD-first; add custom action endpoints only where side effects are required (e.g., `/actions/{id}/execute`).
- Break large features into 1–2 week milestones for quick feedback.

Immediate next actions (short-term)
- Finalize mapping of existing API modules to FEATURE requirements (gap report).
- Create minimal CI workflow to run tests when PRs are opened.
- Draft a contributor/dev guide describing how to add providers, tests, and API routes.
