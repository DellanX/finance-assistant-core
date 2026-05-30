from app.providers.base import BaseProvider
from app.providers.devices import register_device, register_entity, Device, Entity


class EnvelopeBudgetProvider(BaseProvider):
    def __init__(self, provider_id: str = "envelope_budget", name: str = "Envelope Budget"):
        self.id = provider_id
        self.name = name
        # register a device and an example budget entity so the provider exposes HA-friendly state
        dev = Device(id=f"{self.id}_device", name=self.name)
        register_device(self.id, dev)
        ent = Entity(id=f"{self.id}_budget", type="budget", name="Budget Summary", state={"remaining": 0.0})
        register_entity(self.id, dev.id, ent)

    async def discover_accounts(self):
        pass

    async def sync_transactions(self, account, since):
        pass

    async def sync_positions(self, account):
        pass

    async def list_actions(self):
        pass

    async def execute_action(self, action_name: str, payload: dict, dry_run: bool = False):
        pass

    async def match_transaction(self, optimistic_tx, provider_tx):
        pass
