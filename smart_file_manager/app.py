"""Application startup and QApplication lifecycle."""

import sys

from PyQt6.QtWidgets import QApplication

from .config import APP_NAME, VERSION, AppConfig
from .logging_config import configure_logging
from .ui.main_window import SFM_Lite


def run() -> int:
    """Create and run the Smart File Manager application."""
    config = AppConfig()
    configure_logging(config.get("activity_logging"))

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(VERSION)

    window = SFM_Lite(config)
    window.show()

    return app.exec()