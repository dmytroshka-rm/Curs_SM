# Smart Home Energy Management System

Інтелектуальна система для керування пристроями, моніторингу споживання та рекомендацій з економії енергії у розумному домі.

## Встановлення

### 1. Клонування репозиторію:
```bash
git clone https://github.com/dmytroshka-rm/Curs.git
cd Curs
```

### 2. Збірка backend (C++):
```bash
cd backend
mkdir build
cd build
cmake ..
cmake --build . --config Release
```

### 3. Запуск frontend (Python):
```bash
cd frontend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Архітектура 
- Backend: C++17, Crow, ASIO. REST ендпоінти для пристроїв, розкладів, статистики, оптимізації.
- Frontend: Python 3.9+, PyQt5. Головне вікно з вкладками (кімнати, погода, оптимізація, бюджет, статистика).
- Зв’язок: HTTP/JSON між фронтом і бекендом.

## Структура проекту
```
Curs/
├── README.md
├── run_all.bat
├── smarthome.log
│
├── backend/
│   ├── main.cpp                      # REST API сервер (Crow)
│   ├── CMakeLists.txt
│   │
│   ├── include/                      # Заголовкові файли
│   │   ├── smart_home.h
│   │   ├── devices.h
│   │   ├── schedule.h
│   │   ├── strategy.h
│   │   ├── consumption_history.h
│   │   ├── logger.h
│   │   └── nlohmann/
│   │       └── json.hpp
│   │
│   ├── src/                          # Реалізація
│   │   ├── smart_home.cpp
│   │   ├── devices.cpp
│   │   ├── schedule.cpp
│   │   ├── strategy.cpp
│   │   ├── consumption_history.cpp
│   │   └── logger.cpp
│   │
│   ├── build/                        # Директорія збірки
│   │   └── Release/
│   │       └── smart_home_server.exe
│   │
│   ├── asio/                         # Бібліотека ASIO
│   └── crow/                         # Бібліотека Crow
│
└── frontend/
    ├── __init__.py
    ├── main.py                       # Точка входу
    ├── requirements.txt
    │
    ├── api_client.py                 # HTTP клієнт для backend
    ├── api_worker.py                 # Асинхронні запити
    ├── models.py                     # Моделі даних
    ├── optimization.py               # Логіка оптимізації та рекомендацій
    ├── weather.py                    # Клієнт Open-Meteo API
    ├── tariff.py                     # Тарифні плани (День/Ніч)
    ├── theme.py                      # Light/Dark теми
    ├── resources.qrc                 # Qt ресурси
    ├── build_frontend.ps1
    │
    ├── windows/                      # UI компоненти (PyQt5)
    │   ├── main_window.py            # Головне вікно з вкладками
    │   ├── add_room_dialog.py
    │   ├── add_device_dialog.py
    │   ├── device_item_widget.py
    │   ├── schedule_editor.py
    │   ├── budget_dialog.py
    │   ├── tariff_config_dialog.py
    │   ├── optimization_widget.py
    │   ├── weather_widget.py
    │   └── statistics_window_clean.py
    │
    ├── utils/                        # Утиліти
    │   └── icon_utils.py
    │
    └── resources/                    # Ресурси
        └── icons/
            ├── app.ico
            ├── app.svg
            ├── home.svg
            ├── room.svg
            ├── device.svg
            ├── light.svg
            ├── plug.svg
            ├── climate.svg
            ├── stats.svg
            ├── reload.svg
            └── close.svg
```

## Встановлення
```bash
pip install -r frontend/requirements.txt
```

## Запуск
```powershell
# Backend
cd backend\build\Release
./smart_home_server.exe

# Frontend
cd ..\..
python -m frontend.main
```

## Ключові файли
- `backend/main.cpp` — REST сервер та маршрути
- `backend/src/smart_home.cpp` — логіка кімнат, пристроїв, оптимізації
- `frontend/main.py` — точка входу UI
- `frontend/windows/main_window.py` — головне вікно
- `frontend/optimization.py` — рекомендації та оцінка споживання
- `frontend/weather.py` — клієнт Open-Meteo

---

