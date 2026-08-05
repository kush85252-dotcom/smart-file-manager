"""
Smart File Manager
==================
A modern PyQt6 desktop application for organizing files into categories.

Features:
- Select multiple folders to organize
- Preview files before moving them
- Organize into Documents, Images, Videos, Audio, Archives,
  Applications, Android APKs, Scripts, Code, Others
- Auto Mode using watchdog to monitor folders in real time
- Live status log and move report
- Safe error handling — never crashes on bad files

Usage:
    python main.py
"""

import sys

from app import create_app
from ui.dashboard import MainWindow


def main():
    """Create the QApplication and show the main window."""
    app = create_app()

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
