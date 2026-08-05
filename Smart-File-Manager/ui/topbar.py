"""
ui/topbar.py
============
Header panel builder — top banner with the app title and all action buttons.
"""

from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from utils.constants import COLORS


def build_header(window) -> QFrame:
    """
    Build and return the top header frame.

    Sets the following attributes on *window*:
        btn_add_folder, btn_remove_folder, btn_preview,
        btn_organize, btn_clear_log
    """
    frame = QFrame()
    frame.setStyleSheet(
        f"background-color: {COLORS['surface']};"
        f"border: 1px solid {COLORS['border']};"
        f"border-radius: 8px;"
    )
    layout = QHBoxLayout(frame)
    layout.setContentsMargins(16, 10, 16, 10)

    # App name + subtitle
    title = QLabel("Smart File Manager")
    title.setStyleSheet(
        f"font-size: 20px; font-weight: 700; color: {COLORS['accent']};"
        "border: none; background: transparent;"
    )
    subtitle = QLabel("Organize your files automatically")
    subtitle.setStyleSheet(
        f"font-size: 12px; color: {COLORS['text_muted']};"
        "border: none; background: transparent;"
    )

    title_col = QVBoxLayout()
    title_col.setSpacing(2)
    title_col.addWidget(title)
    title_col.addWidget(subtitle)
    layout.addLayout(title_col)
    layout.addStretch()

    # Action buttons
    window.btn_add_folder = QPushButton("＋  Add Folder")
    window.btn_remove_folder = QPushButton("－  Remove")
    window.btn_preview = QPushButton("🔍  Preview")
    window.btn_organize = QPushButton("▶  Organize Now")
    window.btn_clear_log = QPushButton("🗑  Clear Log")

    window.btn_remove_folder.setObjectName("btn_secondary")
    window.btn_clear_log.setObjectName("btn_secondary")
    window.btn_organize.setObjectName("btn_success")

    for btn in (
        window.btn_add_folder,
        window.btn_remove_folder,
        window.btn_preview,
        window.btn_organize,
        window.btn_clear_log,
    ):
        layout.addWidget(btn)

    # Connect signals
    window.btn_add_folder.clicked.connect(window._add_folders)
    window.btn_remove_folder.clicked.connect(window._remove_selected_folder)
    window.btn_preview.clicked.connect(window._run_preview)
    window.btn_organize.clicked.connect(window._run_organize)
    window.btn_clear_log.clicked.connect(window._clear_log)

    return frame
