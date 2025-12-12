import requests
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import json


class WeatherClient:
    BASE_URL = "https://api.open-meteo.com/v1/forecast"
    
    def __init__(self, latitude: float = 50.4501, longitude: float = 30.5234):
        self.latitude = latitude
        self.longitude = longitude
        self._cache = {}
        self._cache_time = None
    
    def set_location(self, latitude: float, longitude: float):
        self.latitude = latitude
        self.longitude = longitude
        self._cache.clear()

    def search_location(self, query: str) -> Optional[Dict[str, Any]]:
        try:
            params = {
                "name": query,
                "count": 1,
                "language": "uk",
                "format": "json",
            }
            response = requests.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params=params,
                timeout=5,
            )
            response.raise_for_status()
            data = response.json()
            results = data.get("results") or []
            if not results:
                return None
            first = results[0]
            return {
                "name": first.get("name"),
                "country": first.get("country"),
                "latitude": first.get("latitude"),
                "longitude": first.get("longitude"),
            }
        except Exception as e:
            print(f"Error searching location: {e}")
            return None
    
    def get_current_weather(self) -> Optional[Dict[str, Any]]:
        try:
            params = {
                "latitude": self.latitude,
                "longitude": self.longitude,
                "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
                "hourly": "temperature_2m,weather_code",
                "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum",
                "timezone": "Europe/Kiev"
            }
            
            response = requests.get(
                self.BASE_URL,
                params=params,
                timeout=5
            )
            response.raise_for_status()
            
            data = response.json()
            current = data.get("current", {})
            
            return {
                "temperature": current.get("temperature_2m"),
                "humidity": current.get("relative_humidity_2m"),
                "wind_speed": current.get("wind_speed_10m"),
                "weather_code": current.get("weather_code"),
                "weather_description": self._get_weather_description(current.get("weather_code")),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            print(f"Error fetching weather: {e}")
            return None
    
    def get_forecast(self, days: int = 7) -> Optional[Dict[str, Any]]:
        try:
            params = {
                "latitude": self.latitude,
                "longitude": self.longitude,
                "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum",
                "timezone": "Europe/Kiev",
                "forecast_days": min(days, 7)
            }
            
            response = requests.get(
                self.BASE_URL,
                params=params,
                timeout=5
            )
            response.raise_for_status()
            
            data = response.json()
            daily = data.get("daily", {})
            
            forecast = []
            for i in range(len(daily.get("time", []))):
                forecast.append({
                    "date": daily["time"][i],
                    "temp_max": daily["temperature_2m_max"][i],
                    "temp_min": daily["temperature_2m_min"][i],
                    "weather_code": daily["weather_code"][i],
                    "weather_description": self._get_weather_description(daily["weather_code"][i]),
                    "precipitation": daily["precipitation_sum"][i],
                })
            
            return {
                "forecast": forecast,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            print(f"Error fetching forecast: {e}")
            return None
    
    def get_energy_recommendations(self) -> Optional[Dict[str, Any]]:
        try:
            weather = self.get_current_weather()
            if not weather:
                return None
            
            recommendations = []
            
            temp = weather.get("temperature")
            if temp is not None:
                if temp > 25:
                    recommendations.append({
                        "type": "climate",
                        "emoji": "❄️",
                        "title": "Спека!",
                        "message": f"Температура {temp}°C. Розгляньте кондиціонер!",
                        "priority": "high"
                    })
                elif temp < 5:
                    recommendations.append({
                        "type": "climate",
                        "emoji": "🔥",
                        "title": "Холодно!",
                        "message": f"Температура {temp}°C. Перевірте опалення!",
                        "priority": "high"
                    })
            
            humidity = weather.get("humidity")
            if humidity is not None:
                if humidity > 70:
                    recommendations.append({
                        "type": "energy",
                        "emoji": "💨",
                        "title": "Висока вологість",
                        "message": f"Вологість {humidity}%. Увімкніть вентиляцію!",
                        "priority": "medium"
                    })
            
            wind = weather.get("wind_speed")
            if wind is not None and wind > 20:
                recommendations.append({
                    "type": "energy",
                    "emoji": "🌪️",
                    "title": "Сильний вітер",
                    "message": f"Вітер {wind} км/год. Перевірте ущільнення вікон!",
                    "priority": "medium"
                })
            
            code = weather.get("weather_code")
            if code in [80, 81, 82]:
                recommendations.append({
                    "type": "energy",
                    "emoji": "☔",
                    "title": "Дощ",
                    "message": "Дощова погода. Розгляньте природне освітлення!",
                    "priority": "low"
                })
            elif code in [1, 2, 3]:
                recommendations.append({
                    "type": "energy",
                    "emoji": "☀️",
                    "title": "Сонячна погода",
                    "message": "Використовуйте природне світло!",
                    "priority": "low"
                })
            
            return {
                "recommendations": recommendations,
                "weather": weather,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            return None
    
    @staticmethod
    def _get_weather_description(code: Optional[int]) -> str:
        weather_codes = {
            0: "Ясно",
            1: "Переважно ясно",
            2: "Частково хмарно",
            3: "Хмарно",
            45: "Туманно",
            48: "Туман з інеєм",
            51: "Дріжджова морось",
            53: "Помірна морось",
            55: "Густа морось",
            61: "Слабкий дощ",
            63: "Помірний дощ",
            65: "Сильний дощ",
            71: "Слабкий сніг",
            73: "Помірний сніг",
            75: "Сильний сніг",
            77: "Зернистий сніг",
            80: "Слабкі дощові грози",
            81: "Помірні дощові грози",
            82: "Сильні дощові грози",
            85: "Слабкі снігові грози",
            86: "Сильні снігові грози",
            95: "Гроза",
            96: "Гроза з градом",
            99: "Гроза з великим градом",
        }
        return weather_codes.get(code, "Невідома погода")
