@echo off
echo ============================================
echo        Запуск SmartHome System
echo ============================================

REM --- Запуск backend ---
echo [1] Запуск backend (C++)...
start "Backend" cmd /k "cd /d %~dp0backend\build\Release && smart_home_server.exe"

timeout /t 2 >nul

REM --- Запуск frontend ---
echo [2] Запуск frontend (Python PyQt5)...
start "Frontend" cmd /k "cd /d %~dp0 && python -m frontend.main"

echo ============================================
echo           Все запущено
echo ============================================
exit
