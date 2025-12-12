from dataclasses import dataclass
from typing import Dict, Tuple
from datetime import datetime


@dataclass
class DayNightTariff:
    name: str
    day_price: float
    night_price: float
    day_start: int
    day_end: int
    
    def get_current_price(self) -> Tuple[float, str]:
        current_hour = datetime.now().hour
        
        if self.day_start <= self.day_end:
            is_day = self.day_start <= current_hour < self.day_end
        else:
            is_day = current_hour >= self.day_start or current_hour < self.day_end
        
        if is_day:
            return self.day_price, "День"
        else:
            return self.night_price, "Ніч"
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "day_price": self.day_price,
            "night_price": self.night_price,
            "day_start": self.day_start,
            "day_end": self.day_end,
        }
    
    @staticmethod
    def from_dict(data: Dict) -> "DayNightTariff":
        return DayNightTariff(
            name=data.get("name", ""),
            day_price=data.get("day_price", 0),
            night_price=data.get("night_price", 0),
            day_start=data.get("day_start", 6),
            day_end=data.get("day_end", 22),
        )


class TariffManager:
    def __init__(self):
        self.custom_day_price = 4.32
        self.custom_night_price = 2.59
        self.current_plan: DayNightTariff = DayNightTariff(
            name="Користувацькі",
            day_price=self.custom_day_price,
            night_price=self.custom_night_price,
            day_start=7,
            day_end=23,
        )
    
    def set_custom_prices(self, day_price: float, night_price: float):
        self.custom_day_price = day_price
        self.custom_night_price = night_price
        self.current_plan = DayNightTariff(
            name="Користувацькі",
            day_price=day_price,
            night_price=night_price,
            day_start=self.current_plan.day_start,
            day_end=self.current_plan.day_end,
        )
    
    def get_current_price(self) -> float:
        price, _ = self.current_plan.get_current_price()
        return price
    
    def get_current_period(self) -> str:
        _, period = self.current_plan.get_current_price()
        return period
    
    def calculate_cost(self, power_watts: float, hours: float) -> float:
        power_kw = power_watts / 1000.0
        price = self.get_current_price()
        return power_kw * price * hours
    
    def to_dict(self) -> Dict:
        return {
            "current_plan": self.current_plan.name,
            "current_plan_data": self.current_plan.to_dict(),
            "custom_day_price": self.custom_day_price,
            "custom_night_price": self.custom_night_price,
        }
    
    @staticmethod
    def from_dict(data: Dict) -> "TariffManager":
        mgr = TariffManager()
        if "current_plan_data" in data:
            mgr.current_plan = DayNightTariff.from_dict(data["current_plan_data"])
        if "custom_day_price" in data:
            mgr.custom_day_price = data["custom_day_price"]
        if "custom_night_price" in data:
            mgr.custom_night_price = data["custom_night_price"]
        return mgr
