from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import json
from collections import deque, Counter


class DeviceType(Enum):
    LIGHT = "light"
    CLIMATE = "climate"
    PLUG = "plug"


class OptimizationLevel(Enum):
    MINIMAL = 1
    BALANCED = 2
    AGGRESSIVE = 3     


@dataclass
class OptimizationTip:
    device_name: str
    device_type: DeviceType
    title: str
    description: str
    estimated_savings: float
    priority: str
    action: str
    impact: str                    


class OptimizationEngine:
    def __init__(self, optimization_level: OptimizationLevel = OptimizationLevel.BALANCED):
        self.level = optimization_level
        self.daily_consumption_history = []
        self.hourly_patterns = {}
        self.device_usage_stats = {}
        self._power_samples = deque(maxlen=120)

    def update_power_sample(self, power_watts: float):
        if power_watts is None:
            return
        try:
            self._power_samples.append(float(power_watts))
        except Exception:
            pass

    def estimate_daily_kwh(self) -> float:
        if not self._power_samples:
            return 0.0
        avg_power_w = sum(self._power_samples) / len(self._power_samples)
        return (avg_power_w / 1000.0) * 24
    
    def analyze_consumption(self, 
                           current_power: float,
                           total_power_today: float,
                           hourly_avg: float,
                           weather_data: Optional[Dict] = None,
                           time_of_day: Optional[str] = None,
                           device_mix: Optional[Counter] = None) -> List[OptimizationTip]:
        tips = []
        
        if current_power > 3000:
            tips.append(OptimizationTip(
                device_name="System",
                device_type=DeviceType.PLUG,
                title="Високе споживання!",
                description=f"Поточне споживання {int(current_power)} Вт вище норми",
                estimated_savings=15.0,
                priority="high",
                action="Відключіть непотрібні пристрої",
                impact="Економія до 50 ₴/день"
            ))
        elif current_power > 2000 and self.level != OptimizationLevel.MINIMAL:
            tips.append(OptimizationTip(
                device_name="System",
                device_type=DeviceType.PLUG,
                title="Підвищене споживання",
                description=f"Поточне споживання {int(current_power)} Вт",
                estimated_savings=8.0,
                priority="medium",
                action="Розгляньте відключення малокритичних пристроїв",
                impact="Економія до 25 ₴/день"
            ))
        
        if total_power_today > 15:
            tips.append(OptimizationTip(
                device_name="System",
                device_type=DeviceType.PLUG,
                title="Високе денне спожування",
                description=f"Ви спожили {total_power_today:.1f} кВт⋅год (норма ~10-12 кВт⋅год)",
                estimated_savings=30.0,
                priority="high" if self.level == OptimizationLevel.AGGRESSIVE else "medium",
                action="Активуйте режим енергозбереження",
                impact="Економія 100-150 ₴/день"
            ))
        
        if weather_data:
            temp = weather_data.get('temperature')
            humidity = weather_data.get('humidity')
            
            if temp and temp > 25:
                tips.append(OptimizationTip(
                    device_name="Клімат",
                    device_type=DeviceType.CLIMATE,
                    title="Спека - вимкніть обігрів!",
                    description=f"Температура {temp}°C. Обігрів марно витрачає енергію",
                    estimated_savings=20.0,
                    priority="high",
                    action="Відключіть опалювальні пристрої",
                    impact="Економія 40 ₴/день"
                ))
            elif temp and temp < 5 and self.level == OptimizationLevel.AGGRESSIVE:
                tips.append(OptimizationTip(
                    device_name="Клімат",
                    device_type=DeviceType.CLIMATE,
                    title="Холодно - оптимізуйте опалення",
                    description=f"Температура {temp}°C. Включіть розумне опалення",
                    estimated_savings=5.0,
                    priority="medium",
                    action="Використовуйте програмуючий терморегулятор",
                    impact="Економія 15 ₴/день"
                ))
            
            if humidity and humidity > 70:
                tips.append(OptimizationTip(
                    device_name="Вентиляція",
                    device_type=DeviceType.PLUG,
                    title="Висока вологість",
                    description=f"Вологість {humidity}% - природна вентиляція ефективніша",
                    estimated_savings=3.0,
                    priority="low" if self.level == OptimizationLevel.MINIMAL else "medium",
                    action="Відкрийте вікна замість кондиціонера",
                    impact="Економія 10 ₴/день"
                ))
        
        if time_of_day == "morning":
            tips.append(OptimizationTip(
                device_name="Освітлення",
                device_type=DeviceType.LIGHT,
                title="Ранок - природне світло",
                description="Ранкові години - максимум природного світла",
                estimated_savings=2.0,
                priority="low",
                action="Відключіть зайві ліхтарики",
                impact="Економія 5 ₴/день"
            ))
        elif time_of_day == "afternoon":
            tips.append(OptimizationTip(
                device_name="Освітлення",
                device_type=DeviceType.LIGHT,
                title="День - вимкніть світло",
                description="Денне світло достатньо яскраве, штучне світло непотрібне",
                estimated_savings=4.0,
                priority="medium" if self.level != OptimizationLevel.MINIMAL else "low",
                action="Вимкніть зайве освітлення",
                impact="Економія 12 ₴/день"
            ))
        elif time_of_day == "evening":
            tips.append(OptimizationTip(
                device_name="Освітлення",
                device_type=DeviceType.LIGHT,
                title="Вечір - розумне освітлення",
                description="Використовуйте локальне освітлення замість загального",
                estimated_savings=2.5,
                priority="low",
                action="Використовуйте локальні лампи",
                impact="Економія 7 ₴/день"
            ))
        elif time_of_day == "night":
            tips.append(OptimizationTip(
                device_name="Резервні пристрої",
                device_type=DeviceType.PLUG,
                title="Ніч - вимкніть резервні пристрої",
                description="Нічний час - найменше активних пристроїв",
                estimated_savings=1.0,
                priority="low",
                action="Встановіть режим сну для пристроїв",
                impact="Економія 3 ₴/день"
            ))
        
        if current_power < 100 and total_power_today > 10:
            tips.append(OptimizationTip(
                device_name="Система",
                device_type=DeviceType.PLUG,
                title="Режим очікування активний",
                description="Багато пристроїв у режимі очікування витрачають енергію",
                estimated_savings=5.0,
                priority="medium" if self.level != OptimizationLevel.MINIMAL else "low",
                action="Відключайте пристрої з розеток, коли не використовуються",
                impact="Економія 20 ₴/день"
            ))

        if device_mix:
            lights = device_mix.get(DeviceType.LIGHT, 0)
            plugs = device_mix.get(DeviceType.PLUG, 0)
            if lights >= 3 and current_power > 1500:
                tips.append(OptimizationTip(
                    device_name="Освітлення",
                    device_type=DeviceType.LIGHT,
                    title="Оптимізуйте освітлення",
                    description="Багато ламп активні одночасно",
                    estimated_savings=4.0,
                    priority="medium",
                    action="Залиште ввімкненими лише потрібні зони",
                    impact="Економія 10-15 ₴/день"
                ))
            if plugs >= 2 and total_power_today > 12:
                tips.append(OptimizationTip(
                    device_name="Розетки",
                    device_type=DeviceType.PLUG,
                    title="Перевірте навантаження розеток",
                    description="Кілька розеток можуть тягнути фонове споживання",
                    estimated_savings=3.0,
                    priority="low",
                    action="Вимкніть зарядки/адаптери без навантаження",
                    impact="Економія 5-8 ₴/день"
                ))
        
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        tips.sort(key=lambda x: (priority_order.get(x.priority, 3), -x.estimated_savings))
        
        return tips
    
    def estimate_monthly_savings(self, tips: List[OptimizationTip]) -> Dict[str, float]:
        if not tips:
            return {"total": 0, "high": 0, "medium": 0, "low": 0}
        
        daily_savings = sum(tip.estimated_savings for tip in tips)
        
        return {
            "total": daily_savings * 30,
            "high": sum(t.estimated_savings for t in tips if t.priority == "high") * 30,
            "medium": sum(t.estimated_savings for t in tips if t.priority == "medium") * 30,
            "low": sum(t.estimated_savings for t in tips if t.priority == "low") * 30,
            "daily": daily_savings
        }
    
    def get_score(self, current_power: float, daily_consumption: float) -> Tuple[int, str]:
        score = 100
        
        if current_power > 3500:
            score -= 30
        elif current_power > 3000:
            score -= 20
        elif current_power > 2500:
            score -= 10
        elif current_power > 2000:
            score -= 5
        
        if daily_consumption > 20:
            score -= 25
        elif daily_consumption > 15:
            score -= 15
        elif daily_consumption > 12:
            score -= 5
        
        score = max(0, min(100, score))
        
        if score >= 90:
            grade = "A (Відмінно)"
        elif score >= 75:
            grade = "B (Добре)"
        elif score >= 60:
            grade = "C (Нормально)"
        elif score >= 45:
            grade = "D (Низько)"
        else:
            grade = "F (Дуже низько)"
        
        return score, grade
    
    def get_peak_hour_recommendations(self, hourly_data: Dict[int, float]) -> List[str]:
        if not hourly_data:
            return []
        
        peak_hour = max(hourly_data, key=hourly_data.get)
        peak_power = hourly_data[peak_hour]
        avg_power = sum(hourly_data.values()) / len(hourly_data)
        
        recommendations = []
        
        if peak_power > avg_power * 1.5:
            recommendations.append(
                f"Пікове споживання о {peak_hour}:00 ({int(peak_power)}W). "
                f"Розгляньте перенесення енергоємних завдань на інші години."
            )
        
        low_hours = [h for h, p in hourly_data.items() if p < avg_power * 0.7]
        if low_hours:
            hours_str = ", ".join(f"{h}:00" for h in sorted(low_hours)[:3])
            recommendations.append(
                f"Низьке споживання в години: {hours_str}. "
                f"Перенесіть енергоємні операції на ці години."
            )
        
        return recommendations
    
    def to_dict(self) -> Dict:
        return {
            "level": self.level.name,
            "daily_history_count": len(self.daily_consumption_history),
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'OptimizationEngine':
        level_name = data.get("level", "BALANCED")
        level = OptimizationLevel[level_name]
        return OptimizationEngine(level)


class EnergyBudgetAnalyzer:
    def __init__(self, monthly_budget: float = 300.0):
        self.monthly_budget = monthly_budget
        self.daily_budgets = []
    
    def check_budget_status(self, today_consumption: float, 
                           today_cost: float, 
                           day_of_month: int) -> Dict[str, any]:
        daily_avg_budget = self.monthly_budget / 30
        days_left = 30 - day_of_month
        
        projected_daily_cost = (today_cost * 30) / day_of_month if day_of_month > 0 else 0
        remaining_budget = self.monthly_budget - (today_cost * (30 / day_of_month))
        
        status = "on_track"
        if projected_daily_cost > self.monthly_budget * 1.1:
            status = "over_budget"
        elif remaining_budget < 0:
            status = "exceeded"
        
        return {
            "status": status,
            "daily_budget": daily_avg_budget,
            "today_cost": today_cost,
            "projected_monthly": projected_daily_cost,
            "remaining_budget": max(0, remaining_budget),
            "days_left": days_left,
            "percentage_used": min(100, (projected_daily_cost / self.monthly_budget) * 100)
        }
    
    def get_daily_limit_recommendation(self, day_of_month: int, 
                                       cost_so_far: float) -> str:
        days_left = 30 - day_of_month
        remaining_budget = self.monthly_budget - cost_so_far
        
        if days_left <= 0:
            return "Місяць завершився!"
        
        daily_limit = remaining_budget / days_left
        
        if daily_limit < 5:
            return f"Критично! Ліміт {daily_limit:.2f}₴/день. Критично скоротьте витрати!"
        elif daily_limit < 10:
            return f"Обережно! Ліміт {daily_limit:.2f}₴/день. Зменшіть споживання!"
        else:
            return f"OK! Ліміт {daily_limit:.2f}₴/день. Дотримуйтеся розпорядку!"
