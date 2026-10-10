"""Application startup and QApplication lifecycle."""

import logging
import sys

from PyQt6.QtWidgets import QApplication

from .config import APP_NAME, VERSION, AppConfig
from .logging_config import configure_logging, install_exception_hook
from .ui.main_window import SFM_Lite

def run() -> int:
    """Create and run the Smart File Manager application."""
    config = AppConfig()
    configure_logging(config.get("activity_logging"))
    install_exception_hook()
    logging.getLogger(__name__).info("%s %s starting", APP_NAME, VERSION)

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(VERSION)

    window = SFM_Lite(config)
    window.show()

    exit_code = app.exec()
    logging.getLogger(__name__).info("%s exiting with code %s", APP_NAME, exit_code)
    return exit_code
