from typing import List, Optional, Callable, Any

from PyQt5.QtCore import Qt, QThread, QTimer
import threading
import requests
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QComboBox,
    QMessageBox,
    QScrollArea,
    QListWidget,
    QListWidgetItem,
    QAction,
    QMenu,
    QSplitter,
    QTabWidget,
)
import os
from PyQt5.QtGui import QIcon

from frontend.api_client import ApiSmartHomeClient, ApiError
from frontend.models import DeviceModel, RoomModel, DeviceType
from frontend.windows.device_item_widget import DeviceItemWidget
from frontend.windows.add_room_dialog import AddRoomDialog
from frontend.windows.add_device_dialog import AddDeviceDialog
from frontend.windows.statistics_window_clean import StatisticsWindow
from frontend.windows.weather_widget import WeatherWidget
from frontend.windows.optimization_widget import OptimizationWidget, BudgetWidget
from frontend.api_worker import ApiWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.client = ApiSmartHomeClient()

        self.rooms: List[RoomModel] = []
        self.devices: List[DeviceModel] = []
        self.current_room_id: Optional[str] = None

        self.tile_widgets: List[DeviceItemWidget] = []
        self.active_threads: List[QThread] = []

        self._build_ui()
        QTimer.singleShot(100, self._load_data_initial)
        self._start_connection_timer()
        self._start_tariff_update_timer()

    def closeEvent(self, event):
        for thread in self.active_threads[:]:  
            if thread.isRunning():
                thread.quit()
                thread.wait(1000) 
        self.active_threads.clear()
        event.accept()


    def _build_ui(self):
        self.setWindowTitle("SmartHome Energy Manager")
        self.resize(1200, 700)
        
        central = QWidget()
        central.setObjectName("centralwidget")
        central.setContentsMargins(0, 0, 0, 0)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(12, 0, 12, 10)
        main_layout.setSpacing(6)
        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(8)
        top_widget = QWidget()
        top_widget.setLayout(top)
        top_widget.setObjectName("topPanel")
        top_widget.setContentsMargins(0, 0, 0, 0)

        top_widget.setMaximumHeight(90)
        self.btn_reload = QPushButton("Оновити")
        self.btn_add_room = QPushButton("Додати кімнату")
        self.btn_add_device = QPushButton("Додати пристрій")
        self.btn_optimize = QPushButton("Оптимізувати")
        self.btn_stats = QPushButton("Статистика")
        try:
            from frontend.utils.icon_utils import get_icon
            self.btn_reload.setIcon(get_icon('reload.svg'))
            self.btn_add_room.setIcon(get_icon('room.svg'))
            self.btn_add_device.setIcon(get_icon('device.svg'))
            self.btn_optimize.setIcon(get_icon('plug.svg'))
            self.btn_stats.setIcon(get_icon('stats.svg'))
        except Exception:
            try:
                base = os.path.join(os.path.dirname(__file__), '..', 'resources', 'icons')
                self.btn_reload.setIcon(QIcon(os.path.join(base, 'reload.svg')))
                self.btn_add_room.setIcon(QIcon(os.path.join(base, 'room.svg')))
                self.btn_add_device.setIcon(QIcon(os.path.join(base, 'device.svg')))
                self.btn_optimize.setIcon(QIcon(os.path.join(base, 'plug.svg')))
                self.btn_stats.setIcon(QIcon(os.path.join(base, 'stats.svg')))
            except Exception:
                pass

        top.addWidget(self.btn_reload)
        top.addWidget(self.btn_add_room)
        top.addWidget(self.btn_add_device)
        top.addWidget(self.btn_optimize)
        top.addWidget(self.btn_stats)

        from frontend.theme import apply_theme
        apply_theme('light')

        top.addSpacing(12)
        top.addWidget(QLabel("Тариф:"))

        from frontend.tariff import TariffManager
        self.tariff_manager = TariffManager()
        
        self.btn_tariff_config = QPushButton("⚙️ Налаштувати")
        self.btn_tariff_config.setToolTip("Налаштувати тарифи День/Ніч")
        self.btn_tariff_config.clicked.connect(self._on_tariff_config)
        top.addWidget(self.btn_tariff_config)
        
        self.tariff_label = QLabel("Тариф: 4.32 ₴/кВт (День)")
        self.tariff_label.setObjectName("tariffLabel")
        top.addWidget(self.tariff_label)

        top.addSpacing(12)

        self.total_power_label = QLabel("Загальна потужність: 0 Вт")
        self.total_power_label.setObjectName("totalPower")
        top.addWidget(self.total_power_label)
        
        top.addSpacing(8)
        
        self.cost_label = QLabel("Вартість: 0.00 ₴/год")
        self.cost_label.setObjectName("costLabel")
        self.cost_label.setToolTip("Поточна вартість споживання")
        top.addWidget(self.cost_label)


        self.conn_indicator = QLabel()
        self.conn_indicator.setFixedSize(14, 14)
        self.conn_indicator.setStyleSheet("border-radius:7px; background: gray;")
        top.addWidget(self.conn_indicator)

        self.conn_label = QLabel("")
        self.conn_label.setVisible(False)
        top.addWidget(self.conn_label)

        main_layout.addWidget(top_widget)

        splitter = QSplitter(Qt.Horizontal)

        # Таб-панель (вкладки для всіх компонентів)
        self.tab_widget = QTabWidget()
        self.tab_widget.setMinimumWidth(350)
        self.tab_widget.setMinimumHeight(500)
        
        # ============ ВКЛ 1: Кімнати ============
        tab_rooms = QWidget()
        rooms_layout = QVBoxLayout(tab_rooms)
        rooms_layout.setContentsMargins(8, 8, 8, 8)
        rooms_layout.setSpacing(6)
        
        self.rooms_list = QListWidget()
        self.rooms_list.setObjectName('roomsList')
        self.rooms_list.itemClicked.connect(self._on_room_selected)
        self.rooms_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.rooms_list.customContextMenuRequested.connect(self._on_rooms_context_menu)
        rooms_layout.addWidget(self.rooms_list)
        
        self.tab_widget.addTab(tab_rooms, "🏠 Кімнати")
        
        # ============ ВКЛ 2: Погода ============
        tab_weather = QWidget()
        weather_layout = QVBoxLayout(tab_weather)
        weather_layout.setContentsMargins(8, 8, 8, 8)
        weather_layout.setSpacing(6)
        
        self.weather_widget = WeatherWidget()
        weather_layout.addWidget(self.weather_widget)
        weather_layout.addStretch()
        
        self.tab_widget.addTab(tab_weather, "🌤️ Погода")
        
        # ============ ВКЛ 3: Оптимізація ============
        tab_optimization = QWidget()
        opt_layout = QVBoxLayout(tab_optimization)
        opt_layout.setContentsMargins(8, 8, 8, 8)
        opt_layout.setSpacing(6)
        
        self.optimization_widget = OptimizationWidget()
        opt_layout.addWidget(self.optimization_widget)
        opt_layout.addStretch()
        
        self.tab_widget.addTab(tab_optimization, "💡 Оптимізація")
        
        # ============ ВКЛ 4: Бюджет ============
        tab_budget = QWidget()
        budget_layout = QVBoxLayout(tab_budget)
        budget_layout.setContentsMargins(8, 8, 8, 8)
        budget_layout.setSpacing(6)
        
        from PyQt5.QtCore import QSettings
        settings = QSettings('SmartHome', 'EnergyManager')
        monthly_budget = float(settings.value('monthly_budget', 300.0))
        
        self.budget_widget = BudgetWidget(monthly_budget=monthly_budget)
        budget_layout.addWidget(self.budget_widget)
        budget_layout.addStretch()
        
        self.tab_widget.addTab(tab_budget, "💰 Бюджет")
        
        splitter.addWidget(self.tab_widget)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_widget = QWidget()
        self.devices_layout = QVBoxLayout(self.scroll_widget)
        self.devices_layout.setContentsMargins(10, 10, 10, 10)
        self.devices_layout.setSpacing(8)
        self.devices_layout.addStretch()
        self.scroll.setWidget(self.scroll_widget)

        splitter.addWidget(self.scroll)

        splitter.setSizes([500, 700])
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        main_layout.addWidget(splitter)

        self.setCentralWidget(central)

        self.btn_reload.clicked.connect(self._load_data_initial)
        self.btn_add_room.clicked.connect(self._add_room)
        self.btn_add_device.clicked.connect(self._add_device)
        self.btn_optimize.clicked.connect(self._optimize)
        self.btn_stats.clicked.connect(self._open_stats_window)


    def _run_api_call(
        self, api_call: Callable[[], Any], on_success: Callable[[Any], None]
    ):
        thread = QThread()
        worker = ApiWorker(api_call)
        worker.moveToThread(thread)

        self.active_threads.append(thread)

        def on_finished(result):
            try:
                on_success(result)
            finally:
                thread.quit()
                if thread in self.active_threads:
                    self.active_threads.remove(thread)

        def on_error(error_msg: str):
            try:
                QMessageBox.critical(self, "Помилка", f"Помилка API:\n{error_msg}")
            finally:
                thread.quit()
                if thread in self.active_threads:
                    self.active_threads.remove(thread)

        def cleanup_thread():
            worker.deleteLater()
            if thread in self.active_threads:
                self.active_threads.remove(thread)

        worker.finished.connect(on_finished)
        worker.error.connect(on_error)
        thread.finished.connect(cleanup_thread)

        thread.started.connect(worker.run)
        thread.start()


    def _load_data_initial(self):
        self._run_api_call(
            lambda: self.client.get_rooms(),
            self._on_rooms_loaded,
        )

    def _on_rooms_loaded(self, rooms: List[RoomModel]):
        self.rooms = rooms
        self._fill_rooms_list()

        self._run_api_call(
            lambda: self.client.get_devices(),
            self._on_devices_loaded,
        )

    def _on_devices_loaded(self, devices: List[DeviceModel]):
        self.devices = devices

        room_name_by_device = {}
        for r in self.rooms:
            for d in r.devices:
                room_name_by_device[d.id] = r.name

        for dev in self.devices:
            room_name = room_name_by_device.get(dev.id, dev.room)
            dev.room = room_name

        self._show_devices_for_current_room()
        self._update_total_power_label()

    def _device_power(self, device: DeviceModel) -> float:
        base_power = device.load_power if device.load_power is not None else device.current_power
        return base_power if device.is_on else 0.0

    def _fill_rooms_list(self):
        self.rooms_list.clear()
        for room in self.rooms:
            room_power = sum(
                self._device_power(d)
                for d in self.devices
                if d.room == room.name
            )
            item_text = f"{room.name} ({room_power:.0f} Вт)"
            item = QListWidgetItem(item_text)
            try:
                base = os.path.join(os.path.dirname(__file__), '..', 'resources', 'icons')
                icon_path = os.path.join(base, 'room.svg')
                if os.path.exists(icon_path):
                    item.setIcon(QIcon(icon_path))
            except Exception:
                pass
            item.setData(Qt.UserRole, room.id)
            self.rooms_list.addItem(item)

        if self.rooms and self.current_room_id is None:
            self.rooms_list.setCurrentRow(0)
            if self.rooms_list.currentItem():
                self._on_room_selected(self.rooms_list.currentItem())

    def _fill_rooms_list_silent(self):
        current_item = self.rooms_list.currentItem()
        current_room_id_backup = self.current_room_id
        
        self.rooms_list.clear()
        for room in self.rooms:
            room_power = sum(
                self._device_power(d)
                for d in self.devices
                if d.room == room.name
            )
            item_text = f"{room.name} ({room_power:.0f} Вт)"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, room.id)
            self.rooms_list.addItem(item)
            
            if current_room_id_backup and room.id == current_room_id_backup:
                self.rooms_list.setCurrentItem(item)
        
        if not current_room_id_backup and self.rooms:
            self.rooms_list.setCurrentRow(0)
            if self.rooms_list.currentItem():
                self._on_room_selected(self.rooms_list.currentItem())

    def _show_devices_for_current_room(self):
        self._clear_devices()

        if self.current_room_id is None:
            return

        filtered_devices = [
            d for d in self.devices if d.room == self._get_room_name_by_id(self.current_room_id)
        ]

        for dev in filtered_devices:
            tile = DeviceItemWidget(dev, self._on_device_widget_changed, on_delete=self._on_delete_device)
            self.tile_widgets.append(tile)
            self.devices_layout.insertWidget(self.devices_layout.count() - 1, tile)

        self._update_total_power_label()

    def _on_room_selected(self, item: QListWidgetItem):
        if not item:
            return

        room_id = item.data(Qt.UserRole)
        if room_id == self.current_room_id:
            return

        self.current_room_id = room_id
        self._show_devices_for_current_room()

    def _on_rooms_context_menu(self, pos):
        item = self.rooms_list.itemAt(pos)
        if not item:
            return

        room_id = item.data(Qt.UserRole)
        menu = QMenu(self)
        act_del = QAction("Видалити кімнату", self)
        menu.addAction(act_del)

        def on_delete():
            reply = QMessageBox.question(self, "Підтвердження", "Видалити цю кімнату? Це видалить всі пристрої у ній.", QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self._delete_room(room_id)

        act_del.triggered.connect(on_delete)
        menu.exec_(self.rooms_list.mapToGlobal(pos))

    def _delete_room(self, room_id: str):
        def on_success(resp: dict):
            self.rooms = [r for r in self.rooms if r.id != room_id]
            self.devices = [d for d in self.devices if d.room != self._get_room_name_by_id(room_id)]
            self.current_room_id = None
            self._fill_rooms_list()
            self._show_devices_for_current_room()

        self._run_api_call(lambda: self.client.delete_room(room_id), on_success)

    def _on_delete_device(self, device_id: str):
        def on_success(resp: dict):
            self.devices = [d for d in self.devices if d.id != device_id]
            self._fill_rooms_list_silent()
            self._show_devices_for_current_room()
            self._update_total_power_label()

        self._run_api_call(lambda: self.client.delete_device(device_id), on_success)

    def _get_room_name_by_id(self, room_id: str) -> Optional[str]:
        for room in self.rooms:
            if room.id == room_id:
                return room.name
        return None

    def _update_total_power_label(self):
        total = sum(self._device_power(d) for d in self.devices)
        self.total_power_label.setText(f"Загальна потужність: {total:.0f} Вт")
        self._update_cost_display()

    def _update_cost_display(self):
        total_power = sum(self._device_power(d) for d in self.devices)
        price_per_kwh = self.tariff_manager.get_current_price()
        period = self.tariff_manager.get_current_period()
        
        self.tariff_label.setText(f"Тариф: {price_per_kwh:.2f} ₴/кВт ({period})")
        
        cost_per_hour = (total_power / 1000.0) * price_per_kwh
        
        cost_per_day = cost_per_hour * 24
        
        cost_per_month = cost_per_day * 30
        
        self.cost_label.setText(
            f"💰 {cost_per_hour:.2f} ₴/год | {cost_per_day:.0f} ₴/день | {cost_per_month:.0f} ₴/міс"
        )
        self.cost_label.setToolTip(
            f"Поточне споживання ({period}):\n"
            f"За годину: {cost_per_hour:.2f} ₴\n"
            f"За день: {cost_per_day:.2f} ₴\n"
            f"За місяць: {cost_per_month:.2f} ₴"
        )
        
        # Оновлюємо Optimization widget
        weather = getattr(self.weather_widget, '_weather_data', None) if hasattr(self, 'weather_widget') else None
        time_of_day = self._get_time_of_day()
        
        if hasattr(self, 'optimization_widget'):
            self.optimization_widget.update_data(
                current_power=total_power,
                daily_consumption=cost_per_day / price_per_kwh if price_per_kwh > 0 else 0,
                weather_data=weather,
                time_of_day=time_of_day,
                devices=getattr(self, 'devices', None)
            )
        
        from datetime import datetime
        today = datetime.now()
        if hasattr(self, 'budget_widget'):
            self.budget_widget.update_budget_status(
                today_cost=cost_per_day,
                day_of_month=today.day
            )
        
        if hasattr(self, 'optimization_widget'):
            level = self._calculate_tariff_level()
            self.optimization_widget.set_optimization_level(level)


    def _start_connection_timer(self):
        self._conn_timer = QTimer(self)
        self._conn_timer.timeout.connect(self._perform_connection_check)
        self._conn_timer.start(5000) 
        self._perform_connection_check()


    def _perform_connection_check(self):
        def worker():
            try:
                self.client.get_stats()
                ok = True
            except Exception:
                ok = False

            def update_label():
                if ok:
                    self.conn_indicator.setStyleSheet("border-radius:7px; background: #2ecc71;")
                    self.conn_label.setText("OK")
                else:
                    self.conn_indicator.setStyleSheet("border-radius:7px; background: #e74c3c;")
                    self.conn_label.setText("Відсутнє")

            QTimer.singleShot(0, update_label)

        t = threading.Thread(target=worker, daemon=True)
        t.start()


    def _open_stats_window(self):
        self.stats_window = StatisticsWindow(self, client=self.client)
        self.stats_window.show()


    def _clear_devices(self):
        for w in self.tile_widgets:
            w.setParent(None)
        self.tile_widgets = []

        while self.devices_layout.count() > 1:
            item = self.devices_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


    def _add_room(self):
        dialog = AddRoomDialog(self)
        name = dialog.get_room_name()
        if not name:
            return

        def on_success(room: RoomModel):
            self.rooms.append(room)
            self._fill_rooms_list()
            for i in range(self.rooms_list.count()):
                item = self.rooms_list.item(i)
                if item and item.data(Qt.UserRole) == room.id:
                    self.rooms_list.setCurrentRow(i)
                    self._on_room_selected(item)
                    break

        self._run_api_call(lambda: self.client.add_room(name), on_success)

    def _add_device(self):
        if not self.rooms:
            QMessageBox.warning(
                self,
                "Немає кімнат",
                "Спочатку додайте хоча б одну кімнату.",
            )
            return

        dialog = AddDeviceDialog(self.rooms, self)
        result = dialog.get_result()
        if not result:
            return

        room_id, dev_type, config = result

        def on_success(dev: DeviceModel):
            self.devices.append(dev)
            self._fill_rooms_list()
            self._show_devices_for_current_room()

        self._run_api_call(
            lambda: self.client.add_device(room_id, dev_type, config), on_success
        )

    def _optimize(self):
        tariff = self._calculate_tariff_level()
        
        if hasattr(self, 'optimization_widget'):
            self.optimization_widget.set_optimization_level(tariff)

        def on_success(devices: List[DeviceModel]):
            self.devices = devices

            room_name_by_device = {}
            for r in self.rooms:
                for d in r.devices:
                    room_name_by_device[d.id] = r.name

            for dev in self.devices:
                room_name = room_name_by_device.get(dev.id, dev.room)
                dev.room = room_name

            self._show_devices_for_current_room()
            self._fill_rooms_list() 
            self._update_total_power_label()
            
            level_names = {0: "відключено", 1: "м'яка", 2: "агресивна"}
            print(f"Оптимізація виконана (рівень: {level_names.get(tariff, tariff)})")

        self._run_api_call(lambda: self.client.optimize(tariff), on_success)
    
    def _calculate_tariff_level(self) -> int:
        if not hasattr(self, 'budget_widget'):
            return 1
        
        from datetime import datetime
        day_of_month = datetime.now().day
        monthly_budget = self.budget_widget.monthly_budget
        
        total_power = sum(d.current_power or 0 for d in self.devices)
        price_per_kwh, _ = self.tariff_manager.current_plan.get_current_price()
        cost_per_hour = (total_power / 1000.0) * price_per_kwh
        cost_per_day = cost_per_hour * 24
        
        if day_of_month < 1:
            day_of_month = 1
        projected_monthly = (cost_per_day * 30) / day_of_month
        
        budget_percentage = (projected_monthly / monthly_budget) * 100 if monthly_budget > 0 else 0
        
        if budget_percentage <= 80:
            return 0
        elif budget_percentage <= 100:
            return 1
        else:
            return 2


    def _on_device_widget_changed(self, new_device_state: DeviceModel):
        state = {"is_on": new_device_state.is_on}

        if new_device_state.brightness is not None:
            state["brightness"] = new_device_state.brightness
        if new_device_state.target_temperature is not None:
            state["target_temperature"] = new_device_state.target_temperature
        if new_device_state.load_power is not None:
            state["load_power"] = new_device_state.load_power

        for i, d in enumerate(self.devices):
            if d.id == new_device_state.id:
                merged = {**d.__dict__, **new_device_state.__dict__}
                if merged.get("current_power") is None:
                    merged["current_power"] = d.current_power
                self.devices[i] = DeviceModel(**merged)
                local_updated = self.devices[i]
                break
        else:
            local_updated = None

        if local_updated is not None:
            for tile in self.tile_widgets:
                if tile.device.id == local_updated.id:
                    tile.update_from_device(local_updated, preserve_user_input=True)
                    break

        self._fill_rooms_list_silent()
        self._update_total_power_label()

        def on_success(updated: DeviceModel):
            preserved_values = {}
            for tile in self.tile_widgets:
                if tile.device.id == updated.id:
                    if tile.device.type == DeviceType.LIGHT:
                        if hasattr(tile, 'slider_brightness'):
                            preserved_values['brightness'] = tile.slider_brightness.value()
                    elif tile.device.type == DeviceType.CLIMATE:
                        if hasattr(tile, 'spin_temp'):
                            preserved_values['target_temperature'] = tile.spin_temp.value()
                    elif tile.device.type == DeviceType.SMART_PLUG:
                        if hasattr(tile, 'spin_load'):
                            preserved_values['load_power'] = tile.spin_load.value()
                    break
            
            for i, d in enumerate(self.devices):
                if d.id == updated.id:
                    updated_copy = DeviceModel(**updated.__dict__)
                    if 'brightness' in preserved_values:
                        updated_copy.brightness = preserved_values['brightness']
                    elif updated.brightness is not None:
                        updated_copy.brightness = updated.brightness
                    
                    if 'target_temperature' in preserved_values:
                        updated_copy.target_temperature = preserved_values['target_temperature']
                    elif updated.target_temperature is not None:
                        updated_copy.target_temperature = updated.target_temperature
                    
                    if 'load_power' in preserved_values:
                        updated_copy.load_power = preserved_values['load_power']
                    elif updated.load_power is not None:
                        updated_copy.load_power = updated.load_power
                    
                    self.devices[i] = updated_copy
                    break

            for tile in self.tile_widgets:
                if tile.device.id == updated.id:
                    tile.update_from_device(updated, preserve_user_input=True)
                    break

            self._fill_rooms_list_silent()
            self._update_total_power_label()

        self._run_api_call(
            lambda: self.client.update_device(new_device_state.id, state), on_success
        )

    def _on_tariff_config(self):
        """Відкрити діалог налаштування тарифів."""
        try:
            from frontend.windows.tariff_config_dialog import TariffConfigDialog
            dialog = TariffConfigDialog(self.tariff_manager.current_plan, self)
            if dialog.exec_() == dialog.Accepted:
                plan = dialog.get_selected_plan()
                self.tariff_manager.current_plan = plan
                self._update_cost_display()
        except Exception as e:
            print(f"Error opening tariff config: {e}")

    def _start_tariff_update_timer(self):
        self._tariff_timer = QTimer(self)
        self._tariff_timer.timeout.connect(self._update_tariff_display)
        self._tariff_timer.start(60000)  
        self._update_tariff_display()

    def _update_tariff_display(self):
        self._update_cost_display()
    
    def _get_time_of_day(self) -> str:
        from datetime import datetime
        hour = datetime.now().hour
        
        if 6 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"

