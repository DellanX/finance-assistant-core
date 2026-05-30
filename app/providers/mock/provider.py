import json
import os
from typing import Dict, Any, List
from app.providers.base import BaseProvider
from app.providers.coordinator import BaseCoordinator
from app.providers import registry

class MockProvider(BaseProvider):
    def __init__(self, config_path: str, coordinator_factory=None, write_json_fn=None, load_state_fn=None):
        """Mock provider backed by a JSON file.

        Tests may pass `coordinator_factory` (callable(provider)->coord),
        `write_json_fn(path, data)` to avoid filesystem writes, and
        `load_state_fn(path)->dict` to control loading behavior.
        """
        self.config_path = config_path
        self._write_json_fn = write_json_fn
        self._load_state_fn = load_state_fn
        self._state = self._load_state()
        self.id = self._state.get("id", "unknown_mock_provider")
        self.name = self._state.get("name", "Unknown Mock Provider")
        # Attach a coordinator that will periodically reload the state file
        async def _reload_state():
            try:
                self._state = self._load_state()
            except Exception:
                pass

        if coordinator_factory is not None:
            try:
                self.coordinator = coordinator_factory(self)
            except Exception:
                # fallback to default coordinator
                self.coordinator = BaseCoordinator(update_fn=_reload_state, update_interval=30, name=f"mock:{self.id}")
        else:
            self.coordinator = BaseCoordinator(update_fn=_reload_state, update_interval=30, name=f"mock:{self.id}")

    def _load_state(self) -> Dict[str, Any]:
        if self._load_state_fn is not None:
            try:
                return self._load_state_fn(self.config_path)
            except Exception:
                pass
        if not os.path.exists(self.config_path):
            return {"id": "error", "name": "Error Loading Provider", "accounts": [], "transactions": {}, "positions": {}}
        with open(self.config_path, "r") as f:
            return json.load(f)
            
    def _save_state(self):
        if self._write_json_fn is not None:
            try:
                return self._write_json_fn(self.config_path, self._state)
            except Exception:
                pass
        with open(self.config_path, "w") as f:
            json.dump(self._state, f, indent=4)

    def get_state(self) -> Dict[str, Any]:
        return self._state
        
    def update_state(self, updates: Dict[str, Any]):
        """Merge new updates into the mock state."""
        # Simple top-level merge for now
        for key, value in updates.items():
            self._state[key] = value
        self._save_state()

    def _config(self) -> Dict[str, Any]:
        """Return the ProviderConfig data for this provider, falling back to state 'config' or sensible defaults."""
        try:
            cfg = registry.get_provider_config(self.id)
            if cfg is not None:
                return cfg.data
        except Exception:
            pass

        # fallback to state-held config or defaults
        return self._state.get("config", {"enable_balances": True, "enable_transactions": True, "enable_budgets": False})

    async def discover_accounts(self) -> List[Dict[str, Any]]:
        accounts = self._state.get("accounts", [])
        cfg = self._config()
        if not cfg.get("enable_balances", True):
            # hide balance fields when balances are disabled
            result = []
            for a in accounts:
                a_copy = dict(a)
                if "balance" in a_copy:
                    a_copy.pop("balance")
                result.append(a_copy)
            return result
        # Wrap accounts into normalized account models if available
        try:
            from app.core.schemas import NormalizedAccount
            return [NormalizedAccount(**a) for a in accounts]
        except Exception:
            return accounts

    async def sync_transactions(self, account: Dict[str, Any], since=None) -> List[Dict[str, Any]]:
        # support either dict-like or Pydantic model accounts
        if hasattr(account, "model_dump"):
            acct = account.model_dump()
        elif isinstance(account, dict):
            acct = account
        else:
            try:
                acct = dict(account)
            except Exception:
                acct = {}

        account_id = acct.get("id")
        # Returns transactions mapped by account_id
        cfg = self._config()
        if not cfg.get("enable_transactions", True):
            return []
        raw = self._state.get("transactions", {}).get(account_id, [])
        try:
            from app.providers.normalizers import normalize_transactions
            # return normalized models (Pydantic) directly
            return normalize_transactions(raw)
        except Exception:
            return raw

    async def sync_positions(self, account: Dict[str, Any]) -> List[Dict[str, Any]]:
        if hasattr(account, "model_dump"):
            acct = account.model_dump()
        elif isinstance(account, dict):
            acct = account
        else:
            try:
                acct = dict(account)
            except Exception:
                acct = {}

        account_id = acct.get("id")
        cfg = self._config()
        if not cfg.get("enable_balances", True):
            return []
        raw = self._state.get("positions", {}).get(account_id, [])
        try:
            from app.providers.normalizers import normalize_positions
            return normalize_positions(raw)
        except Exception:
            return raw

    async def list_actions(self) -> List[str]:
        # Return the ids of available actions (combine core + provider-level in registry)
        defs = await self.get_action_definitions()
        return [d.get("id") for d in defs]

    async def execute_action(self, action_name: str, payload: dict, dry_run: bool = False):
        if action_name == "simulate_transfer":
            return {"status": "success", "message": "Simulated transfer executed."}
        elif action_name == "simulate_failure":
            raise Exception("Simulated failure action triggered.")
        return {"status": "ignored", "message": f"Action {action_name} not recognized."}

    async def get_action_definitions(self) -> List[Dict[str, Any]]:
        """Return provider-specific action metadata used by the UI/API.

        Each action dict should include at least `id` and may include `name`,
        `description`, `params` (a simple schema), and flags like `supports_dry_run`.
        """
        return [
            {
                "id": "simulate_transfer",
                "name": "Simulate Transfer",
                "description": "Simulate moving funds between mock accounts for testing UI flows.",
                "integration": "mock",
                "params": {"from_account": {"type": "string"}, "to_account": {"type": "string"}, "amount": {"type": "number"}},
                "supports_dry_run": True,
                "is_async": False,
            },
            {
                "id": "simulate_failure",
                "name": "Simulate Failure",
                "description": "Trigger a simulated failing action to test error handling paths.",
                "integration": "mock",
                "params": {},
                "supports_dry_run": False,
                "is_async": False,
            },
        ]

    async def match_transaction(self, optimistic_tx, provider_tx):
        # A simple matching logic for mock purposes: match if amounts and dates are close, or if reference matches
        return True
