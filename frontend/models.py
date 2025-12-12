from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Dict, Any


class DeviceType(str, Enum):
    LIGHT = "light"
    CLIMATE = "climate"
    SMART_PLUG = "smart_plug"

    @staticmethod
    def from_str(value: str) -> "DeviceType":
        value = value.lower()
        if value in ("light", "lamp"):
            return DeviceType.LIGHT
        if value in ("climate", "hvac"):
            return DeviceType.CLIMATE
        if value in ("smart_plug", "plug"):
            return DeviceType.SMART_PLUG
        return DeviceType.LIGHT


@dataclass
class DeviceModel:
    id: str
    name: str
    room: str
    type: DeviceType
    is_on: bool
    critical: bool
    current_power: float

    brightness: Optional[int] = None       
    max_power: Optional[float] = None

    target_temperature: Optional[int] = None  
    base_power: Optional[float] = None

    load_power: Optional[float] = None 

    @staticmethod
    def from_json(data: Dict[str, Any]) -> "DeviceModel":
        d_type = DeviceType.from_str(data.get("type", "light"))
        
        load_power = data.get("load_power")
        if load_power is None:
            load_power = data.get("current_power", 0.0)
        
        return DeviceModel(
            id=data.get("id", ""),
            name=data.get("name", ""),
            room=data.get("room", data.get("room_name", "")),
            type=d_type,
            is_on=data.get("is_on", True),
            critical=data.get("critical", False),
            current_power=float(data.get("current_power", 0.0)),
            brightness=data.get("brightness"),
            max_power=data.get("max_power"),
            target_temperature=data.get("target_temperature"),
            base_power=data.get("base_power"),
            load_power=load_power,
        )


@dataclass
class RoomModel:
    id: str
    name: str
    total_power: float
    devices: List[DeviceModel]

    @staticmethod
    def from_json(data: Dict[str, Any]) -> "RoomModel":
        devices_json = data.get("devices", [])
        devices = [DeviceModel.from_json(d) for d in devices_json]
        return RoomModel(
            id=data.get("id", ""),
            name=data.get("name", ""),
            total_power=float(data.get("total_power", 0.0)),
            devices=devices,
        )


@dataclass
class ScheduleEntryModel:
    device_id: str
    day_of_week: int
    enabled: bool
    turn_on_hour: int
    turn_on_minute: int
    turn_off_hour: int
    turn_off_minute: int

    @staticmethod
    def from_json(data: Dict[str, Any]) -> "ScheduleEntryModel":
        return ScheduleEntryModel(
            device_id=data.get("device_id", ""),
            day_of_week=data.get("day_of_week", 0),
            enabled=data.get("enabled", True),
            turn_on_hour=data.get("turn_on_hour", 7),
            turn_on_minute=data.get("turn_on_minute", 0),
            turn_off_hour=data.get("turn_off_hour", 23),
            turn_off_minute=data.get("turn_off_minute", 0),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "device_id": self.device_id,
            "day_of_week": self.day_of_week,
            "enabled": self.enabled,
            "turn_on_hour": self.turn_on_hour,
            "turn_on_minute": self.turn_on_minute,
            "turn_off_hour": self.turn_off_hour,
            "turn_off_minute": self.turn_off_minute,
        }
