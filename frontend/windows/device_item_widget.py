from typing import Callable, Optional

from PyQt5.QtCore import Qt, QTimer, QVariantAnimation, QPropertyAnimation, QEasingCurve, QPoint
import os
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QCheckBox,
    QSlider,
    QSpinBox,
    QDoubleSpinBox,
    QPushButton,
    QFrame,
    QGraphicsDropShadowEffect,
)

from frontend.models import DeviceModel, DeviceType


class DeviceItemWidget(QFrame):

    def __init__(
        self,
        device: DeviceModel,
        on_state_changed: Callable[[DeviceModel], None],
        on_delete: Optional[Callable[[str], None]] = None,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self._device = device
        self._on_state_changed = on_state_changed
        self._on_delete = on_delete

        self._debounce_timer = QTimer(self)
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.setInterval(400)

        self.setObjectName("deviceCard")
        self.setFrameShape(QFrame.NoFrame)

        try:
            self._shadow = QGraphicsDropShadowEffect(self)
            self._shadow.setBlurRadius(6)
            self._shadow.setOffset(0, 3)
            from PyQt5.QtGui import QColor
            self._shadow.setColor(QColor(0, 0, 0, 100))
            self.setGraphicsEffect(self._shadow)

            self._shadow_anim = QVariantAnimation(self)
            self._shadow_anim.setDuration(180)

            self._shadow_anim.setStartValue(6)
            self._shadow_anim.setEndValue(12)
            self._shadow_anim.valueChanged.connect(self._on_shadow_value_changed)
            try:
                self._pos_anim = QPropertyAnimation(self, b"pos", self)
                self._pos_anim.setDuration(180)
                self._pos_anim.setEasingCurve(QEasingCurve.OutQuad)
            except Exception:
                self._pos_anim = None
        except Exception:
            self._shadow = None
            self._shadow_anim = None

        self._build_ui()
        self._update_ui_from_model()


    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        header = QHBoxLayout()
        header.setSpacing(8)

        try:
            from frontend.icon_utils import get_device_icon, get_pixmap
            self.icon_label = QLabel()
            self.icon_label.setFixedSize(32, 32)
            self.icon_label.setObjectName("thumbnail")
            
            device_type = self._device.type.name 
            pix = get_device_icon(device_type, self._device.is_on, 36)
            
            if pix.isNull():
                icon_name = 'device.svg'
                if self._device.type == DeviceType.LIGHT:
                    icon_name = 'light.svg'
                elif self._device.type == DeviceType.SMART_PLUG:
                    icon_name = 'plug.svg'
                elif self._device.type == DeviceType.CLIMATE:
                    icon_name = 'climate.svg'
                pix = get_pixmap(icon_name, 36)
            
            if not pix.isNull():
                self.icon_label.setPixmap(pix)
            header.addWidget(self.icon_label)
        except Exception:
            pass

        # Назва пристрою
        name_container = QVBoxLayout()
        name_container.setSpacing(2)
        
        self.name_label = QLabel(self._device.name)
        self.name_label.setObjectName("deviceName")
        font = self.name_label.font()
        font.setPointSize(12)
        font.setBold(True)
        self.name_label.setFont(font)

        self.room_label = QLabel(self._device.room)
        self.room_label.setObjectName("roomName")
        room_font = self.room_label.font()
        room_font.setPointSize(11)
        self.room_label.setFont(room_font)
        self.room_label.setStyleSheet("color: #666666;")

        name_container.addWidget(self.name_label)
        name_container.addWidget(self.room_label)

        header.addLayout(name_container)
        header.addStretch()

        # Потужність
        self.power_label = QLabel(f"{self._device.current_power:.0f} Вт")
        self.power_label.setObjectName("powerLabel")
        power_font = self.power_label.font()
        power_font.setPointSize(11)
        power_font.setBold(True)
        self.power_label.setFont(power_font)
        self.power_label.setStyleSheet("color: #2c3e50;")
        header.addWidget(self.power_label)
        
        # Кнопка розкладу
        self.btn_schedule = QPushButton("⏰ Розклад")
        self.btn_schedule.setObjectName("btnSchedule")
        self.btn_schedule.setToolTip("Встановити розклад роботи")
        self.btn_schedule.clicked.connect(self._on_schedule_clicked)
        header.addWidget(self.btn_schedule)
        
        # Кнопка видалення
        if self._on_delete is not None:
            self.btn_delete = QPushButton("Видалити")
            self.btn_delete.setObjectName("btnDelete")
            self.btn_delete.clicked.connect(lambda: self._on_delete(self._device.id))
            header.addWidget(self.btn_delete)

        layout.addLayout(header)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("color: #e0e0e0;")
        layout.addWidget(separator)

        row_on = QHBoxLayout()
        row_on.setSpacing(8)
        self.cb_on = QCheckBox("Увімкнено")
        self.cb_on.setStyleSheet("""
            QCheckBox {
                font-size: 11px;
            }
        """)
        row_on.addWidget(self.cb_on)
        row_on.addStretch()
        layout.addLayout(row_on)

        if self._device.type == DeviceType.LIGHT:
            self._build_light_controls(layout)
        elif self._device.type == DeviceType.CLIMATE:
            self._build_climate_controls(layout)
        elif self._device.type == DeviceType.SMART_PLUG:
            self._build_plug_controls(layout)

        self.cb_on.stateChanged.connect(self._on_any_change)

    def _build_light_controls(self, parent_layout: QVBoxLayout):
        """Контролли для освітлення."""
        container = QVBoxLayout()
        container.setSpacing(6)

        label_row = QHBoxLayout()
        label = QLabel("Яскравість:")
        label.setStyleSheet("font-size: 12px; color: #555555;")
        label_row.addWidget(label)
        label_row.addStretch()
        
        self.brightness_value_label = QLabel("0%")
        self.brightness_value_label.setStyleSheet("font-size: 12px; color: #666666; font-weight: 500;")
        label_row.addWidget(self.brightness_value_label)
        container.addLayout(label_row)

        slider_row = QHBoxLayout()
        self.slider_brightness = QSlider(Qt.Horizontal)
        self.slider_brightness.setRange(0, 100)
        self.slider_brightness.setMinimumHeight(30)
        slider_row.addWidget(self.slider_brightness)
        container.addLayout(slider_row)

        parent_layout.addLayout(container)

        def _on_slider_value(v):
            self.brightness_value_label.setText(f"{v}%")
            try:
                self._device.brightness = int(v)
            except Exception:
                pass
            self._debounce_timer.start()

        self.slider_brightness.valueChanged.connect(_on_slider_value)
        self._debounce_timer.timeout.connect(self._on_any_change)

    def _build_climate_controls(self, parent_layout: QVBoxLayout):
        """Контролли для клімату."""
        container = QVBoxLayout()
        container.setSpacing(6)

        label_row = QHBoxLayout()
        label = QLabel("Цільова температура:")
        label.setStyleSheet("font-size: 12px; color: #555555;")
        label_row.addWidget(label)
        label_row.addStretch()
        container.addLayout(label_row)

        spin_row = QHBoxLayout()
        self.spin_temp = QSpinBox()
        self.spin_temp.setRange(14, 30)
        self.spin_temp.setSuffix(" °C")
        self.spin_temp.setStyleSheet("""
            QSpinBox {
                font-size: 13px;
                padding: 6px;
            }
        """)
        spin_row.addWidget(self.spin_temp)
        spin_row.addStretch()
        container.addLayout(spin_row)

        parent_layout.addLayout(container)

        self.spin_temp.editingFinished.connect(self._on_any_change)

    def _build_plug_controls(self, parent_layout: QVBoxLayout):
        container = QVBoxLayout()
        container.setSpacing(6)

        label_row = QHBoxLayout()
        label = QLabel("Навантаження:")
        label.setStyleSheet("font-size: 12px; color: #555555;")
        label_row.addWidget(label)
        label_row.addStretch()
        container.addLayout(label_row)

        spin_row = QHBoxLayout()
        self.spin_load = QDoubleSpinBox()
        self.spin_load.setRange(0, 5000)
        self.spin_load.setDecimals(0)
        self.spin_load.setSuffix(" Вт")
        self.spin_load.setStyleSheet("""
            QDoubleSpinBox {
                font-size: 13px;
                padding: 6px;
            }
        """)
        spin_row.addWidget(self.spin_load)
        spin_row.addStretch()
        container.addLayout(spin_row)

        parent_layout.addLayout(container)

        self.spin_load.editingFinished.connect(self._on_any_change)


    def _update_ui_from_model(self):
        self.cb_on.blockSignals(True)
        self.cb_on.setChecked(self._device.is_on)
        self.cb_on.blockSignals(False)

        self.power_label.setText(f"{self._device.current_power:.0f} Вт")
        
        try:
            from frontend.icon_utils import get_device_icon
            if hasattr(self, 'icon_label'):
                device_type = self._device.type.name
                pix = get_device_icon(device_type, self._device.is_on, 36)
                if not pix.isNull():
                    self.icon_label.setPixmap(pix)
        except Exception:
            pass

        if self._device.type == DeviceType.LIGHT:
            brightness = self._device.brightness if self._device.brightness is not None else 0
            self.slider_brightness.blockSignals(True)
            self.slider_brightness.setValue(brightness)
            self.slider_brightness.blockSignals(False)
            if hasattr(self, 'brightness_value_label'):
                self.brightness_value_label.setText(f"{brightness}%")
        elif self._device.type == DeviceType.CLIMATE:
            self.spin_temp.blockSignals(True)
            self.spin_temp.setValue(self._device.target_temperature if self._device.target_temperature is not None else 22)
            self.spin_temp.blockSignals(False)
        elif self._device.type == DeviceType.SMART_PLUG:
            self.spin_load.blockSignals(True)
            self.spin_load.setValue(self._device.load_power if self._device.load_power is not None else 0.0)
            self.spin_load.blockSignals(False)

    def _on_shadow_value_changed(self, v):
        try:
            if not getattr(self, '_shadow', None):
                return
            val = float(v)
            self._shadow.setBlurRadius(val)
            off = max(1.5, val / 4.0)
            self._shadow.setOffset(0, off)
        except Exception:
            pass

    def enterEvent(self, event):
        super().enterEvent(event)
        try:
            if getattr(self, '_shadow_anim', None) is not None:
                self._shadow_anim.setDirection(self._shadow_anim.Forward)
                self._shadow_anim.start()
            if getattr(self, '_pos_anim', None) is not None:
                try:
                    start = self.pos()
                    end = QPoint(self.x(), self.y() - 4)
                    self._pos_anim.stop()
                    self._pos_anim.setStartValue(start)
                    self._pos_anim.setEndValue(end)
                    self._pos_anim.start()
                except Exception:
                    pass
        except Exception:
            pass

    def leaveEvent(self, event):
        super().leaveEvent(event)
        try:
            if getattr(self, '_shadow_anim', None) is not None:
                self._shadow_anim.setDirection(self._shadow_anim.Backward)
                self._shadow_anim.start()
            if getattr(self, '_pos_anim', None) is not None:
                try:
                    end = self.pos()

                    target = QPoint(self.x(), self.y() + 4)
                    self._pos_anim.stop()
                    self._pos_anim.setStartValue(end)
                    self._pos_anim.setEndValue(target)
                    self._pos_anim.start()
                except Exception:
                    pass
        except Exception:
            pass

    def _collect_state_from_ui(self) -> dict:
        state = {"is_on": self.cb_on.isChecked()}

        if self._device.type == DeviceType.LIGHT:
            state["brightness"] = int(self.slider_brightness.value())
        elif self._device.type == DeviceType.CLIMATE:
            state["target_temperature"] = int(self.spin_temp.value())
        elif self._device.type == DeviceType.SMART_PLUG:
            state["load_power"] = float(self.spin_load.value())

        return state
    

    def _on_any_change(self):
        """Обробник зміни стану пристрою."""
        state = self._collect_state_from_ui()
        if self._on_state_changed:
            self._on_state_changed(
                DeviceModel(
                    **{
                        **self._device.__dict__,
                        "is_on": state.get("is_on", self._device.is_on),
                        "brightness": state.get(
                            "brightness", self._device.brightness
                        ),
                        "target_temperature": state.get(
                            "target_temperature", self._device.target_temperature
                        ),
                        "load_power": state.get(
                            "load_power", self._device.load_power
                        ),
                    }
                )
            )

    @property
    def device(self) -> DeviceModel:
        return self._device

    def update_from_device(self, device: DeviceModel, preserve_user_input: bool = True):

        if preserve_user_input:
  
            old_is_on = self._device.is_on
            old_power = self._device.current_power
            
            old_brightness = None
            old_temp = None
            old_load = None
            
            if self._device.type == DeviceType.LIGHT and hasattr(self, 'slider_brightness'):
                old_brightness = self.slider_brightness.value()
            elif self._device.type == DeviceType.CLIMATE and hasattr(self, 'spin_temp'):
                old_temp = self.spin_temp.value()
            elif self._device.type == DeviceType.SMART_PLUG and hasattr(self, 'spin_load'):
                old_load = self.spin_load.value()
            
            self._device = device
            
            if self._device.type == DeviceType.LIGHT and old_brightness is not None:
                self._device.brightness = old_brightness
            elif self._device.type == DeviceType.CLIMATE and old_temp is not None:
                self._device.target_temperature = old_temp
            elif self._device.type == DeviceType.SMART_PLUG and old_load is not None:
                self._device.load_power = old_load
            
            if old_is_on != device.is_on:
                self.cb_on.setChecked(device.is_on)
            
            if abs(old_power - device.current_power) > 0.1: 
                self.power_label.setText(f"{device.current_power:.0f} Вт")
        else:
            self._device = device
            self._update_ui_from_model()

    def _on_schedule_clicked(self):
        try:
            from frontend.windows.schedule_editor import ScheduleEditorDialog
            from frontend.api_client import ApiSmartHomeClient
            dialog = ScheduleEditorDialog(self._device.id, self._device.name, parent=self)
            
            if dialog.exec_() == dialog.Accepted:
                client = ApiSmartHomeClient()
                schedules = dialog.get_schedules()
                for day_of_week, schedule_entry in schedules.items():
                    try:
                        client.save_schedule(self._device.id, schedule_entry.to_dict())
                        print(f"Schedule saved for {self._device.name} on day {day_of_week}")
                    except Exception as e:
                        print(f"Error saving schedule: {e}")
        except Exception as e:
            print(f"Error opening schedule editor: {e}")
