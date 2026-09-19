@echo off
title PhonePe Expense Tracker Launcher
echo ===================================================
echo   PhonePe Expense Tracker - Desktop Application
echo ===================================================
echo Starting Application...

if exist .venv312\Scripts\python.exe (
    .venv312\Scripts\python.exe backend\app.py
) else if exist .venv\Scripts\python.exe (
    .venv\Scripts\python.exe backend\app.py
) else (
    python backend\app.py
)

pause
