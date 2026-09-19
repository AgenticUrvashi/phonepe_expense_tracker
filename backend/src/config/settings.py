"""Configuration settings for PhonePe Expense Tracker."""

import sys
import os
from pathlib import Path

# Base Paths (Supports source execution & PyInstaller frozen bundle)
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    BUNDLE_DIR = Path(sys._MEIPASS)
    BACKEND_DIR = BUNDLE_DIR / "backend"
    ROOT_DIR = BUNDLE_DIR
    STATIC_DIR = BACKEND_DIR / "static"
    DATA_DIR = BUNDLE_DIR / "data"
else:
    BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
    ROOT_DIR = BACKEND_DIR.parent
    STATIC_DIR = BACKEND_DIR / "static"
    DATA_DIR = ROOT_DIR / "data"

DEFAULT_DATA_FILE = DATA_DIR / "transactions.txt"
DEFAULT_SUMMARY_OUTPUT = DATA_DIR / "summary.json"
DEFAULT_BUDGET_LIMIT = 10000.0

# Window Settings
WINDOW_TITLE = "PhonePe Expense Tracker"
WINDOW_WIDTH = 1300
WINDOW_HEIGHT = 880
WINDOW_MIN_WIDTH = 980
WINDOW_MIN_HEIGHT = 650
