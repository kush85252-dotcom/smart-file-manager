"""
app.py
======
QApplication factory — creates and configures the application instance.
"""

import sys

from PyQt6.QtWidgets import QApplication

from utils.constants import STYLESHEET


def create_app() -> QApplication:
    """
    Create and configure the QApplication.
    Applies the global dark stylesheet and sets application metadata.
    """
    app = QApplication(sys.argv)
    app.setApplicationName("Smart File Manager")
    app.setApplicationVersion("1.0.0")
    app.setStyleSheet(STYLESHEET)
    return app
