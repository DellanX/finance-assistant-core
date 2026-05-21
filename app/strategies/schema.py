from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class TriggerSchema(BaseModel):
    platform: str
    minutes: Optional[str] = None
    # other trigger properties

class ActionSchema(BaseModel):
    service: str
    data: Dict[str, Any]

class StrategySchema(BaseModel):
    id: str
    name: str
    trigger: List[TriggerSchema]
    condition: Optional[List[str]] = None
    action: List[ActionSchema]
    mode: str = "single"
    dry_run: bool = False
