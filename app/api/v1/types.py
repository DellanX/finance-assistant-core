from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field


class ProviderListItem(BaseModel):
    id: str
    name: Optional[str]
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
    schema: Optional[Dict[str, Any]]


class ActionDefinition(BaseModel):
    id: str
    name: Optional[str]
    description: Optional[str]
    integration: Optional[str] = None
    provider_id: Optional[str] = None
    # Note: categories, labels, and tags are separate resources and not embedded here.
    params: Optional[Dict[str, Any]] = Field(default_factory=dict)
    supports_dry_run: bool = False
    is_async: bool = False


class ActionListResponse(BaseModel):
    actions: List[ActionDefinition]


class CategoryDefinition(BaseModel):
    id: str
    name: Optional[str]
    description: Optional[str]


class TagDefinition(BaseModel):
    key: str
    description: Optional[str]
    values: Optional[List[str]] = Field(default_factory=list)


class CategoryListResponse(BaseModel):
    categories: List[CategoryDefinition]


class TagListResponse(BaseModel):
    tags: List[TagDefinition]


class LabelDefinition(BaseModel):
    id: str
    name: Optional[str]
    description: Optional[str]


class LabelListResponse(BaseModel):
    labels: List[LabelDefinition]


class ActionExecuteRequest(BaseModel):
    entity_id: Optional[str] = None
    params: Optional[Dict[str, Any]] = Field(default_factory=dict)
    dry_run: Optional[bool] = False


class ActionExecuteResponse(BaseModel):
    status: str
    result: Optional[Any] = None
    error: Optional[str] = None
