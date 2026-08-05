"""
ui/widgets.py
=============
Panel / tab builder functions:
  • build_preview_tab   — Preview tab (QTreeWidget)
  • build_log_tab       — Activity Log tab (QTextEdit)
  • build_report_tab    — Report tab (QTreeWidget)
  • build_bottom_bar    — Progress bar + label
"""

from PyQt6.QtWidgets import (
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QProgressBar,
    QTabWidget,
    QTextEdit,
    QTreeWidget,
    QVBoxLayout,
    QWidget,
)

from utils.constants import COLORS


# ---------------------------------------------------------------------------
# PREVIEW TAB
# ---------------------------------------------------------------------------

def build_preview_tab(window) -> QWidget:
    """
    Build and return the Preview tab widget.

    Sets the following attributes on *window*:
        preview_tree, preview_count_lbl
    """
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setContentsMargins(8, 8, 8, 8)

    hint = QLabel(
        "Click  🔍 Preview  to scan your selected folders and see "
        "where each file will be moved before you start organizing."
    )
    hint.setWordWrap(True)
    hint.setStyleSheet(
        f"color: {COLORS['text_muted']}; font-size: 12px;"
        f"border: 1px solid {COLORS['border']}; border-radius: 6px;"
        f"background: {COLORS['surface']}; padding: 8px;"
    )
    layout.addWidget(hint)

    # Tree columns: Folder | File Name | Category | Size
    window.preview_tree = QTreeWidget()
    window.preview_tree.setHeaderLabels(["Folder", "File Name", "Category", "Size"])
    window.preview_tree.setAlternatingRowColors(True)
    window.preview_tree.setSortingEnabled(True)
    header = window.preview_tree.header()
    header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
    header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
    header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
    header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
    window.preview_tree.setColumnWidth(0, 180)
    window.preview_tree.setColumnWidth(2, 120)
    window.preview_tree.setColumnWidth(3, 80)
    layout.addWidget(window.preview_tree, stretch=1)

    window.preview_count_lbl = QLabel("No preview loaded.")
    window.preview_count_lbl.setStyleSheet(
        f"color: {COLORS['text_muted']}; font-size: 12px;"
    )
    layout.addWidget(window.preview_count_lbl)

    return widget


# ---------------------------------------------------------------------------
# LOG TAB
# ---------------------------------------------------------------------------

def build_log_tab(window) -> QWidget:
    """
    Build and return the Activity Log tab widget.

    Sets the following attributes on *window*:
        log_text
    """
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setContentsMargins(8, 8, 8, 8)

    window.log_text = QTextEdit()
    window.log_text.setReadOnly(True)
    window.log_text.setPlaceholderText("Activity log will appear here…")
    layout.addWidget(window.log_text)

    return widget


# ---------------------------------------------------------------------------
# REPORT TAB
# ---------------------------------------------------------------------------

def build_report_tab(window) -> QWidget:
    """
    Build and return the Report tab widget.

    Sets the following attributes on *window*:
        report_tree, report_summary_lbl
    """
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setContentsMargins(8, 8, 8, 8)

    window.report_tree = QTreeWidget()
    window.report_tree.setHeaderLabels(["Category", "Files Moved"])
    window.report_tree.setAlternatingRowColors(True)
    header = window.report_tree.header()
    header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
    header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
    window.report_tree.setColumnWidth(1, 120)
    layout.addWidget(window.report_tree, stretch=1)

    window.report_summary_lbl = QLabel(
        "No report yet — run Organize to generate one."
    )
    window.report_summary_lbl.setStyleSheet(
        f"color: {COLORS['text_muted']}; font-size: 12px;"
    )
    layout.addWidget(window.report_summary_lbl)

    return widget


# ---------------------------------------------------------------------------
# BOTTOM BAR
# ---------------------------------------------------------------------------

def build_bottom_bar(window) -> QFrame:
    """
    Build and return the bottom progress bar + label frame.

    Sets the following attributes on *window*:
        progress_label, progress_bar
    """
    frame = QFrame()
    layout = QHBoxLayout(frame)
    layout.setContentsMargins(0, 4, 0, 0)
    layout.setSpacing(10)

    window.progress_label = QLabel("Idle")
    window.progress_label.setStyleSheet(
        f"color: {COLORS['text_muted']}; font-size: 12px;"
    )
    window.progress_label.setFixedWidth(220)

    window.progress_bar = QProgressBar()
    window.progress_bar.setValue(0)
    window.progress_bar.setTextVisible(True)
    window.progress_bar.setFormat("%v / %m files")

    layout.addWidget(window.progress_label)
    layout.addWidget(window.progress_bar, stretch=1)

    return frame


# ---------------------------------------------------------------------------
# RIGHT PANEL (tabbed)
# ---------------------------------------------------------------------------

def build_right_panel(window) -> QTabWidget:
    """
    Build and return the tabbed right panel.

    Sets the following attributes on *window*:
        tabs
    """
    window.tabs = QTabWidget()
    window.tabs.addTab(build_preview_tab(window), "📁  Preview")
    window.tabs.addTab(build_log_tab(window), "📋  Activity Log")
    window.tabs.addTab(build_report_tab(window), "📊  Report")
    return window.tabs
