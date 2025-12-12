from typing import Callable, Optional
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox,
    QPushButton, QCheckBox, QComboBox, QMessageBox, QTableWidget, QTableWidgetItem
)
from PyQt5.QtCore import Qt
from frontend.models import ScheduleEntryModel


DAYS = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота", "Неділя"]


class ScheduleEditorDialog(QDialog):
    
    def __init__(self, device_id: str, device_name: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Розклад - {device_name}")
        self.setModal(True)
        self.resize(600, 400)
        
        self.setStyleSheet("""
            QDialog {
                background: #ffffff;
                color: #1d1d1f;
            }
            QLabel {
                color: #1d1d1f;
                font-size: 13px;
                font-weight: 500;
            }
            QComboBox, QSpinBox {
                background: #f5f5f7;
                color: #1d1d1f;
                border: 0.5px solid rgba(0, 0, 0, 0.1);
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
            }
            QComboBox:focus, QSpinBox:focus {
                border: 1px solid #007aff;
                background: #ffffff;
            }
            QPushButton {
                background: #007aff;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                color: white;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #0051d5;
            }
            QPushButton:pressed {
                background: #004ecb;
            }
            QCheckBox {
                color: #1d1d1f;
                font-size: 13px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid rgba(0, 0, 0, 0.15);
                border-radius: 4px;
                background: #ffffff;
            }
            QCheckBox::indicator:checked {
                background: #007aff;
                border: 1px solid #007aff;
            }
            QTableWidget {
                background: #ffffff;
                color: #1d1d1f;
                border: 0.5px solid rgba(0, 0, 0, 0.1);
                border-radius: 8px;
            }
        """)
        
        self.device_id = device_id
        self.schedules = {}  
        
        layout = QVBoxLayout(self)
        
        # Вибір дня тижня
        day_layout = QHBoxLayout()
        day_layout.addWidget(QLabel("День тижня:"))
        self.day_combo = QComboBox()
        self.day_combo.addItems(DAYS)
        day_layout.addWidget(self.day_combo)
        day_layout.addStretch()
        layout.addLayout(day_layout)
        
        # Контроль вмикання
        on_layout = QHBoxLayout()
        on_layout.addWidget(QLabel("Вмикати о:"))
        self.on_hour = QSpinBox()
        self.on_hour.setRange(0, 23)
        self.on_hour.setValue(7)
        on_layout.addWidget(self.on_hour)
        on_layout.addWidget(QLabel(":"))
        self.on_minute = QSpinBox()
        self.on_minute.setRange(0, 59)
        on_layout.addWidget(self.on_minute)
        on_layout.addStretch()
        layout.addLayout(on_layout)
        
        # Контроль вимикання
        off_layout = QHBoxLayout()
        off_layout.addWidget(QLabel("Вимикати о:"))
        self.off_hour = QSpinBox()
        self.off_hour.setRange(0, 23)
        self.off_hour.setValue(23)
        off_layout.addWidget(self.off_hour)
        off_layout.addWidget(QLabel(":"))
        self.off_minute = QSpinBox()
        self.off_minute.setRange(0, 59)
        off_layout.addWidget(self.off_minute)
        off_layout.addStretch()
        layout.addLayout(off_layout)
        
        # Чекбокс для активації
        self.enabled_check = QCheckBox("Активний")
        self.enabled_check.setChecked(True)
        layout.addWidget(self.enabled_check)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("Зберегти")
        btn_save.clicked.connect(self._save_schedule)
        btn_layout.addWidget(btn_save)
        
        btn_delete = QPushButton("Видалити")
        btn_delete.clicked.connect(self._delete_schedule)
        btn_layout.addWidget(btn_delete)
        
        btn_close = QPushButton("Закрити")
        btn_close.clicked.connect(self.accept) 
        btn_layout.addWidget(btn_close)
        
        layout.addLayout(btn_layout)
    
    def _save_schedule(self):
        day = self.day_combo.currentIndex()
        entry = ScheduleEntryModel(
            device_id=self.device_id,
            day_of_week=day,
            enabled=self.enabled_check.isChecked(),
            turn_on_hour=self.on_hour.value(),
            turn_on_minute=self.on_minute.value(),
            turn_off_hour=self.off_hour.value(),
            turn_off_minute=self.off_minute.value(),
        )
        self.schedules[day] = entry
        QMessageBox.information(self, "Успішно", f"Розклад на {DAYS[day]} збережено")
    
    def _delete_schedule(self):
        day = self.day_combo.currentIndex()
        if day in self.schedules:
            del self.schedules[day]
            QMessageBox.information(self, "Успішно", f"Розклад на {DAYS[day]} видалено")
    
    def get_schedules(self):
        return self.schedules
