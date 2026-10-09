"""Fast Scan / Full Scan controls shown on the Overview page."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Callable

from PyQt6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..services.scanner import FAST, FULL, ScanProgress, ScanResult, is_drive_root
from ..utils import format_size
from .workers import ScanWorker

logger = logging.getLogger(__name__)

SHUTDOWN_WAIT_MS = 5000


class ScanPanel(QFrame):
    """Owns the scan worker, its buttons, progress and result display."""

    def __init__(
        self,
        folder_provider: Callable[[], Path],
        hidden_provider: Callable[[], bool],
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.setObjectName("settingsCard")
        self._folder_provider = folder_provider
        self._hidden_provider = hidden_provider
        self._worker: ScanWorker | None = None
        self.last_result: ScanResult | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(10)

        title = QLabel("Scan")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        intro = QLabel(
            "Scans only read information. They never change, move or delete your files, "
            "and they do not follow shortcuts/links."
        )
        intro.setObjectName("description")
        intro.setWordWrap(True)
        layout.addWidget(intro)

        buttons = QHBoxLayout()
        self.fast_button = QPushButton("⚡ Fast Scan (current folder)")
        self.full_button = QPushButton("🔍 Full Scan…")
        self.cancel_button = QPushButton("✖ Cancel")
        self.cancel_button.setEnabled(False)
        self.fast_button.clicked.connect(self.start_fast_scan)
        self.full_button.clicked.connect(self.start_full_scan)
        self.cancel_button.clicked.connect(self.cancel_scan)
        for button in (self.fast_button, self.full_button, self.cancel_button):
            buttons.addWidget(button)
        buttons.addStretch()
        layout.addLayout(buttons)

        # Range (0, 0) is Qt's "busy" bar: the total is unknown while scanning.
        self.progress = QProgressBar()
        self.progress.setRange(0, 1)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        layout.addWidget(self.progress)

        cards = QHBoxLayout()
        self.files_value = self._card(cards, "📄 Files")
        self.folders_value = self._card(cards, "📁 Folders")
        self.size_value = self._card(cards, "💾 Size")
        self.errors_value = self._card(cards, "⚠ Access errors")
        layout.addLayout(cards)

        self.status_label = QLabel("No scan has been run yet.")
        self.status_label.setObjectName("status")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        self.details_label = QLabel("")
        self.details_label.setObjectName("description")
        self.details_label.setWordWrap(True)
        self.details_label.setVisible(False)
        layout.addWidget(self.details_label)

    # ---- helpers -------------------------------------------------------

    def _card(self, row: QHBoxLayout, title: str) -> QLabel:
        card = QFrame()
        card.setObjectName("card")
        box = QVBoxLayout(card)
        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")
        value = QLabel("-")
        value.setObjectName("cardValue")
        box.addWidget(title_label)
        box.addWidget(value)
        row.addWidget(card)
        return value

    def _dialog_parent(self) -> QWidget:
        return self.window()

    def is_busy(self) -> bool:
        return self._worker is not None

    def _set_busy(self, busy: bool) -> None:
        self.fast_button.setEnabled(not busy)
        self.full_button.setEnabled(not busy)
        self.cancel_button.setEnabled(busy)
        if busy:
            self.progress.setRange(0, 0)
        else:
            self.progress.setRange(0, 1)
            self.progress.setValue(0)

    # ---- starting scans ------------------------------------------------

    def start_fast_scan(self) -> None:
        folder = Path(self._folder_provider())
        if self.is_busy():
            return
        if is_drive_root(folder):
            answer = QMessageBox.question(
                self._dialog_parent(),
                "Scan an entire drive?",
                f"The current folder is a drive root:\n\n{folder}\n\n"
                "A Fast Scan stops after 100,000 entries, but this can still take a while. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return
        self._start(folder, FAST)

    def start_full_scan(self) -> None:
        if self.is_busy():
            return
        chosen = QFileDialog.getExistingDirectory(
            self._dialog_parent(),
            "Choose a drive or folder for a Full Scan",
            str(self._folder_provider()),
        )
        if not chosen:
            return
        folder = Path(chosen)
        answer = QMessageBox.warning(
            self._dialog_parent(),
            "Full Scan may take a long time",
            f"Scan everything inside:\n\n{folder}\n\n"
            "A Full Scan has no size limit and includes hidden files. On a large folder or "
            "drive it can take many minutes and use the disk heavily on older computers.\n\n"
            "It is read-only and can be cancelled at any time. Start the Full Scan?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self._start(folder, FULL)

    def _start(self, folder: Path, mode: str) -> None:
        if self.is_busy():
            return
        worker = ScanWorker(folder, mode, include_hidden=self._hidden_provider(), parent=self)
        worker.progress.connect(self._on_progress)
        worker.scan_finished.connect(self._on_finished)
        worker.scan_failed.connect(self._on_failed)
        worker.finished.connect(self._on_thread_finished)
        self._worker = worker
        self._set_busy(True)
        self.details_label.setVisible(False)
        for label in (self.files_value, self.folders_value, self.size_value, self.errors_value):
            label.setText("0" if label is not self.size_value else "0 B")
        self.status_label.setText(f"{'Fast' if mode == FAST else 'Full'} scan running…")
        logger.info("Starting %s scan of %s", mode, folder)
        worker.start()

    def cancel_scan(self) -> None:
        if self._worker is not None:
            self.status_label.setText("Cancelling…")
            self.cancel_button.setEnabled(False)
            self._worker.cancel()

    def shutdown(self) -> None:
        """Cancel any running scan and wait briefly; called when the app closes."""
        worker = self._worker
        if worker is None:
            return
        worker.cancel()
        if not worker.wait(SHUTDOWN_WAIT_MS):
            logger.warning("Scan thread did not stop within %d ms during shutdown", SHUTDOWN_WAIT_MS)

    # ---- worker signals (always delivered on the GUI thread) ------------

    def _on_progress(self, progress: ScanProgress) -> None:
        self._show_counts(progress.files, progress.folders, progress.total_bytes, progress.access_errors)
        self.status_label.setText(f"Scanning… {progress.current_folder}")

    def _show_counts(self, files: int, folders: int, size: int, errors: int) -> None:
        self.files_value.setText(f"{files:,}")
        self.folders_value.setText(f"{folders:,}")
        self.size_value.setText(format_size(size))
        self.errors_value.setText(f"{errors:,}")

    def _on_finished(self, result: ScanResult) -> None:
        self.last_result = result
        if not result.ok:
            self.status_label.setText(result.root_error or "The scan could not start.")
            logger.warning("Scan of %s could not run: %s", result.root, result.root_error)
            return

        self._show_counts(result.files, result.folders, result.total_bytes, result.access_errors)
        if result.cancelled:
            state = "Scan cancelled - the numbers below are partial."
        elif result.truncated:
            state = ("Fast Scan stopped at its 100,000-entry limit - the numbers are partial. "
                     "Use Full Scan for everything.")
        else:
            state = "Scan complete."
        self.status_label.setText(f"{state} ({result.elapsed_seconds:.1f}s)")
        self.details_label.setText(self._details_text(result))
        self.details_label.setVisible(True)

    def _details_text(self, result: ScanResult) -> str:
        lines = [f"Folder: {result.root}"]
        if result.skipped_links:
            lines.append(f"Skipped {result.skipped_links:,} shortcut/link item(s) (never followed).")
        if result.skipped_protected:
            lines.append(f"Skipped {result.skipped_protected:,} protected system folder(s).")
        if result.categories:
            top = sorted(result.categories.items(), key=lambda kv: (-kv[1], kv[0]))[:8]
            lines.append("Categories: " + ", ".join(f"{name} {count:,}" for name, count in top))
        if result.largest_files:
            lines.append("Largest files:")
            lines.extend(f"  {format_size(size)}  {path}" for size, path in result.largest_files[:5])
        if result.error_samples:
            lines.append(f"Could not read {result.access_errors:,} item(s), for example:")
            lines.extend(f"  {sample}" for sample in result.error_samples[:5])
            if result.access_errors > 5:
                lines.append("  …more are listed in the log file.")
        return "\n".join(lines)

    def _on_failed(self, message: str) -> None:
        self.status_label.setText(message)

    def _on_thread_finished(self) -> None:
        """Runs after every scan, successful or not: always unlock the buttons."""
        worker, self._worker = self._worker, None
        self._set_busy(False)
        if worker is not None:
            worker.deleteLater()
