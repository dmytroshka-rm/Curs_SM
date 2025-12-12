"""Optimization recommendations widget for main window."""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QScrollArea, QFrame, QPushButton, QProgressBar)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor
from frontend.optimization import OptimizationEngine, OptimizationLevel
from frontend.theme import current_theme
from collections import Counter


class OptimizationWidget(QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.engine = OptimizationEngine(OptimizationLevel.BALANCED)
        self.current_power = 0
        self.daily_consumption = 0
        self.weather_data = None
        self.optimization_level = 1
        self._theme = current_theme()
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("💡 Оптимізація")
        title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        header_layout.addWidget(title)
        
        self.level_label = QLabel("Рівень: --")
        self.level_label.setFont(QFont("Segoe UI", 9))
        self.level_label.setStyleSheet("color: #64748b;")
        header_layout.addWidget(self.level_label)
        
        self.score_label = QLabel("Оцінка: --")
        self.score_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.score_label.setStyleSheet("color: #3b82f6;")
        header_layout.addWidget(self.score_label)
        
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        self.score_bar = QProgressBar()
        self.score_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                height: 20px;
                text-align: center;
                font-weight: bold;
                font-size: 11px;
            }
            QProgressBar::chunk {
                background-color: #10b981;
                border-radius: 5px;
            }
        """)
        self.score_bar.setValue(50)
        layout.addWidget(self.score_bar)
        
        self.savings_label = QLabel("Потенційна економія: -- ₴/день")
        self.savings_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.savings_label.setStyleSheet("color: #059669;")
        layout.addWidget(self.savings_label)
        
        is_dark = self._theme == 'dark'
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(250)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                border: 1px solid {'#334155' if is_dark else '#cbd5e1'};
                background-color: {'#0f172a' if is_dark else '#f9fafb'};
                border-radius: 6px;
            }}
        """)
        
        self.recommendations_container = QWidget()
        self.recommendations_layout = QVBoxLayout(self.recommendations_container)
        self.recommendations_layout.setSpacing(6)
        self.recommendations_layout.setContentsMargins(8, 8, 8, 8)
        
        scroll.setWidget(self.recommendations_container)
        layout.addWidget(scroll)
        
        layout.addStretch()
        
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self._update_analysis)
        self.update_timer.start(60 * 1000) 
    
    def update_data(self, current_power: float, daily_consumption: float, 
                   weather_data: dict = None, time_of_day: str = None, devices: list = None):
        
        self.current_power = current_power
        self.daily_consumption = daily_consumption
        self.weather_data = weather_data
        self.time_of_day = time_of_day
        self.device_mix = Counter([getattr(d, 'type', None) for d in devices]) if devices else None
        self.engine.update_power_sample(current_power)
        self._update_analysis()
    
    def set_optimization_level(self, level: int):
        self.optimization_level = level
        level_info = {
            0: ("🟢 Відключено", "#10b981"),
            1: ("🟡 М'яка", "#f59e0b"),
            2: ("🔴 Агресивна", "#ef4444")
        }
        text, color = level_info.get(level, ("--", "#64748b"))
        self.level_label.setText(f"Рівень: {text}")
        self.level_label.setStyleSheet(f"color: {color}; font-weight: bold;")
    
    def _update_analysis(self):
        est_daily_kwh = self.daily_consumption if self.daily_consumption else self.engine.estimate_daily_kwh()
        tips = self.engine.analyze_consumption(
            current_power=self.current_power,
            total_power_today=est_daily_kwh,
            hourly_avg=est_daily_kwh / 24 if est_daily_kwh else 0,
            weather_data=self.weather_data,
            time_of_day=getattr(self, 'time_of_day', None),
            device_mix=getattr(self, 'device_mix', None)
        )
        
        score, grade = self.engine.get_score(self.current_power, self.daily_consumption)
        self.score_bar.setValue(score)
        self.score_label.setText(f"Оцінка: {score} ({grade})")
        
        if score >= 75:
            color = "#10b981"  #
        elif score >= 50:
            color = "#f59e0b"  
        else:
            color = "#ef4444"  
        
        self.score_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                height: 20px;
                text-align: center;
                font-weight: bold;
                font-size: 11px;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 5px;
            }}
        """)
        
        savings = self.engine.estimate_monthly_savings(tips)
        self.savings_label.setText(
            f"Потенційна економія: {savings['daily']:.1f} ₴/день "
            f"({savings['total']:.0f} ₴/місяць)"
        )
        
        for i in reversed(range(self.recommendations_layout.count())):
            self.recommendations_layout.itemAt(i).widget().setParent(None)
        
        if not tips:
            no_tips = QLabel("✅ Оптимально! Немає рекомендацій.")
            no_tips.setStyleSheet(f"color: {'#10b981' if self._theme == 'dark' else '#059669'}; font-weight: bold;")
            self.recommendations_layout.addWidget(no_tips)
        else:
            for tip in tips[:5]:  
                self._add_recommendation_item(tip)
        
        if len(tips) > 5:
            more = QLabel(f"... та ще {len(tips) - 5} рекомендацій")
            more.setStyleSheet(f"color: {'#94a3b8' if self._theme == 'dark' else '#94a3b8'}; font-style: italic;")
            self.recommendations_layout.addWidget(more)
    
    def _add_recommendation_item(self, tip):
        item = QFrame()
        
        # Color by priority
        dark = self._theme == 'dark'
        if tip.priority == "high":
            border_color = "#ef4444"
            bg_color = "#2f1515" if dark else "#fef2f2"
        elif tip.priority == "medium":
            border_color = "#f59e0b"
            bg_color = "#2f2410" if dark else "#fffbeb"
        else:
            border_color = "#3b82f6"
            bg_color = "#152238" if dark else "#eff6ff"
        
        item.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border-left: 3px solid {border_color};
                border-radius: 4px;
                padding: 8px;
            }}
        """)
        
        layout = QVBoxLayout(item)
        layout.setSpacing(4)
        layout.setContentsMargins(8, 6, 8, 6)
        
        title = QLabel(f"{tip.title} ({tip.estimated_savings:.1f} ₴/день)")
        title.setFont(QFont("Segoe UI", 10, QFont.Bold))
        title.setStyleSheet(f"color: {'#e5e7eb' if dark else '#0f172a'};")
        layout.addWidget(title)
        
        desc = QLabel(tip.description)
        desc.setWordWrap(True)
        desc.setFont(QFont("Segoe UI", 9))
        desc.setStyleSheet(f"color: {'#cbd5e1' if dark else '#4b5563'};")
        layout.addWidget(desc)
        
        action = QLabel(f"→ {tip.action}")
        action.setFont(QFont("Segoe UI", 9, QFont.Bold))
        action.setStyleSheet(f"color: {border_color};")
        layout.addWidget(action)
        
        impact = QLabel(f"💰 {tip.impact}")
        impact.setFont(QFont("Segoe UI", 8))
        impact.setStyleSheet(f"color: {'#22c55e' if dark else '#059669'};")
        layout.addWidget(impact)
        
        self.recommendations_layout.addWidget(item)
    
    def set_optimization_level(self, level: OptimizationLevel):
        self.engine.level = level
        self._update_analysis()


