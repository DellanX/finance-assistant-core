# Target Feature Set

Product Overview

Finance Assistant is a self-hosted automation engine that unifies financial data from multiple providers (GetSequence.io, Coinbase, Alpaca, Actual, etc.) into a consistent internal model. It enables users to track income, expenses, invesments, savings, and debts and to automate financial decidsions using a YAML-based strategy system.

The system is designed to run on lightweight hardware (e.g., Raspberry Pi 4) and integrate seamlessly with Home Assistant, while remaining fully functional as a standalone service.

# Core Principles

## Provider Agnostic Data Model

All external data is normalized into internal primitives:
* Ledger - chronological list of transactions
* Portfolio - grouping of assets
* Asset - any financial instrument or holding
* Tranche - a user-defined slice of an asset, allocations or transactions
* Budget - planned vs actual spending categories
* Account - bank, exchange, wallet, brokerage, etc

## Three-Layer Processing Model

1. Input Layer
  * raw provider data (partial or complete)
  * Provider-specific schemas
  * Webhooks, polling, or manual support
2. Correction Layer
  * Reconciliation
  * Missing-data inference
  * Cost-basis reconstruction
  * Fee attribution
  * Tag/label/category assignment
  * Polic evaluation
3. Output Layer
  * Unified API representation
  * Strategy triggers
  * Automation-ready events
  * Provider-specific write-back (where supported)

## Automation-First Design

Strategies operate like Home Assistant automations:
* YAML-based
* Trigger->Conditions->Action
* Can reference categories, labels, policiee, tags and computed metrics
* Can execute provider actions (e.g., rebalance, transfer, buy/sell, move funds)

# Feature Set
## Integrations
### Provider Integrations

Each provider integration must support:
* Authentication (OAuth, API Keys local tokens)
* Data ingestion (Polling + webhook + websocket)
* Partial data tolerance
  Examples:
    - Coinbase: positions but no cost basis
    - Alpaca: trade but no deposits
    - Actual: budgets but no investment data
    - GetSequence: balances but no other information

### Home Assitant Integration
* Add-on compatible
* Expose entities:
  - Balances
  - Net worth
  - Budget categories
  - Portfolio performance
  - Strategy status
* Fire events:
  - "income_received"
  - "bill_due"
  - "allocation_completed"
  - "strategy_executed"

## Data Model Features
### Categories
* Valueless attributes
* Used for classifications (e.g., "Bills", "Savings", "Investments")
* Many-to-many with transactions, assets, accounts

### Labels
* Valued attributes (e.g. "priority: high", "risk: 0.7")
* User-defined
* Used for strategy conditions

### Tags
* System-defined valued attributes
* Examples:
  - "fee: $1.25"
  - "exchange_rate: 1.09"
  - "confidence: 0.82"

### Policies
Metadata attached to resources (accounts, assets, tranches, categories).
Examples:
* "auto-invest: true"
* "min-balance: 500"
* "rebalance-target: 20%"

### Strategies
Automation definitions:
* Triggers
  - On income
  - On transaction
  - On schedule
  - On threshold (e.g., balance < X)
* Conditions
  - Category/label/policy checks
  - Provider state
  - Portfolio metrcis
* Actions
  - Move funds
  - Buy/sell
  - Allocation to tranches
  - Update labels/policies
  - Emit events
  - Notify user

## Financial Tracking Features
### Income Tracking
* Detect income transactions
* Categories by source
* Allocate automatically to:
  - Bills
  - Savings
  - Investments
  - Debt repayment
* Track allocation history

### Expense tracking
* Categorizaation engine
* Recurring bill detection
* Cost attribution
* Fee detection and tagging

### Investment Tracking
* Portfolio aggregation
* Cost basis reconstruction
* Realized/unrealized gains
* Tranche-level performance
* Allocation drift detection
* Rebalance suggestions

### Debt tracking
* Loan accounts
* Interest calculatin
* Amortization modeling
* Strategy-driven extra payments

### Budgeting
* Import from Actual, another provider, or internal budgeting module
* Category-level planned vs actual
* Alerts for overspending
* Strategy triggers for budget events

## Allocation Engine
A core subsystem responsible for:
* Splitting income into tranches
* Tracking how each dollar flows through the system
* Supporting:
  - Percentage-based allocation
  - Priority-based allocation
  - Conditional allocation
  - Multi-step allocation (e.g. income -> bills -> leftover -> investments)
* Allocation records must include:
  - Source transaction
  - Destination accounts/categories
  - Amount
  - Strategy responsible
  - Timestamp
  - Confidence score (if inferred)

## API Features
### REST API (v1)
Endpoints for:
* Acounts
* Transactions
* Portfolios
* Assets
* Budgets
* Strategies
* Categories/labels/policies/tags
* Allocatin history
* Provider sync status

### Websocket API (v1)
Channels:
* Live Logs
* Strategy execution previews
* Sync status updates
* Allocation visualizer
* Event stream

## UI Features (Frontend)
### Dashboard
* Net worth
* Income vs expenses
* Allocation flow diagram
* Portfolio performance
* Upcoming bills
* Strategy status

### Strategy Editor
* YAML editor with schema validation
* Visual builder (future)
* Dryrun mode
* Execution logs

### Provider Management
* Add/remove providers
* Sync history
* Error reporting
* Data completeness indicators

### Ledger and Portfolio Views
* Transaction explorer
* Asset breakdown
* Tranche explorer
* Cost basis inspector
* Fee attribution view

# Test Required
## Unit Tests
* Provider adapters
* Normalization logic
* Allocaation engine
* Strategy parser
* Policy evaluattor
* Cost basis reconstruction
* Category/label/tag assignment

## Integration Tests
* Multi-provider sync
* Partial-data ingestion
* Strategy parser
* Allocation flows
* Webhook handling
* Home Assistant integration

## End-to-end tests
* Income -> allocation -> investment
* Bill detection -> payment -> reconciliation
* Portfolio drift -> rebalance strategy
* Debt repayment automation
* Budget overspend alert -> strategy action

## Performance Tests
* Rasberry Pi 3 Baselie
* 100K+ transactions
* 10+ providers
* 50+ strategies
* Real-time websocket updates

# Future Enhancements
* Machine-learning-based categorization
* Natural-language strategy builder
* Multi-user support with authentication and RBAC
* Plugin Marketplace (similar to HACS)
* Strategy templates
  - builtin tax optimization strategies
* AI based anomaly detection
* MCP for local LLM connections for privcy presering insights

# Open Questions (for future refinement)
* Should strategies be allowed to modify historical data?
* Should the system support virtual accounts?
  - Virtual envelopes?
* How should confliting strategies be resolved?
* Should the sysem support multi-currency portfolios natively or via conversion?
* Should the allocation engine support "waterfall" models?
