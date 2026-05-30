from pydantic import BaseModel
from typing import Dict, List, Optional
import uuid


class Entity(BaseModel):
    id: str
    type: str
    name: Optional[str] = None
    state: Optional[dict] = None
    attributes: dict = {}


class Device(BaseModel):
    id: str
    name: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    entities: List[Entity] = []


# provider_id -> device_id -> Device
provider_devices: Dict[str, Dict[str, Device]] = {}


def _ensure_provider(provider_id: str):
    if provider_id not in provider_devices:
        provider_devices[provider_id] = {}


def register_device(provider_id: str, device: Device) -> Device:
    _ensure_provider(provider_id)
    if not device.id:
        device.id = f"device_{uuid.uuid4().hex[:8]}"
    provider_devices[provider_id][device.id] = device
    return device


def register_entity(provider_id: str, device_id: str, entity: Entity) -> Entity:
    _ensure_provider(provider_id)
    devices = provider_devices[provider_id]
    if device_id not in devices:
        # create placeholder device
        devices[device_id] = Device(id=device_id, name=device_id, entities=[])
    dev = devices[device_id]
    # replace existing entity with same id
    existing = [e for e in dev.entities if e.id == entity.id]
    if existing:
        dev.entities = [e for e in dev.entities if e.id != entity.id]
    dev.entities.append(entity)
    return entity


def list_devices(provider_id: str) -> List[Device]:
    _ensure_provider(provider_id)
    return list(provider_devices[provider_id].values())


def clear_provider(provider_id: str):
    provider_devices.pop(provider_id, None)
