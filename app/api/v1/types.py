from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field


class ProviderListItem(BaseModel):
    id: str
    name: Optional[str] = None
    integration: Optional[str] = None


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
    schema: Optional[Dict[str, Any]] = None


class ActionDefinition(BaseModel):
    id: str
    name: Optional[str] = None
    description: Optional[str] = None
    integration: Optional[str] = None
    provider_id: Optional[str] = None
    # Note: categories, labels, and tags are separate resources and not embedded here.
    params: Optional[Dict[str, Any]] = Field(default_factory=dict)
    supports_dry_run: bool = False
    is_async: bool = False


class ActionListResponse(BaseModel):
    actions: List[ActionDefinition]


class ProviderListResponse(BaseModel):
    providers: List[ProviderListItem]
    total: Optional[int] = None
    limit: Optional[int] = None
    offset: Optional[int] = None
    next_cursor: Optional[str] = None
    prev_cursor: Optional[str] = None


class CategoryDefinition(BaseModel):
    id: str
    name: Optional[str] = None
    description: Optional[str] = None


class TagDefinition(BaseModel):
    key: str
    description: Optional[str] = None
    values: Optional[List[str]] = Field(default_factory=list)


class CategoryListResponse(BaseModel):
    categories: List[CategoryDefinition]
    total: Optional[int] = None
    limit: Optional[int] = None
    offset: Optional[int] = None
    next_cursor: Optional[str] = None
    prev_cursor: Optional[str] = None


class TagListResponse(BaseModel):
    tags: List[TagDefinition]
    total: Optional[int] = None
    limit: Optional[int] = None
    offset: Optional[int] = None
    next_cursor: Optional[str] = None
    prev_cursor: Optional[str] = None


class LabelDefinition(BaseModel):
    id: str
    name: Optional[str] = None
    description: Optional[str] = None


class LabelListResponse(BaseModel):
    labels: List[LabelDefinition]
    total: Optional[int] = None
    limit: Optional[int] = None
    offset: Optional[int] = None
    next_cursor: Optional[str] = None
    prev_cursor: Optional[str] = None


class ActionExecuteRequest(BaseModel):
    entity_id: Optional[str] = None
    params: Optional[Dict[str, Any]] = Field(default_factory=dict)
    dry_run: Optional[bool] = False


class ActionExecuteResponse(BaseModel):
    status: str
    result: Optional[Any] = None
    error: Optional[str] = None


class StrategyDefinition(BaseModel):
    id: str
    name: Optional[str] = None
    description: Optional[str] = None


class StrategyListResponse(BaseModel):
    strategies: List[StrategyDefinition]
    total: Optional[int] = None
    limit: Optional[int] = None
    offset: Optional[int] = None
    next_cursor: Optional[str] = None
    prev_cursor: Optional[str] = None


class SnapshotDefinition(BaseModel):
    id: str
    name: Optional[str] = None
    created_at: Optional[str] = None


class SnapshotListResponse(BaseModel):
    snapshots: List[SnapshotDefinition]
    total: Optional[int] = None
    limit: Optional[int] = None
    offset: Optional[int] = None
    next_cursor: Optional[str] = None
    prev_cursor: Optional[str] = None


class ReconcilerListResponse(BaseModel):
    reconcilers: List[str]


class HealthResponse(BaseModel):
    status: str
    providers: Dict[str, Any]


class MockStateResponse(BaseModel):
    state: Dict[str, Any]


class SimpleStatusResponse(BaseModel):
    status: str
    message: Optional[str] = None
