"""
ui/sidebar.py
=============
Left panel builder — selected folders list and Auto Mode (watchdog) controls.
"""

from PyQt6.QtWidgets import (
    QGroupBox,
    QLabel,
    QListWidget,
    QPushButton,
    QVBoxLayout,
)

from backend.watcher import FolderWatcher
from utils.constants import COLORS


def build_left_panel(window) -> QGroupBox:
    """
    Build and return the left panel QGroupBox.

    Sets the following attributes on *window*:
        folder_list, btn_start_auto, btn_stop_auto, auto_status_lbl
    """
    group = QGroupBox("Selected Folders")
    layout = QVBoxLayout(group)
    layout.setSpacing(8)

    # Folder list
    window.folder_list = QListWidget()
    window.folder_list.setToolTip("Folders to organize")
    layout.addWidget(window.folder_list, stretch=1)

    # Auto-mode sub-group
    auto_group = QGroupBox("Auto Mode  (Watchdog)")
    auto_layout = QVBoxLayout(auto_group)
    auto_layout.setSpacing(6)

    info_lbl = QLabel(
        f"Monitors selected folders for new files.\n"
        f"Waits {FolderWatcher.DEBOUNCE_SECONDS}s before moving them."
    )
    info_lbl.setStyleSheet(
        f"color: {COLORS['text_muted']}; font-size: 11px;"
        "border: none; background: transparent;"
    )
    info_lbl.setWordWrap(True)
    auto_layout.addWidget(info_lbl)

    window.btn_start_auto = QPushButton("▶  Start Auto Mode")
    window.btn_stop_auto = QPushButton("■  Stop Auto Mode")
    window.btn_stop_auto.setObjectName("btn_danger")

    window.btn_start_auto.clicked.connect(window._start_auto_mode)
    window.btn_stop_auto.clicked.connect(window._stop_auto_mode)

    auto_layout.addWidget(window.btn_start_auto)
    auto_layout.addWidget(window.btn_stop_auto)

    # Auto-mode status indicator
    window.auto_status_lbl = QLabel("● Inactive")
    window.auto_status_lbl.setStyleSheet(
        f"color: {COLORS['text_muted']}; font-weight: 600;"
        "border: none; background: transparent;"
    )
    auto_layout.addWidget(window.auto_status_lbl)

    layout.addWidget(auto_group)
    return group
