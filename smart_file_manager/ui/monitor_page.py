"""Live Monitor page: watch one folder and list file events as they happen."""

from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import Callable

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..services.monitor import (
    CREATED,
    DELETED,
    MODIFIED,
    MOVED,
    WATCHDOG_AVAILABLE,
    FolderMonitor,
    MonitorError,
    MonitorEvent,
)

logger = logging.getLogger(__name__)

MAX_ROWS = 500
POLL_INTERVAL_MS = 250

_LABELS = {CREATED: "Created", MODIFIED: "Modified", DELETED: "Deleted", MOVED: "Moved"}


class MonitorPage(QWidget):
    """GUI for :class:`FolderMonitor`.  Events are polled on the GUI thread."""

    def __init__(self, folder_provider: Callable[[], Path], parent: QWidget | None = None):
        super().__init__(parent)
        self._folder_provider = folder_provider
        self.monitor = FolderMonitor()
        self._event_total = 0

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(12)

        heading = QLabel("Live Monitor")
        heading.setObjectName("heading")
        description = QLabel(
            "Watch a folder and see files appear, change, move or disappear. "
            "Monitoring only observes - it never changes your files."
        )
        description.setObjectName("description")
        description.setWordWrap(True)
        layout.addWidget(heading)
        layout.addWidget(description)

        status_row = QHBoxLayout()
        self.status_dot = QLabel("●")
        self.status_dot.setObjectName("statusDot")
        self.status_text = QLabel("")
        status_row.addWidget(self.status_dot)
        status_row.addWidget(self.status_text, 1)
        layout.addLayout(status_row)

        folder_row = QHBoxLayout()
        self.folder_edit = QLineEdit()
        self.folder_edit.setReadOnly(True)
        self.folder_edit.setPlaceholderText("Choose a folder to watch…")
        self.choose_button = QPushButton("📂 Choose…")
        self.current_button = QPushButton("Use Current Folder")
        folder_row.addWidget(self.folder_edit, 1)
        folder_row.addWidget(self.choose_button)
        folder_row.addWidget(self.current_button)
        layout.addLayout(folder_row)

        control_row = QHBoxLayout()
        self.recursive_check = QCheckBox("Include subfolders")
        self.start_button = QPushButton("▶ Start")
        self.stop_button = QPushButton("■ Stop")
        self.clear_button = QPushButton("Clear List")
        control_row.addWidget(self.recursive_check)
        control_row.addStretch()
        control_row.addWidget(self.start_button)
        control_row.addWidget(self.stop_button)
        control_row.addWidget(self.clear_button)
        layout.addLayout(control_row)

        self.notice = QLabel(
            "Live Monitor needs the optional 'watchdog' package.\n"
            "Install it with:  pip install watchdog   - the rest of Smart File Manager works without it."
        )
        self.notice.setObjectName("preview")
        self.notice.setWordWrap(True)
        self.notice.setVisible(not WATCHDOG_AVAILABLE)
        layout.addWidget(self.notice)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Time", "Event", "Path"])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table, 1)

        self.footer = QLabel("")
        self.footer.setObjectName("status")
        layout.addWidget(self.footer)

        self._timer = QTimer(self)
        self._timer.setInterval(POLL_INTERVAL_MS)
        self._timer.timeout.connect(self._poll)

        self.choose_button.clicked.connect(self._choose_folder)
        self.current_button.clicked.connect(self.use_current_folder)
        self.start_button.clicked.connect(self.start_monitoring)
        self.stop_button.clicked.connect(self.stop_monitoring)
        self.clear_button.clicked.connect(self._clear)

        self._set_state("stopped")

    # ---- state / indicator ----------------------------------------------

    def _set_state(self, state: str, detail: str = "") -> None:
        running = state == "running"
        default_text = {
            "running": f"Monitoring {self.monitor.folder}",
            "stopped": "Not monitoring",
            "error": "Monitoring stopped because of an error",
        }[state]
        self.status_text.setText(detail or default_text)
        self.status_dot.setProperty("state", state)
        self.status_dot.style().unpolish(self.status_dot)
        self.status_dot.style().polish(self.status_dot)
        self.start_button.setEnabled(not running and WATCHDOG_AVAILABLE)
        self.stop_button.setEnabled(running)
        self.choose_button.setEnabled(not running)
        self.current_button.setEnabled(not running)
        self.recursive_check.setEnabled(not running)

    def is_monitoring(self) -> bool:
        return self.monitor.is_running()

    # ---- user actions -----------------------------------------------------

    def use_current_folder(self) -> None:
        self.folder_edit.setText(str(self._folder_provider()))

    def _choose_folder(self) -> None:
        start = self.folder_edit.text() or str(self._folder_provider())
        chosen = QFileDialog.getExistingDirectory(self.window(), "Choose a folder to watch", start)
        if chosen:
            self.folder_edit.setText(chosen)

    def start_monitoring(self) -> None:
        if self.monitor.is_running():
            return
        if not self.folder_edit.text():
            self.use_current_folder()
        folder = self.folder_edit.text()
        try:
            self.monitor.start(folder, recursive=self.recursive_check.isChecked())
        except MonitorError as error:
            self._set_state("error", str(error))
            return
        self._timer.start()
        self._set_state("running")

    def stop_monitoring(self) -> None:
        """Stop the observer and poll timer.  Also called when the app closes."""
        self._timer.stop()
        clean = self.monitor.stop()
        self._poll()  # show events that arrived just before stopping
        self._set_state("stopped", "" if clean else "Stopped (the watcher thread was slow to exit)")

    def _clear(self) -> None:
        self.table.setRowCount(0)
        self._event_total = 0
        self._update_footer()

    # ---- polling (GUI thread) ---------------------------------------------

    def _poll(self) -> None:
        events = self.monitor.drain()
        if events:
            self._add_events(events)
        if self._timer.isActive() and not self.monitor.is_running():
            logger.error("Live monitor thread ended unexpectedly for %s", self.monitor.folder)
            self._timer.stop()
            self.monitor.stop()
            self._set_state("error", "Monitoring stopped unexpectedly (the folder may have been removed).")

    def _display_path(self, path: str) -> str:
        base = self.monitor.folder
        if base is not None:
            try:
                relative = os.path.relpath(path, base)
                if not relative.startswith(".."):
                    return relative
            except ValueError:  # different drive on Windows
                pass
        return path

    def _add_events(self, events: list[MonitorEvent]) -> None:
        self.table.setUpdatesEnabled(False)
        try:
            for event in events:
                text = self._display_path(event.path)
                if event.kind == MOVED and event.destination:
                    text = f"{text}  →  {self._display_path(event.destination)}"
                if event.is_directory:
                    text += "  (folder)"
                self.table.insertRow(0)
                values = (time.strftime("%H:%M:%S", time.localtime(event.timestamp)),
                          _LABELS.get(event.kind, event.kind), text)
                for column, value in enumerate(values):
                    item = QTableWidgetItem(value)
                    item.setToolTip(event.path)
                    self.table.setItem(0, column, item)
            while self.table.rowCount() > MAX_ROWS:
                self.table.removeRow(self.table.rowCount() - 1)
        finally:
            self.table.setUpdatesEnabled(True)
        self._event_total += len(events)
        self._update_footer()

    def _update_footer(self) -> None:
        extra = self.monitor.suppressed_count
        dropped = self.monitor.dropped_count
        text = f"{self._event_total} events shown (newest first, last {MAX_ROWS} kept)"
        if extra:
            text += f" - {extra} duplicate events merged"
        if dropped:
            text += f" - {dropped} events skipped because the list was overloaded"
        self.footer.setText(text)
