from fastapi import APIRouter
from app.api.v1 import transactions, portfolios, tranches, ledgers, providers, strategies, snapshots

api_router = APIRouter()

api_router.include_router(transactions.router, prefix="/v1/transactions", tags=["transactions"])
api_router.include_router(portfolios.router, prefix="/v1/portfolios", tags=["portfolios"])
api_router.include_router(tranches.router, prefix="/v1/tranches", tags=["tranches"])
api_router.include_router(ledgers.router, prefix="/v1/ledgers", tags=["ledgers"])
api_router.include_router(providers.router, prefix="/v1/providers", tags=["providers"])
api_router.include_router(strategies.router, prefix="/v1/strategies", tags=["strategies"])
api_router.include_router(snapshots.router, prefix="/v1/snapshots", tags=["snapshots"])
