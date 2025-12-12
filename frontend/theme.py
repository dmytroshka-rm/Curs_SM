from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QSettings
import os

def get_light_qss():
    return """
/* Apple-Inspired Theme */
* {
    font-family: -apple-system, 'SF Pro Display', 'Segoe UI', system-ui, sans-serif;
    font-size: 13px;
}

QMainWindow, QWidget#centralwidget {
    background: #f5f5f7;
}

QWidget { 
    background: transparent; 
    color: #1d1d1f;
}

QDialog {
    background: #ffffff;
    color: #1d1d1f;
}

/* Top Panel - Apple Style */
QWidget#topPanel {
    background: rgba(255, 255, 255, 0.95);
    border: none;
    border-bottom: 0.5px solid rgba(0, 0, 0, 0.08);
    padding: 12px 16px;
}

/* Device Cards - Apple Style */
QFrame#deviceCard {
    background: #ffffff;
    border: 0.5px solid rgba(0, 0, 0, 0.04);
    border-radius: 12px;
    padding: 16px;
}
QFrame#deviceCard:hover {
    border: 0.5px solid rgba(0, 0, 0, 0.1);
    background: #fafafa;
}

/* Buttons - Apple Style */
QPushButton {
    background: #ffffff;
    border: 0.5px solid rgba(0, 0, 0, 0.1);
    border-radius: 8px;
    padding: 8px 16px;
    color: #1d1d1f;
    font-weight: 500;
    font-size: 13px;
}
QPushButton:hover { 
    background: #f5f5f7;
    border: 0.5px solid rgba(0, 0, 0, 0.15);
}
QPushButton:pressed { 
    background: #e8e8ed;
}

/* Danger Buttons - Apple Style */
QPushButton#btnDelete {
    background: #ff3b30;
    border: none;
    color: white;
    font-weight: 600;
}
QPushButton#btnDelete:hover {
    background: #ff453a;
}
QPushButton#btnDelete:pressed {
    background: #d70015;
}

/* Schedule Button - Apple Style */
QPushButton#btnSchedule {
    background: #007aff;
    border: none;
    color: white;
    font-weight: 600;
}
QPushButton#btnSchedule:hover {
    background: #0051d5;
}
QPushButton#btnSchedule:pressed {
    background: #004ecb;
}

/* Tariff Button - Apple Style */
QPushButton#btnTariff {
    background: #34c759;
    border: none;
    color: white;
    font-weight: 600;
}
QPushButton#btnTariff:hover {
    background: #30d158;
}
QPushButton#btnTariff:pressed {
    background: #248a3d;
}

/* Input Fields - Apple Style */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background: #ffffff;
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

/* Checkboxes - Apple Style */
QCheckBox {
    color: #1d1d1f;
    font-size: 13px;
    spacing: 6px;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid rgba(0, 0, 0, 0.15);
    border-radius: 4px;
    background: #ffffff;
}
QCheckBox::indicator:hover {
    border: 1px solid rgba(0, 0, 0, 0.25);
}
QCheckBox::indicator:checked {
    background: #007aff;
    border: 1px solid #007aff;
}

/* Sliders - Apple Style */
QSlider::groove:horizontal {
    height: 4px;
    background: rgba(0, 0, 0, 0.1);
    border-radius: 2px;
    margin: 0px;
}
QSlider::handle:horizontal {
    background: #ffffff;
    border: 0.5px solid rgba(0, 0, 0, 0.04);
    width: 20px;
    height: 20px;
    margin: -8px 0;
    border-radius: 10px;
}
QSlider::handle:horizontal:hover {
    background: #f5f5f7;
}

/* Lists - Apple Style */
QListWidget {
    background: transparent;
    border: none;
    font-size: 13px;
}
QListWidget::item { 
    padding: 8px 12px; 
    border-radius: 6px;
    margin: 1px 0;
}
QListWidget::item:selected { 
    background: #007aff;
    color: white;
    font-weight: 500;
}
QListWidget::item:hover:!selected { 
    background: rgba(0, 0, 0, 0.04);
}

QScrollArea { background: transparent; }

/* Tooltips */
QToolTip { 
    background: #1f2937; 
    color: #f3f4f6; 
    border: none; 
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 12px;
}

/* Scrollbars - Apple Style */
QScrollBar:vertical { 
    background: transparent; 
    width: 8px; 
    margin: 0px; 
}
QScrollBar::handle:vertical { 
    background: rgba(0, 0, 0, 0.2); 
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover { 
    background: rgba(0, 0, 0, 0.3); 
}
QScrollBar::add-line, QScrollBar::sub-line { 
    height: 0px; 
}

/* Labels - Professional Typography */
QLabel#totalPower { 
    font-weight: 700; 
    font-size: 14px;
    color: #0f172a;
}
QLabel#costLabel {
    font-weight: 700;
    font-size: 13px;
    color: #059669;
}
QLabel#tariffLabel {
    font-weight: 500;
    font-size: 12px;
    color: #6b7280;
}
QLabel#deviceName {
    font-size: 14px;
    font-weight: 600;
    color: #1f2937;
}
QLabel#roomName {
    font-size: 11px;
    color: #9ca3af;
}
QLabel#powerLabel {
    font-size: 16px;
    font-weight: 700;
    color: #3b82f6;
}

/* Device Icons/Thumbnails */
QLabel#thumbnail {
    background: #f0fdf4;
    border-radius: 10px;
    padding: 4px;
}

/* Tab Widget - Apple Style */
QTabWidget::pane {
    border: none;
    background: transparent;
}
QTabBar {
    background: transparent;
}
QTabBar::tab {
    background: transparent;
    color: #86868b;
    border: none;
    padding: 8px 16px;
    margin-right: 0px;
    font-weight: 500;
    font-size: 13px;
}
QTabBar::tab:hover:!selected {
    color: #515154;
}
QTabBar::tab:selected {
    color: #007aff;
    font-weight: 600;
}
    color: #374151;
    background: #f9fafb;
}
QTabBar::tab:selected {
    color: #0f172a;
    border-bottom: 2px solid #3b82f6;
    background: transparent;
}

/* Left Navigation */
QWidget#leftNav { background: transparent; }
QListWidget#roomsList { background: transparent; border: none; }
"""

