from fastapi import APIRouter
from app.providers.registry import active_providers
from app.api.v1.schemas import LedgerResponse

router = APIRouter()


@router.get("", response_model=list[LedgerResponse])
async def get_ledgers():
    ledgers: list[LedgerResponse] = []
    for provider_id, provider in active_providers.items():
        accounts = await provider.discover_accounts()
        for acc in accounts:
            # acc may be a Pydantic model
            if hasattr(acc, "model_dump"):
                accd = acc.model_dump()
            elif isinstance(acc, dict):
                accd = acc
            else:
                try:
                    accd = dict(acc)
                except Exception:
                    accd = {}

            lr = LedgerResponse(
                id=accd.get("id", ""),
                name=accd.get("name"),
                currency=accd.get("currency"),
                balance=accd.get("balance", 0.0),
                accounts_count=1,
                provider_id=provider_id,
                provider_name=provider.name,
            )
            ledgers.append(lr)
    return ledgers

