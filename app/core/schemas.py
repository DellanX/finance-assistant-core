from pydantic import BaseModel
from typing import Optional


class NormalizedTransaction(BaseModel):
    id: str
    date: Optional[str] = None
    amount: float = 0.0
    merchant: Optional[str] = None
    status: str = "unknown"


class NormalizedPosition(BaseModel):
    symbol: str
    quantity: float = 0.0
    cost_basis: float = 0.0
    current_price: float = 0.0


class Holding(BaseModel):
    symbol: str
    quantity: float
    value: float
    cost_basis: float
    gain: float
    gain_pct: float
    account_name: Optional[str] = None
    provider_name: Optional[str] = None


class PortfolioSummary(BaseModel):
    total_value: float
    cash_balance: float
    investment_balance: float


class PortfolioResponse(BaseModel):
    summary: PortfolioSummary
    holdings: list[Holding] = []


class NormalizedAccount(BaseModel):
    id: str
    name: Optional[str] = None
    type: Optional[str] = None
    balance: float = 0.0


class NormalizedAsset(BaseModel):
    symbol: str
    name: Optional[str] = None
    currency: Optional[str] = None
    current_price: float = 0.0


class NormalizedTranche(BaseModel):
    id: str
    name: Optional[str] = None
    type: Optional[str] = None
    total_amount: float = 0.0


class NormalizedLedger(BaseModel):
    id: str
    name: Optional[str] = None
    currency: Optional[str] = None
    balance: float = 0.0
    accounts_count: int = 0
