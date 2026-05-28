from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class ProviderConfig:
    """Represents a provider configuration record suitable for UI consumption.

    - `provider_id`: unique id of the provider instance
    - `data`: arbitrary configuration key/value map
    - `schema`: optional dict describing expected keys (used by simple validation/UI hints)
    - `updated_at`: timestamp when config was last changed
    """
    provider_id: str
    data: Dict[str, Any] = field(default_factory=dict)
    schema: Optional[Dict[str, Any]] = None
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def update(self, updates: Dict[str, Any]):
        """Merge updates into the config data and refresh timestamp."""
        for k, v in updates.items():
            self.data[k] = v
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "data": self.data,
            "schema": self.schema,
            "updated_at": self.updated_at.isoformat(),
        }
