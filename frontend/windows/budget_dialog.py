from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QDoubleSpinBox, QPushButton
from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QFont


class BudgetDialog(QDialog):

    
    def __init__(self, current_budget: float = 300.0, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Налаштування бюджету")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        self.setStyleSheet("""
            QDialog {
                background: #ffffff;
                color: #1d1d1f;
            }
            QLabel {
                color: #1d1d1f;
                font-size: 13px;
            }
            QDoubleSpinBox {
                background: #f5f5f7;
                color: #1d1d1f;
                border: 0.5px solid rgba(0, 0, 0, 0.1);
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
            }
            QDoubleSpinBox:focus {
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
        """)
        
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("💰 Встановлення місячного бюджету")
        title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(title)
        
        # Info
        info = QLabel("Вкажіть максимальну суму, яку Ви готові витратити на енергію за місяць:")
        info.setFont(QFont("Segoe UI", 10))
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Input field
        input_layout = QHBoxLayout()
        
        label = QLabel("Бюджет (₴):")
        label.setFont(QFont("Segoe UI", 11))
        input_layout.addWidget(label)
        
        self.spin_budget = QDoubleSpinBox()
        self.spin_budget.setMinimum(10.0)
        self.spin_budget.setMaximum(10000.0)
        self.spin_budget.setValue(current_budget)
        self.spin_budget.setDecimals(0)
        self.spin_budget.setStyleSheet("""
            QDoubleSpinBox {
                font-size: 12px;
                padding: 8px;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
            }
        """)
        input_layout.addWidget(self.spin_budget)
        
        layout.addLayout(input_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        btn_cancel = QPushButton("Скасувати")
        btn_cancel.clicked.connect(self.reject)
        button_layout.addWidget(btn_cancel)
        
        btn_ok = QPushButton("Зберегти")
        btn_ok.setStyleSheet("background-color: #3b82f6; color: white; padding: 8px; border-radius: 6px;")
        btn_ok.clicked.connect(self.accept)
        button_layout.addWidget(btn_ok)
        
        layout.addLayout(button_layout)
    
    def get_budget(self) -> float:
        """Get the budget value entered by user."""
        return self.spin_budget.value()
    
    @staticmethod
    def get_budget_from_user(current_budget: float = 300.0, parent=None) -> float:
        """Show dialog and return budget if accepted, else return current budget."""
        dialog = BudgetDialog(current_budget, parent)
        if dialog.exec_() == QDialog.Accepted:
            budget = dialog.get_budget()
            # Save to settings
            settings = QSettings('SmartHome', 'EnergyManager')
            settings.setValue('monthly_budget', budget)
            return budget
        return current_budget
