from typing import List, Optional, Tuple

from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QLineEdit,
    QPushButton,
    QStackedWidget,
    QSpinBox,
    QDoubleSpinBox,
    QCheckBox,
)

from frontend.models import RoomModel, DeviceType


class AddDeviceDialog(QDialog):
    def __init__(self, rooms: List[RoomModel], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Додати пристрій")
        self.setModal(True)
        
        # Apple-inspired styling
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
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                background: #f5f5f7;
                color: #1d1d1f;
                border: 0.5px solid rgba(0, 0, 0, 0.1);
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
            }
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
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
        """)

        self.rooms = rooms

        self.room_combo = QComboBox()
        for r in rooms:
            self.room_combo.addItem(r.name, r.id)

        self.type_combo = QComboBox()
        self.type_combo.addItem("Освітлення (Light)", DeviceType.LIGHT)
        self.type_combo.addItem("Клімат (Climate)", DeviceType.CLIMATE)
        self.type_combo.addItem("Розумна розетка (Smart Plug)", DeviceType.SMART_PLUG)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Назва пристрою (наприклад, Люстра)")

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Кімната:"))
        layout.addWidget(self.room_combo)

        layout.addWidget(QLabel("Тип пристрою:"))
        layout.addWidget(self.type_combo)

        layout.addWidget(QLabel("Назва пристрою:"))
        layout.addWidget(self.name_edit)

        self.stack = QStackedWidget()
        self._build_light_page()
        self._build_climate_page()
        self._build_plug_page()

        layout.addWidget(self.stack)

        btn_row = QHBoxLayout()
        btn_ok = QPushButton("OK")
        btn_cancel = QPushButton("Скасувати")

        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)

        btn_row.addStretch()
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_ok)
        layout.addLayout(btn_row)

        self.type_combo.currentIndexChanged.connect(
            lambda idx: self.stack.setCurrentIndex(idx)
        )


    def _build_light_page(self):
        from PyQt5.QtWidgets import QWidget, QFormLayout

        page = QWidget()
        form = QFormLayout(page)

        self.light_brightness = QSpinBox()
        self.light_brightness.setRange(0, 100)
        self.light_brightness.setValue(80)

        self.light_max_power = QDoubleSpinBox()
        self.light_max_power.setRange(1, 500)
        self.light_max_power.setDecimals(0)
        self.light_max_power.setValue(60)

        self.light_critical = QCheckBox()

        form.addRow("Яскравість, %:", self.light_brightness)
        form.addRow("Макс. потужність, Вт:", self.light_max_power)
        form.addRow("Критичний пристрій:", self.light_critical)

        self.stack.addWidget(page)

    def _build_climate_page(self):
        from PyQt5.QtWidgets import QWidget, QFormLayout

        page = QWidget()
        form = QFormLayout(page)

        self.climate_temp = QSpinBox()
        self.climate_temp.setRange(16, 30)
        self.climate_temp.setValue(24)

        self.climate_base_power = QDoubleSpinBox()
        self.climate_base_power.setRange(100, 5000)
        self.climate_base_power.setDecimals(0)
        self.climate_base_power.setValue(1200)

        self.climate_critical = QCheckBox()
        self.climate_critical.setChecked(True)

        form.addRow("Цільова температура, °C:", self.climate_temp)
        form.addRow("Базова потужність, Вт:", self.climate_base_power)
        form.addRow("Критичний пристрій:", self.climate_critical)

        self.stack.addWidget(page)

    def _build_plug_page(self):
        from PyQt5.QtWidgets import QWidget, QFormLayout

        page = QWidget()
        form = QFormLayout(page)

        self.plug_load = QDoubleSpinBox()
        self.plug_load.setRange(0, 5000)
        self.plug_load.setDecimals(0)
        self.plug_load.setValue(500)

        self.plug_critical = QCheckBox()

        form.addRow("Навантаження, Вт:", self.plug_load)
        form.addRow("Критичний пристрій:", self.plug_critical)

        self.stack.addWidget(page)

    def get_result(
        self,
    ) -> Optional[Tuple[str, DeviceType, dict]]:
        
        if self.exec_() != QDialog.Accepted:
            return None

        name = self.name_edit.text().strip() or "New Device"

        room_id = self.room_combo.currentData()
        device_type: DeviceType = self.type_combo.currentData()

        config = {"name": name}

        if device_type == DeviceType.LIGHT:
            config.update(
                {
                    "brightness": int(self.light_brightness.value()),
                    "max_power": float(self.light_max_power.value()),
                    "critical": self.light_critical.isChecked(),
                }
            )
        elif device_type == DeviceType.CLIMATE:
            config.update(
                {
                    "target_temperature": int(self.climate_temp.value()),
                    "base_power": float(self.climate_base_power.value()),
                    "critical": self.climate_critical.isChecked(),
                }
            )
        elif device_type == DeviceType.SMART_PLUG:
            config.update(
                {
                    "load_power": float(self.plug_load.value()),
                    "critical": self.plug_critical.isChecked(),
                }
            )

        return room_id, device_type, config
