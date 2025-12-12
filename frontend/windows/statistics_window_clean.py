from typing import Any, Dict, Optional
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QMessageBox, QHBoxLayout, QToolTip
)
from PyQt5.QtCore import QTimer, Qt, QThread
from PyQt5.QtGui import QCursor
import threading
import json

from frontend.api_client import ApiSmartHomeClient
from frontend.api_worker import ApiWorker

try:
    import pyqtgraph as pg
    from pyqtgraph import PlotWidget
    HAS_PYQTGRAPH = True
except Exception:
    HAS_PYQTGRAPH = False


class StatisticsWindow(QWidget):
    def __init__(self, parent=None, client: Optional[ApiSmartHomeClient] = None):
        super().__init__(parent)
        self.setWindowFlags(self.windowFlags() | Qt.Window)
        self.setWindowTitle("📈 Статистика")
        self.resize(800, 600)
        
        self.setStyleSheet("""
            StatisticsWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f0f9ff, stop:0.5 #e0f2fe, stop:1 #f0f9ff);
            }
        """)

        self.client = client or ApiSmartHomeClient()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        

        self.info_label = QLabel("⏳ Завантаження статистики...")
        self.info_label.setStyleSheet("""
            QLabel {
                background: rgba(255, 255, 255, 200);
                border: 1px solid rgba(226, 232, 240, 0.5);
                border-radius: 12px;
                padding: 16px 20px;
                color: #1e293b;
                font-size: 14px;
                font-weight: 600;
            }
        """)
        layout.addWidget(self.info_label)

        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.text.setStyleSheet("""
            QTextEdit {
                background: rgba(255, 255, 255, 220);
                border: 1px solid rgba(203, 213, 225, 0.4);
                border-radius: 12px;
                color: #1e293b;
                font-family: 'Segoe UI', 'SF Pro Display', sans-serif;
                font-size: 11pt;
                padding: 16px;
                line-height: 1.6;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 8px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: rgba(148, 163, 184, 0.4);
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(100, 116, 139, 0.6);
            }
        """)
        layout.addWidget(self.text)

        # Вкладки для різних періодів графіку
        from PyQt5.QtWidgets import QTabWidget
        self.chart_tabs = QTabWidget()
        self.chart_tabs.setStyleSheet("""
            QTabWidget::pane {
                background: rgba(255, 255, 255, 220);
                border: 1px solid rgba(203, 213, 225, 0.4);
                border-radius: 12px;
                padding: 8px;
            }
            QTabBar::tab {
                background: rgba(241, 245, 249, 150);
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                margin-right: 4px;
                color: #64748b;
                font-weight: 500;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3b82f6, stop:1 #2563eb);
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background: rgba(226, 232, 240, 200);
                color: #475569;
            }
        """)
        
        # Вкладка 1 година
        self.plot_widget_1h = None
        if HAS_PYQTGRAPH:
            try:
                self.plot_widget_1h = PlotWidget()
                self.plot_widget_1h.setBackground('w')
                self.plot_widget_1h.setLabel('left', 'Power', units='W')
                self.plot_widget_1h.setLabel('bottom', 'Time')
                self.chart_tabs.addTab(self.plot_widget_1h, "1 година")
            except Exception:
                self.plot_widget_1h = None

        # Вкладка 24 години
        self.plot_widget_24h = None
        if HAS_PYQTGRAPH:
            try:
                self.plot_widget_24h = PlotWidget()
                self.plot_widget_24h.setBackground('w')
                self.plot_widget_24h.setLabel('left', 'Power', units='W')
                self.plot_widget_24h.setLabel('bottom', 'Hours')
                self.chart_tabs.addTab(self.plot_widget_24h, "24 години")
            except Exception:
                self.plot_widget_24h = None

        # Вкладка 7 днів
        self.plot_widget_7d = None
        if HAS_PYQTGRAPH:
            try:
                self.plot_widget_7d = PlotWidget()
                self.plot_widget_7d.setBackground('w')
                self.plot_widget_7d.setLabel('left', 'Power', units='W')
                self.plot_widget_7d.setLabel('bottom', 'Days')
                self.chart_tabs.addTab(self.plot_widget_7d, "7 днів")
            except Exception:
                self.plot_widget_7d = None

        if self.plot_widget_1h or self.plot_widget_24h or self.plot_widget_7d:
            layout.addWidget(self.chart_tabs)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        
        self.btn_refresh = QPushButton("🔄 Оновити")
        self.btn_refresh.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3b82f6, stop:1 #2563eb);
                border: none;
                border-radius: 10px;
                padding: 12px 24px;
                color: white;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2563eb, stop:1 #1d4ed8);
                transform: translateY(-2px);
            }
            QPushButton:pressed {
                background: #1e40af;
            }
        """)
        self.btn_refresh.clicked.connect(self._load_stats)
        btn_row.addWidget(self.btn_refresh)

        self.btn_csv = QPushButton("📊 Експорт CSV")
        self.btn_csv.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #10b981, stop:1 #059669);
                border: none;
                border-radius: 10px;
                padding: 12px 24px;
                color: white;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #059669, stop:1 #047857);
            }
            QPushButton:pressed {
                background: #065f46;
            }
        """)
        self.btn_csv.clicked.connect(self.export_csv)
        btn_row.addWidget(self.btn_csv)
        
        btn_row.addStretch()

        self.btn_close = QPushButton("✕ Закрити")
        self.btn_close.setStyleSheet("""
            QPushButton {
                background: rgba(239, 68, 68, 0.1);
                border: 2px solid #ef4444;
                border-radius: 10px;
                padding: 12px 24px;
                color: #ef4444;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #ef4444;
                color: white;
            }
            QPushButton:pressed {
                background: #dc2626;
            }
        """)
        self.btn_close.clicked.connect(self.close)
        btn_row.addWidget(self.btn_close)

        layout.addLayout(btn_row)

        self._worker_threads = []
        self._load_stats()

    def _load_stats(self):
        self.info_label.setText("Loading statistics...")

        thread = QThread()
        worker = ApiWorker(lambda: self.client.get_stats())
        worker.moveToThread(thread)

        def on_finished(result):
            try:
                self._on_stats_loaded(result)
            finally:
                thread.quit()
                worker.deleteLater()
                if thread in self._worker_threads:
                    self._worker_threads.remove(thread)

        def on_error(msg: str):
            try:
                QMessageBox.critical(self, "Error", f"Failed to load stats: {msg}")
                self.info_label.setText("Failed to load statistics")
            finally:
                thread.quit()
                worker.deleteLater()
                if thread in self._worker_threads:
                    self._worker_threads.remove(thread)

        worker.finished.connect(on_finished)
        worker.error.connect(on_error)
        thread.started.connect(worker.run)
        thread.start()
        self._worker_threads.append(thread)

    def _on_stats_loaded(self, data: Dict[str, Any]):
        try:
            self._stats_data = data
            
            total = data.get("total_power", 0)
            forecast = data.get("forecast_next_total", 0)
            self.info_label.setText(f"Загальна потужність: {total:.0f} Вт | Прогноз: {forecast:.0f} Вт")
            
            text_parts = []
            text_parts.append(f"📊 Загальна потужність: {total:.0f} Вт")
            text_parts.append(f"🔮 Прогноз наступної оптимізації: {forecast:.0f} Вт")
            text_parts.append("")
            
            self._load_chart_data("1hour", self.plot_widget_1h if self.plot_widget_1h else None)
            self._load_chart_data("24hours", self.plot_widget_24h if self.plot_widget_24h else None)
            self._load_chart_data("7days", self.plot_widget_7d if self.plot_widget_7d else None)
            
            rooms = data.get("rooms", [])
            if rooms:
                text_parts.append("🏠 Кімнати:")
                text_parts.append("-" * 60)
                for room in rooms:
                    room_name = room.get("name", "")
                    room_power = room.get("total_power", 0)
                    rating = room.get("rating", "")
                    text_parts.append(f"  • {room_name}: {room_power:.0f} Вт (Рейтинг: {rating})")
                    
                    devices = room.get("devices", [])
                    if devices:
                        for dev in devices:
                            dev_name = dev.get("name", "")
                            dev_power = dev.get("current_power", 0)
                            dev_on = "✓" if dev.get("is_on") else "✗"
                            text_parts.append(f"    {dev_on} {dev_name}: {dev_power:.1f} Вт")
                    text_parts.append("")
            
            self.text.setPlainText("\n".join(text_parts))
        except Exception as ex:
            QMessageBox.critical(self, "Error", f"Invalid stats data: {ex}")



    def export_csv(self):
        if not hasattr(self, '_stats_data') or not self._stats_data:
            QMessageBox.warning(self, "Export CSV", "No statistics data available")
            return
            
        try:
            data = self._stats_data
            rows = [["Key", "Value"]]
            
            # Основна інформація
            rows.append(["Total Power (W)", data.get("total_power", 0)])
            rows.append(["Forecast Next Total (W)", data.get("forecast_next_total", 0)])
            
            # Кімнати
            rooms = data.get("rooms", [])
            for room in rooms:
                room_name = room.get("name", "")
                room_power = room.get("total_power", 0)
                rating = room.get("rating", "")
                rows.append([f"Room: {room_name}", f"{room_power} W (Rating: {rating})"])
                
                # Пристрої в кімнаті
                devices = room.get("devices", [])
                for dev in devices:
                    dev_name = dev.get("name", "")
                    dev_power = dev.get("current_power", 0)
                    dev_on = "On" if dev.get("is_on") else "Off"
                    rows.append([f"  Device: {dev_name}", f"{dev_power} W ({dev_on})"])

            with open('statistics_export.csv', 'w', encoding='utf-8', newline='') as f:
                import csv
                writer = csv.writer(f)
                writer.writerows(rows)

            QMessageBox.information(self, "Export", "Statistics exported to statistics_export.csv")
        except Exception as ex:
            QMessageBox.critical(self, "Export CSV", f"Failed to export CSV: {ex}")

    def _load_chart_data(self, period: str, plot_widget):

        if not plot_widget or not HAS_PYQTGRAPH:
            return

        try:
            data = self.client.get_chart_history(period)
            chart_data = data.get("data", [])
            
            if not chart_data:
                return

            powers = [entry.get("power", 0) for entry in chart_data]
            
            if not powers:
                return


            plot_widget.clear()
            curve = plot_widget.plot(powers, pen=pg.mkPen(color=(59, 130, 246), width=2), name="Power (W)")
           
            plot_widget.showGrid(x=True, y=True, alpha=0.3)
            
            try:
                ymin = min(powers)
                ymax = max(powers)
                padding = (ymax - ymin) * 0.1 if ymax != ymin else max(1.0, abs(ymax) * 0.1)
                plot_widget.setYRange(ymin - padding, ymax + padding)
            except Exception:
                pass

        except Exception as ex:
            pass 

    def _on_plot_mouse_move(self, evt):
        try:
            if not hasattr(self, '_plot_values') or not self._plot_values:
                return
            vb = self.plot_widget.getPlotItem().vb
            mousePoint = vb.mapSceneToView(evt)
            x = mousePoint.x()
            idx = int(round(x))
            if idx < 0:
                idx = 0
            if idx >= len(self._plot_values):
                idx = len(self._plot_values) - 1
            val = self._plot_values[idx]
            QToolTip.showText(QCursor.pos(), f"#{idx}: {val:.2f} W", widget=self.plot_widget)
        except Exception:
            pass


def json_pretty(obj: Dict[str, Any]) -> str:
    try:
        return json.dumps(obj, indent=2, ensure_ascii=False)
    except Exception:
        return str(obj)


def render_sparkline(values: list) -> str:
    if not values:
        return ""
    blocks = "▁▂▃▄▅▆▇█"
    mn = min(values)
    mx = max(values)
    if mx == mn:
        return blocks[-1] * len(values)

    out = []
    for v in values:
        t = (v - mn) / (mx - mn)
        idx = int(t * (len(blocks) - 1))
        out.append(blocks[idx])
    return "".join(out)


    


