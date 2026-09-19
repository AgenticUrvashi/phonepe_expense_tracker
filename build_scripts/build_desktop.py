"""PhonePe Expense Tracker - Desktop Launcher & Builder Script.

Usage:
  python build_scripts/build_desktop.py          # Launches the desktop application
  python build_scripts/build_desktop.py --build  # Packages into standalone .exe with PyInstaller
"""

import os
import sys
import subprocess
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Ensure UTF-8 output on Windows consoles
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


def build_executable():
    """Builds a standalone .exe with PyInstaller."""
    print("===================================================")
    print("  Building PhonePe Expense Tracker Executable (.exe)")
    print("===================================================")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--icon", str(PROJECT_ROOT / "backend/static/assets/app.ico"),
        "--add-data", f"{PROJECT_ROOT / 'backend/static'};backend/static",
        "--add-data", f"{PROJECT_ROOT / 'data'};data",
        "--name", "PhonePe_Expense_Tracker",
        str(PROJECT_ROOT / "backend/app.py")
    ]
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
    if result.returncode == 0:
        print("\n✅ Build succeeded! Output single executable saved in: dist/PhonePe_Expense_Tracker.exe")
    else:
        print(f"\n❌ Build failed with exit code {result.returncode}")


def launch_desktop():
    """Launches the desktop GUI application."""
    print("===================================================")
    print("  Starting PhonePe Expense Tracker Desktop App...  ")
    print("===================================================")
    try:
        from backend.app import main
        main()
    except Exception as e:
        print(f"\n❌ Error launching desktop application: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    if "--build" in sys.argv:
        build_executable()
    else:
        launch_desktop()