class BudgetWidget(QWidget):
    
    def __init__(self, monthly_budget: float = 300.0, parent=None):
        super().__init__(parent)
        self.monthly_budget = monthly_budget
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)
        
        header_layout = QHBoxLayout()
        
        self.title = QLabel("💰 Бюджет місяця")
        self.title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        header_layout.addWidget(self.title)
        
        header_layout.addStretch()
        
        from PyQt5.QtWidgets import QPushButton
        btn_settings = QPushButton("⚙️")
        btn_settings.setMaximumWidth(35)
        btn_settings.setToolTip("Налаштувати бюджет")
        btn_settings.clicked.connect(self._on_settings_clicked)
        header_layout.addWidget(btn_settings)
        
        layout.addLayout(header_layout)
        
        self.budget_bar = QProgressBar()
        self.budget_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                height: 22px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #3b82f6;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.budget_bar)
        
        self.info_label = QLabel("Оновлюю...")
        self.info_label.setWordWrap(True)
        self.info_label.setFont(QFont("Segoe UI", 9))
        layout.addWidget(self.info_label)
        
        self.daily_label = QLabel("Щоденний ліміт: --")
        self.daily_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        layout.addWidget(self.daily_label)
        
        layout.addStretch()
    
    def update_budget_status(self, today_cost: float, day_of_month: int):
        if day_of_month < 1:
            day_of_month = 1
        
        projected = (today_cost * 30) / day_of_month if day_of_month > 0 else 0
        percentage = min(100, (projected / self.monthly_budget) * 100)
        
        self.budget_bar.setValue(int(percentage))
        
        # Status color
        if percentage > 110:
            color = "#ef4444"  
            status = "ПЕРЕВИЩЕНО!"
        elif percentage > 100:
            color = "#f59e0b"  
            status = "Зі перевищенням"
        else:
            color = "#10b981" 
            status = "В межах бюджету"
        
        self.budget_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                height: 22px;
                text-align: center;
                font-weight: bold;
                color: {color};
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 5px;
            }}
        """)
        
        days_left = 30 - day_of_month
        remaining = max(0, self.monthly_budget - projected)
        
        self.info_label.setText(
            f"Витрачено: {projected:.0f} ₴ ({percentage:.0f}%) | "
            f"Залишилось: {remaining:.0f} ₴\n"
            f"День {day_of_month}/30 | {status}"
        )
        
        if days_left > 0:
            daily_limit = remaining / days_left
            if daily_limit < 5:
                self.daily_label.setText(f"⚠️ Критично! Ліміт: {daily_limit:.2f}₴/день")
                self.daily_label.setStyleSheet("color: #ef4444; font-weight: bold;")
            elif daily_limit < 10:
                self.daily_label.setText(f"⚠️ Обережно! Ліміт: {daily_limit:.2f}₴/день")
                self.daily_label.setStyleSheet("color: #f59e0b; font-weight: bold;")
            else:
                self.daily_label.setText(f"✅ OK! Ліміт: {daily_limit:.2f}₴/день")
                self.daily_label.setStyleSheet("color: #10b981; font-weight: bold;")
        else:
            self.daily_label.setText("Місяць завершився!")
    
    def _on_settings_clicked(self):
        from frontend.windows.budget_dialog import BudgetDialog
        new_budget = BudgetDialog.get_budget_from_user(self.monthly_budget, self)
        if new_budget != self.monthly_budget:
            self.monthly_budget = new_budget
