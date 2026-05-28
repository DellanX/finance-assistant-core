from fastapi import APIRouter
from app.api.v1 import transactions, portfolios, tranches, ledgers, providers, strategies, snapshots, mock, health, schemas, actions, categories, tags, labels

api_router = APIRouter()

api_router.include_router(transactions.router, prefix="/v1/transactions", tags=["transactions"])
api_router.include_router(portfolios.router, prefix="/v1/portfolios", tags=["portfolios"])
api_router.include_router(tranches.router, prefix="/v1/tranches", tags=["tranches"])
api_router.include_router(ledgers.router, prefix="/v1/ledgers", tags=["ledgers"])
api_router.include_router(providers.router, prefix="/v1/providers", tags=["providers"])
api_router.include_router(actions.router, prefix="/v1/actions", tags=["actions"])
api_router.include_router(categories.router, prefix="/v1/categories", tags=["categories"])
api_router.include_router(tags.router, prefix="/v1/tags", tags=["tags"])
api_router.include_router(labels.router, prefix="/v1/labels", tags=["labels"])
api_router.include_router(strategies.router, prefix="/v1/strategies", tags=["strategies"])
api_router.include_router(snapshots.router, prefix="/v1/snapshots", tags=["snapshots"])
api_router.include_router(mock.router, prefix="/v1/mock", tags=["mock"])
api_router.include_router(health.router, prefix="/v1", tags=["health"])
api_router.include_router(schemas.router, prefix="/v1/schemas", tags=["schemas"])
