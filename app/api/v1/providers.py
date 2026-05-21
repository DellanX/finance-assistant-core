from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_providers():
    return []

@router.get("/{id}/accounts")
def get_provider_accounts(id: str):
    return []
