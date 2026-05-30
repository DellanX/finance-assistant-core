# Strategy Schema — Finance Assistant

This document defines the YAML strategy schema used by the Strategy System (Phase 3). It describes the canonical structure, trigger/condition/action primitives, execution semantics, context variables, and examples. The schema is intentionally conservative to make strategies safe to author and easy to validate.

## Goals
- Human-friendly YAML syntax for common finance automations.
- Deterministic evaluation order with clear dry-run semantics.
- Safe defaults (dry-run, limited side-effects, capability checks).
- Easy testability: strategies validate against a JSON/Pydantic schema and have unit-tests for parsing, evaluation, and action runners.

## Top-level structure

A strategy is a YAML document with the following top-level keys:

- `id` (optional): stable identifier string (UUID or slug). If omitted the system may generate one.
- `name` (required): short human-readable name.
- `description` (optional): longer human readable description.
- `enabled` (optional, default: true): whether the strategy is active.
- `priority` (optional, integer, default: 100): lower number = higher priority when resolving conflicts.
- `mode` (optional): `single` | `parallel` — determines concurrency semantics for action execution.
- `triggers` (required, list): triggers that cause evaluation.
- `conditions` (optional, list): list of condition expressions; all must be true unless expressed as boolean logic.
- `actions` (required, list): ordered list of actions to execute when conditions pass.
- `variables` (optional): static variables available during evaluation (overridable by triggers).
- `metadata` (optional): free-form metadata for UI, tags, or versioning.
- `max_retries` (optional): how many times to retry transient failures (default 0).
- `run_options` (optional): execution specific flags (e.g., `dry_run_default: true`).

Example skeleton:

```yaml
id: income-allocation-monthly
name: Monthly Income Allocation
description: Allocate incoming income to envelopes and investments
enabled: true
priority: 50
mode: single
triggers:
  - type: on_income
    account: checking_main
conditions:
  - type: numeric_threshold
    expr: "trigger.amount > 0"
actions:
  - type: allocate
    to: [
      { tranche: savings, percent: 30 },
      { tranche: bills, percent: 40 },
      { tranche: invest, percent: 30 }
    ]
  - type: notify
    message: "Allocation completed"
variables:
  default_currency: USD
```

## Triggers
Triggers are event sources that start strategy evaluation. A trigger must declare `type` and type-specific fields.

Common trigger types:

- `on_transaction` — fires on any transaction matching optional filters.
  - fields: `account`, `category`, `min_amount`, `direction` (`credit`|`debit`), `match` (simple wildcard or regex)
  - context: `trigger.transaction` contains the normalized transaction object.

- `on_income` — convenience shorthand for `on_transaction` with `direction: credit` and category heuristics.
  - fields: `account` (optional), `min_amount` (optional), `source` (optional)
  - context: `trigger.amount`, `trigger.transaction`

- `schedule` — cron-like or interval schedules.
  - fields: `cron` (cron expression) or `every` (e.g., `1d`, `1h`), optional `timezone`.

- `threshold` — fires when an account/portfolio metric crosses a threshold.
  - fields: `metric` (e.g., `account.balance`, `portfolio.net_worth`), `operator` (`lt`/`lte`/`gt`/`gte`), `value`

- `portfolio_drift` — fires when portfolio drift exceeds a percent.
  - fields: `portfolio_id`, `tolerance_pct`

- `on_event` — fires when an external event (webhook or HA event) with matching `event_type` occurs.
  - fields: `event_type`, optional `payload_filters`.

Triggers may include filter expressions to limit firing. Trigger objects merge into the evaluation context under `trigger`.

## Conditions
Conditions are boolean predicates that can reference context variables, trigger payload, provider state, or static `variables`.

Supported condition primitives:

- `equals`: compare two expressions.
  - `lhs`, `rhs` (expressions or literals)
- `in`: membership checks (e.g., `category in ['salary', 'interest']`)
- `matches`: regex match, `expr` and `pattern`
- `numeric_threshold`: `expr`, `operator`, `value`
- `has_label`: check labels on transaction/account/asset
- `policy_check`: evaluate a named policy on a resource (e.g., `policy: min-balance`)

Compound logic:
- `and`, `or`, `not` — accept lists or single conditions. Short-circuit evaluation is used.

Expressions may reference variables using a dot-style path, e.g. `trigger.amount`, `provider.state.sync_age`, `portfolio.summary.total_value`.

Example conditions:
```yaml
conditions:
  - type: and
    conditions:
      - type: numeric_threshold
        expr: "trigger.amount"
        operator: ">"
        value: 0
      - type: policy_check
        policy: "min-balance"
        resource: "account:checking_main"
```

## Actions
Actions perform side effects. Each action must include `type` and type-specific parameters. Actions are executed in order; failures follow executor retry/compensation rules (see below).

Core action types (initial set):

- `allocate` — split an amount into tranches or accounts.
  - fields: `amount` (optional: defaults to `trigger.amount`), `to` (list of destinations with `tranche`|`account` and `percent` or `amount`), `strategy_id` (optional)

- `move_funds` — transfer between accounts.
  - fields: `from`, `to`, `amount` (or `percent`), optional `currency`

- `buy` / `sell` — place trade orders via provider.
  - fields: `provider`, `account`, `symbol`, `quantity`|`percent`, `order_type`(`market`|`limit`), `limit_price` (if limit)

