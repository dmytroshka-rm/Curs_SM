import requests
from typing import List, Dict, Any

from frontend.models import DeviceModel, RoomModel, DeviceType


class ApiError(Exception):
    pass


class ApiSmartHomeClient:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url.rstrip("/")

    def _get(self, path: str) -> Any:
        url = f"{self.base_url}{path}"
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        return resp.json()

    def _post(self, path: str, payload: Dict[str, Any]) -> Any:
        url = f"{self.base_url}{path}"
        resp = requests.post(url, json=payload, timeout=5)
        resp.raise_for_status()
        return resp.json()

    def get_rooms(self) -> List[RoomModel]:
        data = self._get("/rooms")
        return [RoomModel.from_json(r) for r in data]

    def add_room(self, name: str) -> RoomModel:
        data = self._post("/rooms/add", {"name": name})

        if data.get("status") != "ok":
            raise ApiError(data.get("message", "Unknown error"))

        room = data.get("room")
        return RoomModel.from_json(room)

    def delete_room(self, room_id: str) -> Dict[str, Any]:
        data = self._post("/rooms/delete", {"room_id": room_id})

        if data.get("status") != "ok":
            raise ApiError(data.get("message", "Unknown error"))

        return data


    def get_devices(self) -> List[DeviceModel]:
        data = self._get("/devices")
        return [DeviceModel.from_json(d) for d in data]

    def add_device(
        self,
        room_id: str,
        device_type: DeviceType,
        config: Dict[str, Any],
    ) -> DeviceModel:

        payload = {
            "room_id": room_id,
            "type": device_type.value,
            "config": config,
        }

        data = self._post("/devices/add", payload)

        if data.get("status") != "ok":
            raise ApiError(data.get("message", "Unknown error"))

        return DeviceModel.from_json(data["device"])

    def delete_device(self, device_id: str) -> Dict[str, Any]:
        data = self._post("/devices/delete", {"device_id": device_id})

        if data.get("status") != "ok":
            raise ApiError(data.get("message", "Unknown error"))

        return data

    def update_device(self, device_id: str, state: Dict[str, Any]) -> DeviceModel:
        payload = {"id": device_id, "state": state}

        data = self._post("/device/update", payload)

        if data.get("status") != "ok":
            raise ApiError(data.get("message", "Unknown error"))

        return DeviceModel.from_json(data["device"])


    def optimize(self, tariff: int) -> List[DeviceModel]:
        payload = {"tariff": tariff}

        data = self._post("/optimize", payload)

        devices_json = data.get("devices", [])
        return [DeviceModel.from_json(d) for d in devices_json]

    def get_stats(self) -> Dict[str, Any]:
        data = self._get("/stats")
        return data

    def get_chart_history(self, period: str = "24hours") -> Dict[str, Any]:
        data = self._get(f"/chart/history?period={period}")
        return data

    def get_schedules(self, device_id: str) -> List[Dict[str, Any]]:
        data = self._get(f"/schedules?device_id={device_id}")
        if isinstance(data, list):
            return data
        return data.get("schedules", [])

    def save_schedule(self, device_id: str, schedule_data: Dict[str, Any]) -> Dict[str, Any]:
        payload = {
            "device_id": device_id,
            "schedule": schedule_data
        }
        data = self._post("/schedules/save", payload)
        return data

    def delete_schedule(self, device_id: str, day_of_week: int) -> Dict[str, Any]:
        payload = {
            "device_id": device_id,
            "day_of_week": day_of_week
        }
        data = self._post("/schedules/delete", payload)
        return data
