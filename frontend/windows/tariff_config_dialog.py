from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QDoubleSpinBox,
    QPushButton, QGroupBox
)
from PyQt5.QtCore import Qt
from frontend.tariff import DayNightTariff


class TariffConfigDialog(QDialog):
    
    def __init__(self, current_plan: DayNightTariff, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Налаштування тарифів")
        self.setModal(True)
        self.resize(500, 400)
        
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
            QGroupBox {
                background: #f5f5f7;
                border: 0.5px solid rgba(0, 0, 0, 0.1);
                border-radius: 8px;
                padding: 16px;
                margin-top: 10px;
                font-weight: 600;
                color: #1d1d1f;
            }
            QGroupBox::title {
                color: #1d1d1f;
            }
            QSpinBox, QDoubleSpinBox {
                background: #ffffff;
                color: #1d1d1f;
                border: 0.5px solid rgba(0, 0, 0, 0.1);
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
            }
            QSpinBox:focus, QDoubleSpinBox:focus {
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
            }
        """)
        
        self.current_plan = current_plan
        self.selected_plan = None

        layout = QVBoxLayout(self)

        form_group = QGroupBox("Користувацький тариф")
        form_layout = QVBoxLayout(form_group)

        day_row = QHBoxLayout()
        day_row.addWidget(QLabel("Денний тариф (₴/кВт·год):"))
        self.day_price_spin = QDoubleSpinBox()
        self.day_price_spin.setRange(0.1, 50.0)
        self.day_price_spin.setValue(current_plan.day_price)
        self.day_price_spin.setDecimals(2)
        self.day_price_spin.setSingleStep(0.1)
        day_row.addWidget(self.day_price_spin)
        day_row.addStretch()
        form_layout.addLayout(day_row)

        night_row = QHBoxLayout()
        night_row.addWidget(QLabel("Нічний тариф (₴/кВт·год):"))
        self.night_price_spin = QDoubleSpinBox()
        self.night_price_spin.setRange(0.1, 50.0)
        self.night_price_spin.setValue(current_plan.night_price)
        self.night_price_spin.setDecimals(2)
        self.night_price_spin.setSingleStep(0.1)
        night_row.addWidget(self.night_price_spin)
        night_row.addStretch()
        form_layout.addLayout(night_row)

        day_start_row = QHBoxLayout()
        day_start_row.addWidget(QLabel("День починається о:"))
        self.day_start_spin = QSpinBox()
        self.day_start_spin.setRange(0, 23)
        self.day_start_spin.setValue(current_plan.day_start)
        day_start_row.addWidget(self.day_start_spin)
        day_start_row.addStretch()
        form_layout.addLayout(day_start_row)

        day_end_row = QHBoxLayout()
        day_end_row.addWidget(QLabel("День закінчується о:"))
        self.day_end_spin = QSpinBox()
        self.day_end_spin.setRange(0, 23)
        self.day_end_spin.setValue(current_plan.day_end)
        day_end_row.addWidget(self.day_end_spin)
        day_end_row.addStretch()
        form_layout.addLayout(day_end_row)

        form_layout.addStretch()

        layout.addWidget(form_group)
        
        btn_layout = QHBoxLayout()
        
        btn_save = QPushButton("Зберегти")
        btn_save.clicked.connect(self.accept)
        btn_layout.addWidget(btn_save)
        
        btn_cancel = QPushButton("Скасувати")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        
        layout.addLayout(btn_layout)
    
    def get_selected_plan(self) -> DayNightTariff:
        return DayNightTariff(
            name="Користувацький",
            day_price=self.day_price_spin.value(),
            night_price=self.night_price_spin.value(),
            day_start=self.day_start_spin.value(),
            day_end=self.day_end_spin.value(),
        )
