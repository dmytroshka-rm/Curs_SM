from typing import Optional

from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
)


class AddRoomDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Додати кімнату")
        self.setModal(True)
        
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
            QLineEdit {
                background: #f5f5f7;
                color: #1d1d1f;
                border: 0.5px solid rgba(0, 0, 0, 0.1);
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
            }
            QLineEdit:focus {
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

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Назва кімнати (наприклад, Вітальня)")

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Назва кімнати:"))
        layout.addWidget(self.name_edit)

        btn_row = QHBoxLayout()
        btn_ok = QPushButton("OK")
        btn_cancel = QPushButton("Скасувати")

        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)

        btn_row.addStretch()
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_ok)

        layout.addLayout(btn_row)

    def get_room_name(self) -> Optional[str]:
        if self.exec_() == QDialog.Accepted:
            name = self.name_edit.text().strip()
            return name or None
        return None
