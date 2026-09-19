"""Desktop Application Entry Point for PhonePe Expense Tracker.

Runs a lightweight local daemon HTTP server and opens a native Edge WebView2 window.
"""

import os
import sys
import socket
import threading
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import webview

# Add project root to sys.path to enable clean imports
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    PROJECT_ROOT = Path(sys._MEIPASS)
else:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.src.api.bridge import DesktopAPI
from backend.src.config.settings import (
    WINDOW_TITLE,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    WINDOW_MIN_WIDTH,
    WINDOW_MIN_HEIGHT,
    STATIC_DIR,
)
from backend.src.utils.logger import setup_logger

logger = setup_logger("DesktopApp")


def get_free_port() -> int:
    """Finds an available TCP port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class QuietStaticServer(SimpleHTTPRequestHandler):
    """Quiet static file handler serving the frontend assets."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def log_message(self, format, *args):
        # Suppress verbose terminal log spam for static files
        pass

    def end_headers(self):
        # Prevent aggressive browser caching during development
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()


def start_local_server(port: int) -> ThreadingHTTPServer:
    """Starts a local HTTP server in a daemon thread."""
    server = ThreadingHTTPServer(("127.0.0.1", port), QuietStaticServer)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def main():
    """Initializes and starts the desktop application window."""
    logger.info("Initializing PhonePe Expense Tracker Desktop...")

    if not STATIC_DIR.exists() or not (STATIC_DIR / "index.html").exists():
        logger.error(f"Static directory or index.html not found at: {STATIC_DIR}")
        sys.exit(1)

    # 1. Allocate a local port and launch daemon HTTP server
    port = get_free_port()
    server = start_local_server(port)
    app_url = f"http://127.0.0.1:{port}/"
    logger.info(f"Local application server running at: {app_url}")

    # 2. Instantiate the Desktop API bridge
    api = DesktopAPI()

    # 3. Create the native desktop window with Edge WebView2
    window = webview.create_window(
        title=WINDOW_TITLE,
        url=app_url,
        js_api=api,
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT,
        min_size=(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT),
        background_color="#0f1016",
        text_select=True,
    )

    # 4. Link window reference to the API bridge
    api.set_window(window)

    try:
        # 5. Start the native window event loop
        webview.start(debug=False)
    finally:
        logger.info("Shutting down local server...")
        try:
            server.shutdown()
        except Exception:
            pass


if __name__ == "__main__":
    main()
