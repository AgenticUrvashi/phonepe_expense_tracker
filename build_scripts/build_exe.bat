@echo off
title PhonePe Expense Tracker - Executable Builder
echo ===================================================
echo   Building PhonePe Expense Tracker Standalone .exe
echo ===================================================

if exist .venv312\Scripts\pyinstaller.exe (
    set PYINSTALLER=.venv312\Scripts\pyinstaller.exe
) else (
    set PYINSTALLER=pyinstaller
)

echo Bundling Desktop Application with assets into a single .exe...
%PYINSTALLER% --noconfirm --onefile --windowed ^
    --icon "backend/static/assets/app.ico" ^
    --add-data "backend/static;backend/static" ^
    --add-data "data;data" ^
    --name "PhonePe_Expense_Tracker" ^
    backend/app.py

echo.
echo ===================================================
echo   Build Complete! Single executable saved in: dist/PhonePe_Expense_Tracker.exe
echo ===================================================
pause