- `call_provider_action` — invoke provider-specific action (generic extension point).
  - fields: `provider_id`, `action_name`, `params` (dict), `wait_for_completion` (bool)

- `update_label` — add/update labels on transactions/accounts/assets.
  - fields: `target`, `labels` (dict)

- `emit_event` — emit a platform event (useful for HA or UI hooks).
  - fields: `event_type`, `payload`

- `notify` — send a user notification via configured channels.
  - fields: `message`, `level` (`info`|`warning`|`error`), `channels`

- `delay` / `wait` — pause execution for a specified duration or until a condition is true (use sparingly).

Action result semantics:
- Actions return a standard result object: `{ ok: bool, id?: str, details?: dict, errors?: list }`.
- On failure: executor consults `max_retries` and the action's `retry` policy (if provided). Some actions may be marked `compensating: true` to indicate they are allowed as rollbacks.

Idempotency and safety:
- For operations that can be non-idempotent (e.g., trades, transfers), providers should expose idempotency keys or the executor should attach a unique `execution_id` to the action request to allow providers to deduplicate.

## Execution semantics

- Trigger received → strategy lookup by id (or evaluate candidates) → validate enabled/priority/guardrails.
- Build execution `context` containing: `trigger`, `variables`, `providers` (resolved), `now` (ISO timestamp), `execution_id` (UUID).
- Evaluate `conditions`. If false, record a no-op execution log and stop.
- Execute `actions` in order.
  - For `mode: single`, acquire a per-resource lock where applicable (e.g., per-account or per-portfolio) to avoid concurrent modifications.
  - For `mode: parallel`, execute non-dependent actions concurrently (executor must detect conflicts by resource target).
- For each action, collect results and attach to the execution log.
- On success: persist execution record, emit events, and indicate success via websocket/metrics.
- On partial failure: follow retry rules; if unrecoverable, mark execution as failed and optionally run compensating actions if configured.

Dry-run:
- If `run_options.dry_run_default` is true or user requests dry-run explicitly, evaluate conditions and simulate actions. No external state is changed; execution logs indicate `dry_run: true` and include simulated provider responses.

Audit & history:
- Every execution should produce an `ExecutionRecord` persisted to storage with: `strategy_id`, `execution_id`, `trigger`, `start_ts`, `end_ts`, `status`, `actions_results`, `dry_run`.

## Context variables
Available in expressions and action templates:
- `trigger` — the trigger payload (transaction, schedule info, metric values).
- `providers` — mapping of provider_id -> lightweight provider state (sync status, capabilities).
- `accounts`, `portfolios` — optionally injected snapshot summaries for referenced resources.
- `variables` — strategy static variables and overridable defaults.
- `now` — current ISO timestamp.
- `execution_id` — generated id for this run.

Example expression: `trigger.amount * (variables.invest_pct / 100)`

## Validation rules
- Strategies must pass JSON Schema / Pydantic validation before being accepted.
- Reject strategies that request disallowed `call_provider_action` calls unless the user explicitly grants capability.
- Enforce a maximum number of actions (e.g., 50) and max composite depth to prevent runaway strategies.

## Examples
### Income allocation (full)
```yaml
id: income-allocation-monthly
name: Monthly Income Allocation
description: Allocate incoming income to envelopes and investments
enabled: true
priority: 50
triggers:
  - type: on_income
    account: checking_main
    min_amount: 1
conditions:
  - type: numeric_threshold
    expr: "trigger.amount"
    operator: ">"
    value: 0
actions:
  - type: allocate
    amount: "{{ trigger.amount }}"
    to:
      - tranche: bills
        percent: 40
      - tranche: savings
        percent: 30
      - tranche: invest
        percent: 30
  - type: emit_event
    event_type: allocation_completed
    payload:
      amount: "{{ trigger.amount }}"
```

### Rebalance strategy (drift)
```yaml
id: rebalance-monthly
name: Monthly Rebalance
triggers:
  - type: schedule
    cron: "0 2 1 * *" # first day of month 02:00
conditions:
  - type: portfolio_drift
    portfolio_id: all_investments
    tolerance_pct: 5
actions:
  - type: call_provider_action
    provider_id: alpaca
    action_name: rebalance_portfolio
    params:
      portfolio_id: all_investments
      tolerance_pct: 5
```

## Testing notes (what to unit test before implementation)
- Parser: acceptance of valid YAML and rejection of invalid types/fields.
- Condition evaluator: correctness for atomic and compound conditions.
- Action runner: mocked provider integrations should be used to test action outcomes, idempotency and retry behavior.
- Dry-run: ensure actions are simulated and no provider methods that mutate state are called.

## Security & Permissions
- Strategy creation/updates require authenticated UI/API calls and a capability check for actions with write scope.
- `call_provider_action` and `buy`/`sell` actions must only be allowed for strategies created by users with `write_provider` permission or admin-specified scopes.
- Limit exposure of provider credentials in logs; redact secrets in execution records.

## Open design questions
- Global vs per-strategy rate limits for actions to prevent accidental ddos on provider APIs.
- How to model long-running actions that require human confirmation (2-step flows).
- Versioning strategies: how to migrate previously stored strategy metadata when schema changes.

---

For the next step I can (pick one):
- Produce a JSON Schema / Pydantic models from this spec.
- Draft test skeletons for parser, condition evaluator, action runners.
- Start implementing a minimal parser and executor for dry-run mode.

Tell me which you'd like to do next, or ask for expansions on any section above.
