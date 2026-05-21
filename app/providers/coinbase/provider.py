from app.providers.base import BaseProvider

class CoinbaseProvider(BaseProvider):
    async def discover_accounts(self): pass
    async def sync_transactions(self, account, since): pass
    async def sync_positions(self, account): pass
    async def list_actions(self): pass
    async def execute_action(self, action_name: str, payload: dict, dry_run: bool = False): pass
    async def match_transaction(self, optimistic_tx, provider_tx): pass
