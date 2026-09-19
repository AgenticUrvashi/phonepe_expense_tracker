@echo off
title PhonePe Expense Tracker Launcher
echo ===================================================
echo   PhonePe Expense Tracker - Desktop Application
echo ===================================================
echo Starting Application...

if exist .venv312\Scripts\python.exe (
    .venv312\Scripts\python.exe main.py
) else if exist .venv\Scripts\python.exe (
    .venv\Scripts\python.exe main.py
) else (
    python main.py
)

pause
