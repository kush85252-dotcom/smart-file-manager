"""Application startup and QApplication lifecycle."""

import sys

from PyQt6.QtWidgets import QApplication

from .config import APP_NAME, VERSION
from .logging_config import configure_logging
from .ui.main_window import SFM_Lite


def run() -> int:
    """Create and run the Smart File Manager application."""
    configure_logging()

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(VERSION)

    window = SFM_Lite()
    window.show()

    return app.exec()