def get_dark_qss():
    return """
/* Professional Dark Theme */
* {
    font-family: 'Segoe UI', 'Helvetica Neue', sans-serif;
}

QMainWindow, QWidget#centralwidget {
    background: #0f172a;
}

QWidget { 
    background: transparent; 
    color: #e2e8f0;
}

QDialog {
    background: #1a202c;
    color: #e2e8f0;
}

/* Top Panel - Elegant Header */
QWidget#topPanel {
    background: #1a202c;
    border-bottom: 1px solid #2d3748;
    border-radius: 0px;
    padding: 12px 16px;
}

/* Device Cards - Modern Dark */
QFrame#deviceCard {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 14px;
}
QFrame#deviceCard:hover {
    border: 1px solid #475569;
    background: #253549;
}

/* Buttons - Dark Professional */
QPushButton {
    background: #2d3748;
    border: 1px solid #4a5568;
    border-radius: 8px;
    padding: 9px 16px;
    color: #cbd5e1;
    font-weight: 500;
    font-size: 13px;
}
QPushButton:hover { 
    background: #374151;
    border: 1px solid #64748b;
    color: #e2e8f0;
}
QPushButton:pressed { 
    background: #1f2937;
    border: 1px solid #475569;
}

/* Danger Buttons */
QPushButton#btnDelete {
    background: #7f1d1d;
    border: 1px solid #991b1b;
    color: #fecaca;
}
QPushButton#btnDelete:hover {
    background: #991b1b;
    border: 1px solid #dc2626;
    color: #fee2e2;
}

/* Schedule Button */
QPushButton#btnSchedule {
    background: #1e3a8a;
    border: 1px solid #3b82f6;
    color: #bfdbfe;
    font-weight: 600;
}
QPushButton#btnSchedule:hover {
    background: #1e40af;
    border: 1px solid #60a5fa;
    color: #dbeafe;
}

/* Tariff Button */
QPushButton#btnTariff {
    background: #15803d;
    border: 1px solid #22c55e;
    color: #bbf7d0;
    font-weight: 600;
}
QPushButton#btnTariff:hover {
    background: #16a34a;
    border: 1px solid #4ade80;
    color: #dcfce7;
}

/* Input Fields - Dark Professional */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background: #1a202c;
    color: #e2e8f0;
    border: 1px solid #4a5568;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
    border: 2px solid #3b82f6;
    background: #1a202c;
}

/* Checkboxes - Dark */
QCheckBox {
    color: #cbd5e1;
    font-size: 13px;
    spacing: 8px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #4a5568;
    border-radius: 3px;
    background: #2d3748;
}
QCheckBox::indicator:hover {
    border: 1px solid #64748b;
}
QCheckBox::indicator:checked {
    background: #3b82f6;
    border: 1px solid #3b82f6;
}

/* Sliders - Dark Professional */
QSlider::groove:horizontal {
    height: 6px;
    background: #2d3748;
    border-radius: 3px;
    margin: 0px;
}
QSlider::handle:horizontal {
    background: #3b82f6;
    border: none;
    width: 16px;
    height: 16px;
    margin: -5px 0;
    border-radius: 8px;
}
QSlider::handle:horizontal:hover {
    background: #60a5fa;
}

/* Lists - Dark Clean */
QListWidget { 
    background: transparent; 
    border: none; 
    font-size: 13px;
}
QListWidget::item { 
    padding: 10px 12px; 
    border-radius: 8px;
    margin: 2px 0;
}
QListWidget::item:selected {
    background: rgba(59, 130, 246, 0.15);
    color: #dbeafe;
    font-weight: 500;
    border-left: 3px solid #3b82f6;
    padding-left: 9px;
}
QListWidget::item:hover { 
    background: rgba(255, 255, 255, 0.05);
}

QScrollArea { background: transparent; }

/* Tooltips - Dark */
QToolTip { 
    background: #374151; 
    color: #f3f4f6; 
    border: 1px solid #4b5563;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 12px;
}

/* Scrollbars - Dark Refined */
QScrollBar:vertical { background: transparent; width: 10px; margin: 0px; }
QScrollBar::handle:vertical { 
    background: #4a5568; 
    border-radius: 5px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover { background: #64748b; }
QScrollBar::add-line, QScrollBar::sub-line { height: 0px; }

/* Labels - Dark Typography */
QLabel#totalPower { 
    font-weight: 700; 
    font-size: 14px;
    color: #f1f5f9;
}
QLabel#costLabel {
    font-weight: 700;
    font-size: 13px;
    color: #4ade80;
}
QLabel#tariffLabel {
    font-weight: 500;
    font-size: 12px;
    color: #94a3b8;
}
QLabel#deviceName {
    font-size: 14px;
    font-weight: 600;
    color: #e2e8f0;
}
QLabel#roomName {
    font-size: 11px;
    color: #64748b;
}
QLabel#powerLabel {
    font-size: 16px;
    font-weight: 700;
    color: #60a5fa;
}

/* Device Icons/Thumbnails - Dark */
QLabel#thumbnail {
    background: rgba(34, 197, 94, 0.1);
    border-radius: 10px;
    padding: 4px;
}

/* Tab Widget - Dark Professional Tabs */
QTabWidget::pane {
    border: none;
    background: transparent;
}
QTabBar {
    background: transparent;
    border-bottom: 1px solid #2d3748;
}
QTabBar::tab {
    background: transparent;
    color: #94a3b8;
    border: none;
    padding: 10px 12px;
    margin: 0px;
    font-weight: 500;
    font-size: 13px;
    border-bottom: 2px solid transparent;
}
QTabBar::tab:hover {
    color: #cbd5e1;
    background: rgba(255, 255, 255, 0.05);
}
QTabBar::tab:selected {
    color: #f1f5f9;
    border-bottom: 2px solid #3b82f6;
    background: transparent;
}

/* Left Navigation - Dark */
QWidget#leftNav { background: transparent; }
QListWidget#roomsList { background: transparent; border: none; }
"""


def apply_theme(name: str):
    app = QApplication.instance()
    if not app:
        return
    if name == 'dark':
        app.setStyleSheet(get_dark_qss())
    else:
        app.setStyleSheet(get_light_qss())
    settings = QSettings('SmartHome', 'EnergyManager')
    settings.setValue('theme', name)


def current_theme():
    settings = QSettings('SmartHome', 'EnergyManager')
    val = settings.value('theme', 'light')
    return val if val in ('light', 'dark') else 'light'
