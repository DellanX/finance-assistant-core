from abc import ABC, abstractmethod

class BaseProvider(ABC):
    @abstractmethod
    async def discover_accounts(self):
        pass

    @abstractmethod
    async def sync_transactions(self, account, since):
        pass

    @abstractmethod
    async def sync_positions(self, account):
        pass

    @abstractmethod
    async def list_actions(self):
        pass

    @abstractmethod
    async def execute_action(self, action_name: str, payload: dict, dry_run: bool = False):
        pass

    @abstractmethod
    async def match_transaction(self, optimistic_tx, provider_tx):
        pass
