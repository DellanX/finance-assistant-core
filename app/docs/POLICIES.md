# Policies — Constraints for Strategies

This document defines the Policy object, its constraint types, merge and conflict-detection behavior, and how strategies should consume policy-derived constraints.

Goals
- Policies are declarative constraint/spec objects attached to resources (accounts, assets, tranches, providers, tags).
- Policies do NOT prescribe actions; they only express constraints (e.g., `min_flexible`, `min_hold_period`, `min_sell_profit_pct`).
- Strategies query policies and decide how to react when constraints apply.
- Provide validation and conflict detection to avoid over-constrained systems.

Policy Model (concept)
- `id`: stable identifier (slug/UUID)
- `name`: human-readable
- `enabled`: bool
- `priority`: int (optional, lower = higher precedence)
- `targets`: list of resource selectors (e.g., `account:checking_main`, `asset:BTC`, `tranche:emergency`, `tag:taxable`)
- `constraints`: typed dictionary of zero-or-more constraints
- `conditional_rules`: optional list of `{ condition, constraints }`
- `metadata`: free-form (created_by, timestamps, description)
- `effective_from` / `effective_to` (optional)

Typed Constraints (examples)
- `min_flexible: number` — keep at least this amount liquid in the targeted resource
- `min_hold_period_days: int` — minimum hold time before sale
- `min_sell_profit_pct: number` — require estimated profit pct to sell
- `max_allocation_pct: number` — do not allocate more than this % of a resource
- `min_allocation_amount: number` — minimum $ amount to allocate
- `weights: object` — optional map of resource -> weight used by strategies when splitting allocations

Conditional rules
- Each rule contains a `condition` expression and a `constraints` block.
- Conditions use the same expression language as strategies and may reference the `resource` snapshot and `trigger` context.

PolicyEvaluator & ConstraintDecision
- The system exposes `PolicyEvaluator.evaluate(resource_selector, context)` which:
  1. Collects active policies that target the resource
  2. Merges constraints by precedence and priority
  3. Returns a `ConstraintDecision` object describing the effective constraints and applied policy ids

`ConstraintDecision` (recommended shape)
- `allowed: bool` — true unless a hard deny exists (policies generally do not deny; this supports regulatory holds)
- `constraints: dict` — merged typed constraints (see above)
- `applied_policies: list[str]` — policy ids used in the merge
- `applied_rules: list[str]` — conditional rule ids applied
- `warnings: list[dict]` — optional messages (e.g., conflicts suppressed by precedence)
- `blocked_reasons: list[str]` — if `allowed` is false
- `requires_approval: bool` and `approval_meta` (if applicable)

Merge semantics
- Collect applicable policies, sort by scope specificity and `priority` (resource-specific → parent/group → provider → global; lower priority wins within same scope).
- For each typed constraint, the first (highest-precedence) non-null value wins unless the field is a mergeable collection (e.g., `weights`, which are merged by additive/normalized rules).
- `weights` merging: accumulate weights from applicable policies and renormalize; allow strategy to decide to honor or override.
- `min_*` constraints are additive in feasibility checks (e.g., min_flexible + other required reserves must fit available funds).
- `deny` is supported as an exceptional constraint — if present on any active policy with sufficient precedence, `allowed` becomes false.

Static validation (on create/update)
- Enforce types and ranges (`min_flexible >= 0`, `0 <= max_allocation_pct <= 100`).
- Disallow self-contradictory fields in the same policy (e.g., `min_flexible > some policy-local max_allocation that makes all actions impossible`).
- If validation detects easy contradictions, reject with clear error messages.

Dynamic conflict detection (FeasibilityChecker)
- After merge, run feasibility checks against a resource snapshot:
  - Monetary feasibility: sum of required minima and reserved amounts <= available balance.
  - Percent feasibility: ensure min_percent allocations ≤ 100 and max caps permit required minima.
  - Hold period and profit constraints: evaluate whether requested sells or rebalances would violate time/profit constraints.
- Provide diagnostics with severity levels: `error` (infeasible), `warning` (likely problematic), `info`.
- Options when infeasible:
  - Reject policy update (default safe behavior)
  - Accept but mark policy as `invalid` with attached diagnostic (requires admin action)
  - Auto-resolve using priorities (suppress lower-priority constraints) and emit warnings

Strategy interaction pattern
1. Strategy builds a tentative `Action` with targets, desired `amount` or `percent`, and `fallback` behavior.
2. Strategy calls `PolicyEvaluator.evaluate(target, context)` to obtain `ConstraintDecision`.
3. Strategy inspects `constraints` and `allowed` and then applies its fallback logic:
   - `on_insufficient_funds`: reduce, route, defer, require_approval, or abort
   - `on_min_profit_not_met`: defer or abort depending on strategy policy
   - `weights`: use as suggested split ratios if present
4. Strategy persists `applied_policies` and constraint-derived decisions in `ExecutionRecord` for audit.

Action fallback schema (suggested)
- `fallback` (on action):
  - `on_insufficient_funds`: `reduce | route:<selector> | defer:<duration> | require_approval | abort`
  - `on_min_profit_not_met`: `defer | abort | require_approval`
  - `prioritize`: ordered list of selectors resources to prioritize when funds are limited

API & Simulator endpoints
- `POST /v1/policies` — create policy (validated)
- `PUT /v1/policies/{id}` — update policy (runs static validation + optional simulation)
- `GET /v1/policies` — list
- `GET /v1/policies/{id}` — get
- `POST /v1/policies/{id}/simulate` — run simulation against a supplied resource snapshot and return `ConstraintDecision` + `FeasibilityDiagnostics`
- `POST /v1/policies/simulate-merge` — accept multiple policies and a resource snapshot, return merged constraints and feasibility diagnostics

UI & UX suggestions
- When editing a policy: show immediate linting/validation and a "Simulate against resource" button to preview merged constraints and feasibility.
- When save would cause infeasibility: show detailed diagnostics and suggested remediations (lower min, increase balance, change priority).

Testing checklist
- Unit tests for Policy model validation and typed constraints.
- Unit tests for `PolicyMerger` merge order and precedence rules.
- Unit tests for `FeasibilityChecker` numeric and percent checks.
- Integration tests where a strategy adapts an action per `ConstraintDecision` (reduce, route, defer).
- Audit tests for `ExecutionRecord` containing `applied_policies` and `constraints_applied`.

Example Policy (YAML)
```yaml
id: preserve_flex
name: Preserve flexible balance
priority: 100
targets:
  - account:checking_main
  - tranche:emergency
constraints:
  min_flexible: 500.0
  weights:
    tranche:emergency: 0.6
    tranche:savings: 0.4
conditional_rules:
  - id: high_income_relax
    condition: "trigger.amount >= 5000"
    constraints:
      min_flexible: 300.0
```

Notes & next steps
- Implement Pydantic models for `Policy`, `ConstraintDecision`, and `FeasibilityDiagnostic`.
- Implement `PolicyMerger` and `FeasibilityChecker` in `app/policies/` and add unit tests.
- Add simulator endpoints and UI hooks for policy preview.

This document describes a constraints-first policy system where strategies are responsible for behavior. If you want, I can now scaffold Pydantic models and the `PolicyMerger` implementation next.
