"""Desktop API Bridge bridging pywebview Javascript layer with Python Domain Services."""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import webview

from backend.src.services.tracker import ExpenseTrackerService
from backend.src.services.exporter import ExportService
from backend.src.config.settings import DEFAULT_BUDGET_LIMIT, DEFAULT_DATA_FILE, DATA_DIR
from backend.src.utils.logger import setup_logger

logger = setup_logger("DesktopAPI")


class DesktopAPI:
    """JS-invokable API methods exposed to the frontend UI."""

    def __init__(self, window: Optional[webview.Window] = None):
        self._window: Optional[webview.Window] = window
        self.tracker_service = ExpenseTrackerService(default_budget=DEFAULT_BUDGET_LIMIT)
        self._current_payload: Optional[Dict[str, Any]] = None

    def set_window(self, window: webview.Window) -> None:
        """Assigns the pywebview window instance."""
        self._window = window

    def open_file_dialog(self) -> Optional[str]:
        """Opens native OS file chooser to select a transaction text file."""
        if not self._window:
            logger.warning("Window reference is not initialized")
            return None

        file_types = ("Transaction Files (*.txt;*.csv)", "All files (*.*)")
        result = self._window.create_file_dialog(
            webview.OPEN_DIALOG,
            allow_multiple=False,
            file_types=file_types,
        )

        if result and len(result) > 0:
            return result[0]
        return None

    def process_file(self, file_path: str, budget_limit: float = None) -> Dict[str, Any]:
        """Parses and computes analytics for a specific file path."""
        try:
            logger.info(f"Processing file: {file_path}")
            limit = float(budget_limit) if budget_limit is not None else DEFAULT_BUDGET_LIMIT
            payload = self.tracker_service.process_file_or_default(file_path, budget_limit=limit)
            dict_payload = payload.to_dict()
            self._current_payload = dict_payload
            return {"success": True, "data": dict_payload}
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            return {"success": False, "error": str(e)}

    def process_raw_text(self, text_content: str, budget_limit: float = None) -> Dict[str, Any]:
        """Parses and computes analytics for raw pasted or dropped text content."""
        try:
            limit = float(budget_limit) if budget_limit is not None else DEFAULT_BUDGET_LIMIT
            payload = self.tracker_service.process_raw_content(text_content, budget_limit=limit)
            dict_payload = payload.to_dict()
            self._current_payload = dict_payload
            return {"success": True, "data": dict_payload}
        except Exception as e:
            logger.error(f"Error processing text content: {e}")
            return {"success": False, "error": str(e)}

    def recalculate_budget(self, budget_limit: float) -> Dict[str, Any]:
        """Recalculates budget metrics dynamically without re-parsing files."""
        try:
            if not self._current_payload or not self._current_payload.get("transactions"):
                return {"success": False, "error": "No transactions loaded"}

            # Reconstruct Transaction models from cached dictionary
            from backend.src.models.expense import Transaction
            transactions = [
                Transaction(
                    id=t["id"],
                    date=t["date"],
                    merchant=t["merchant"],
                    amount=t["amount"],
                    category=t["category"],
                    raw_line_number=t["raw_line_number"],
                )
                for t in self._current_payload["transactions"]
            ]

            summary = self.tracker_service.calculate_summary(transactions, budget_limit=float(budget_limit))
            self._current_payload["summary"] = summary.to_dict()
            return {"success": True, "data": self._current_payload}
        except Exception as e:
            logger.error(f"Error recalculating budget: {e}")
            return {"success": False, "error": str(e)}

    def get_sample_data(self) -> Dict[str, Any]:
        """Loads and returns the default sample transaction dataset."""
        if DEFAULT_DATA_FILE.exists():
            return self.process_file(str(DEFAULT_DATA_FILE), budget_limit=DEFAULT_BUDGET_LIMIT)
        return {"success": False, "error": "Sample data file not found"}

    def export_data(self, format_type: str = "csv") -> Dict[str, Any]:
        """Prompts user with a Save File dialog and writes out the report."""
        if not self._current_payload:
            return {"success": False, "error": "No data available to export"}

        fmt = format_type.lower()
        ext_map = {
            "csv": ("CSV File (*.csv)", "phonepe_expense_report.csv"),
            "json": ("JSON File (*.json)", "phonepe_expense_report.json"),
            "html": ("HTML Report (*.html)", "phonepe_expense_report.html"),
        }

        if fmt not in ext_map:
            return {"success": False, "error": f"Unsupported format '{fmt}'"}

        file_type_desc, default_name = ext_map[fmt]

        save_path = None
        if self._window:
            result = self._window.create_file_dialog(
                webview.SAVE_DIALOG,
                save_filename=default_name,
                file_types=(file_type_desc, "All files (*.*)"),
            )
            if result:
                save_path = result if isinstance(result, str) else result[0]

        if not save_path:
            # Fallback to data directory
            save_path = str(DATA_DIR / default_name)

        try:
            if fmt == "csv":
                ExportService.export_csv(self._current_payload, Path(save_path))
            elif fmt == "json":
                ExportService.export_json(self._current_payload, Path(save_path))
            elif fmt == "html":
                ExportService.export_html_report(self._current_payload, Path(save_path))

            return {"success": True, "path": save_path}
        except Exception as e:
            logger.error(f"Export error: {e}")
            return {"success": False, "error": str(e)}
