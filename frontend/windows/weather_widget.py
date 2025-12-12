from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QScrollArea, QLineEdit)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QColor
from frontend.weather import WeatherClient
import re


class WeatherWidget(QFrame):
    
    weather_updated = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._apply_styles()
        self.weather_client = WeatherClient()
        self._weather_data = None
        self._current_location_label = "Київ"
        self._init_ui()
        self._start_update_timer()

    def _is_dark_theme(self) -> bool:
        col = self.palette().window().color()
        if isinstance(col, QColor):
            r, g, b = col.red(), col.green(), col.blue()
            luminance = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255.0
            return luminance < 0.5
        return False

    def _apply_styles(self):
        is_dark = self._is_dark_theme()
        frame_bg = "#111827" if is_dark else "#ecf0f1"
        frame_border = "#1f2937" if is_dark else "#bdc3c7"
        rec_bg = "#0f172a" if is_dark else "white"
        rec_border = "#334155" if is_dark else "#bdc3c7"
        rec_item_bg = "#1e293b" if is_dark else "#f9f9f9"
        rec_item_border = "#3b82f6" if is_dark else "#3498db"

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {frame_bg};
                border-radius: 8px;
                border: 1px solid {frame_border};
                padding: 10px;
            }}
            QScrollArea {{
                border: 1px solid {rec_border};
                background-color: {rec_bg};
                border-radius: 6px;
            }}
            QFrame#recItem {{
                background-color: {rec_item_bg};
                border-left: 3px solid {rec_item_border};
                padding: 5px;
                border-radius: 3px;
            }}
            QLabel#recTitle {{
                color: {'#e5e7eb' if is_dark else '#2c3e50'};
                font-weight: 600;
            }}
            QLabel#recText {{
                color: {'#cbd5e1' if is_dark else '#2c3e50'};
            }}
        """)
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)

        location_layout = QHBoxLayout()
        location_title = QLabel("Локація:")
        location_title.setFont(QFont("Arial", 10, QFont.Bold))
        location_layout.addWidget(location_title)

        self.location_display = QLabel("Київ")
        self.location_display.setFont(QFont("Arial", 10))
        location_layout.addWidget(self.location_display)
        location_layout.addStretch()

        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("Місто або '50.45, 30.52'")
        self.location_input.setFixedWidth(220)
        location_layout.addWidget(self.location_input)

        self.set_location_btn = QPushButton("Задати")
        self.set_location_btn.setMinimumWidth(80)
        self.set_location_btn.clicked.connect(self._handle_location_change)
        location_layout.addWidget(self.set_location_btn)

        layout.addLayout(location_layout)

        self.location_status = QLabel("За замовчуванням: Київ")
        self.location_status.setStyleSheet("color: #6b7280; font-size: 10px;")
        layout.addWidget(self.location_status)

        weather_layout = QHBoxLayout()
        
        self.weather_icon_label = QLabel("☀️")
        self.weather_icon_label.setFont(QFont("Arial", 32))
        weather_layout.addWidget(self.weather_icon_label)
        
        info_layout = QVBoxLayout()
        
        self.temp_label = QLabel("--°C")
        self.temp_label.setFont(QFont("Arial", 20, QFont.Bold))
        info_layout.addWidget(self.temp_label)
        
        self.condition_label = QLabel("Завантаження...")
        self.condition_label.setFont(QFont("Arial", 10))
        info_layout.addWidget(self.condition_label)
        
        details_layout = QHBoxLayout()
        self.humidity_label = QLabel("💧 --% ")
        self.wind_label = QLabel("💨 -- км/год")
        details_layout.addWidget(self.humidity_label)
        details_layout.addWidget(self.wind_label)
        info_layout.addLayout(details_layout)
        
        weather_layout.addLayout(info_layout, 1)
        
        self.refresh_btn = QPushButton("Оновити")
        self.refresh_btn.setMinimumWidth(90)
        self.refresh_btn.setMaximumWidth(120)
        self.refresh_btn.clicked.connect(self._load_weather)
        weather_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(weather_layout)
        
        rec_label = QLabel("💡 Рекомендації:")
        rec_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(rec_label)
        
        self.recommendations_area = QScrollArea()
        self.recommendations_area.setWidgetResizable(True)
        self.recommendations_area.setMinimumHeight(140)
        self.recommendations_area.setMaximumHeight(240)
        
        self.recommendations_container = QFrame()
        self.recommendations_layout = QVBoxLayout(self.recommendations_container)
        self.recommendations_layout.setSpacing(6)
        self.recommendations_layout.setContentsMargins(8, 8, 8, 8)
        
        self.recommendations_area.setWidget(self.recommendations_container)
        layout.addWidget(self.recommendations_area)
        
        layout.addStretch()
    
    def _load_weather(self):
        data = self.weather_client.get_current_weather()
        if data:
            self._weather_data = data
            self._update_weather_display(data)
            self.weather_updated.emit(data)
            
            rec_data = self.weather_client.get_energy_recommendations()
            if rec_data:
                self._update_recommendations(rec_data.get("recommendations", []))

    def _handle_location_change(self):
        text = (self.location_input.text() or "").strip()
        if not text:
            return

        coords = self._parse_coordinates(text)
        if coords:
            latitude, longitude = coords
            display_name = f"{latitude:.2f}, {longitude:.2f}"
        else:
            result = self.weather_client.search_location(text)
            if not result:
                self.location_status.setText("Локацію не знайдено")
                return
            latitude = result.get("latitude")
            longitude = result.get("longitude")
            name = result.get("name")
            country = result.get("country")
            display_name = f"{name}, {country}" if country else name

        if latitude is None or longitude is None:
            self.location_status.setText("Координати недоступні")
            return

        self.weather_client.set_location(float(latitude), float(longitude))
        self._set_location_label(display_name, float(latitude), float(longitude))
        self.location_status.setText("Локацію оновлено")
        self._load_weather()

    @staticmethod
    def _parse_coordinates(text: str):
        match = re.match(r"\s*([+-]?\d+(?:\.\d+)?)\s*[ ,]\s*([+-]?\d+(?:\.\d+)?)\s*", text)
        if match:
            try:
                lat = float(match.group(1))
                lon = float(match.group(2))
                return lat, lon
            except ValueError:
                return None
        return None

    def _set_location_label(self, label: str, lat: float, lon: float):
        self._current_location_label = label or f"{lat:.2f}, {lon:.2f}"
        self.location_display.setText(self._current_location_label)
    
    def _update_weather_display(self, data: dict):
        temp = data.get("temperature")
        if temp is not None:
            self.temp_label.setText(f"{int(temp)}°C")
        
        condition = data.get("weather_description", "Невідома")
        self.condition_label.setText(condition)
        
        humidity = data.get("humidity")
        if humidity is not None:
            self.humidity_label.setText(f"💧 {humidity}%")
        
        wind = data.get("wind_speed")
        if wind is not None:
            self.wind_label.setText(f"💨 {int(wind)} км/год")
        
        icon = self._get_weather_icon(data.get("weather_code"))
        self.weather_icon_label.setText(icon)
    
    def _update_recommendations(self, recommendations: list):
        is_dark = self._is_dark_theme()
        for i in reversed(range(self.recommendations_layout.count())):
            self.recommendations_layout.itemAt(i).widget().setParent(None)
        
        if not recommendations:
            no_rec = QLabel("Немає спеціальних рекомендацій")
            no_rec.setStyleSheet(f"color: {'#9ca3af' if is_dark else '#7f8c8d'}; font-size: 10px;")
            self.recommendations_layout.addWidget(no_rec)
        else:
            for rec in recommendations:
                rec_frame = QFrame()
                rec_frame.setObjectName("recItem")
                rec_layout = QHBoxLayout(rec_frame)
                rec_layout.setSpacing(5)
                rec_layout.setContentsMargins(5, 3, 5, 3)
                
                emoji = QLabel(rec["emoji"])
                emoji.setFont(QFont("Arial", 14))
                emoji.setMaximumWidth(25)
                rec_layout.addWidget(emoji)
                
                text_layout = QVBoxLayout()
                title = QLabel(rec["title"])
                title.setObjectName("recTitle")
                title.setFont(QFont("Arial", 9, QFont.Bold))
                if is_dark:
                    title.setStyleSheet("color: #e5e7eb;")
                message = QLabel(rec["message"])
                message.setObjectName("recText")
                message.setFont(QFont("Arial", 9))
                if is_dark:
                    message.setStyleSheet("color: #cbd5e1;")
                message.setWordWrap(True)
                text_layout.addWidget(title)
                text_layout.addWidget(message)
                rec_layout.addLayout(text_layout, 1)
                
                self.recommendations_layout.addWidget(rec_frame)
    
    @staticmethod
    def _get_weather_icon(code: int) -> str:
        if code is None:
            return "❓"
        elif code == 0:
            return "☀️"
        elif code in [1, 2]:
            return "⛅"
        elif code == 3:
            return "☁️"
        elif code in [45, 48]:
            return "🌫️"
        elif code in [51, 53, 55, 61, 63, 65]:
            return "🌧️"
        elif code in [71, 73, 75, 77]:
            return "❄️"
        elif code in [80, 81, 82]:
            return "⛈️"
        else:
            return "🌤️"
    
    def _start_update_timer(self):
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self._load_weather)
        self.update_timer.start(10 * 60 * 1000)
        
        self._load_weather()
    
    def set_location(self, latitude: float, longitude: float):
        self.weather_client.set_location(latitude, longitude)
        self._load_weather()
