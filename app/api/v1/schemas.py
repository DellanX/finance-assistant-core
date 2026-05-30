from fastapi import APIRouter, HTTPException
from app.providers.registry import list_integration_packages
import importlib

router = APIRouter()


@router.get("/providers")
def list_provider_schemas():
    """List available integration packages and their configuration schemas (for creation UIs)."""
    pkgs = list_integration_packages()
    schemas = {}
    for p in pkgs:
        try:
            mod = importlib.import_module(f"app.providers.{p}.config")
            if hasattr(mod, "get_schema"):
                schemas[p] = {"schema": mod.get_schema()}
            elif hasattr(mod, "SCHEMA"):
                schemas[p] = {"schema": mod.SCHEMA}
            else:
                schemas[p] = {"schema": None}
        except Exception:
            schemas[p] = {"error": "failed_to_load"}
    return schemas


@router.get("/providers/{integration}")
def get_integration_schema(integration: str):
    pkgs = list_integration_packages()
    if integration not in pkgs:
        raise HTTPException(status_code=404, detail="Integration not found")
    try:
        mod = importlib.import_module(f"app.providers.{integration}.config")
        if hasattr(mod, "get_schema"):
            return {"integration": integration, "schema": mod.get_schema()}
        if hasattr(mod, "SCHEMA"):
            return {"integration": integration, "schema": mod.SCHEMA}
        return {"integration": integration, "schema": None}
    except Exception:
        raise HTTPException(status_code=500, detail="failed to load integration schema")
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from app.core.schemas import NormalizedTransaction, NormalizedLedger, NormalizedAccount, NormalizedTranche
from typing import List


class ProviderListItem(BaseModel):
    id: str
    name: Optional[str]


class ProviderCreateRequest(BaseModel):
    integration: str
    id: Optional[str] = None
    name: Optional[str] = None
    config: Dict[str, Any] = Field(default_factory=dict)


class ProviderResponse(ProviderListItem):
    pass


class ProviderConfigModel(BaseModel):
    config: Dict[str, Any]


class ProviderSchemaResponse(BaseModel):
    provider_id: str
    schema: Optional[Dict[str, Any]]


class TransactionResponse(NormalizedTransaction):
    ledger_id: Optional[str]
    ledger_name: Optional[str]
    provider_id: Optional[str]
    provider_name: Optional[str]


class LedgerResponse(NormalizedLedger):
    provider_id: Optional[str]
    provider_name: Optional[str]


class TrancheResponse(NormalizedTranche):
    provider_id: Optional[str]
    provider_name: Optional[str]


class AccountResponse(NormalizedAccount):
    provider_id: Optional[str]
    provider_name: Optional[str]


class AccountListResponse(BaseModel):
    accounts: List[AccountResponse]
    total: Optional[int] = None
    limit: Optional[int] = None
    offset: Optional[int] = None
    next_cursor: Optional[str] = None
    prev_cursor: Optional[str] = None


class TransactionListResponse(BaseModel):
    transactions: List[TransactionResponse]
    total: Optional[int] = None
    limit: Optional[int] = None
    offset: Optional[int] = None
    next_cursor: Optional[str] = None
    prev_cursor: Optional[str] = None


class LedgerListResponse(BaseModel):
    ledgers: List[LedgerResponse]
    total: Optional[int] = None
    limit: Optional[int] = None
    offset: Optional[int] = None
    next_cursor: Optional[str] = None
    prev_cursor: Optional[str] = None


class TrancheListResponse(BaseModel):
    tranches: List[TrancheResponse]
    total: Optional[int] = None
    limit: Optional[int] = None
    offset: Optional[int] = None
    next_cursor: Optional[str] = None
    prev_cursor: Optional[str] = None
