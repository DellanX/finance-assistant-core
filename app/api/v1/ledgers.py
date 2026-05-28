from fastapi import APIRouter
from app.providers.registry import active_providers

router = APIRouter()

@router.get("")
async def get_ledgers():
    ledgers = []
    for provider_id, provider in active_providers.items():
        accounts = await provider.discover_accounts()
        for acc in accounts:
            ledgers.append({
                "id": acc.get("id"),
                "name": acc.get("name"),
                "type": acc.get("type"),
                "balance": acc.get("balance"),
                "currency": acc.get("currency"),
                "provider_id": provider_id,
                "provider_name": provider.name
            })
    return ledgers

