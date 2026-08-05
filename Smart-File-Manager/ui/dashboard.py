"""
ui/dashboard.py
===============
MainWindow — the application's main window.
Hosts all panels: folder list, preview, log, report, and auto-mode controls.
Delegates panel construction to the ui sub-modules and core logic to backend modules.
"""

from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QFileDialog,
    QListWidgetItem,
    QMainWindow,
    QSplitter,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)
from watchdog.observers import Observer

from backend.config import load_settings, save_settings
from backend.logger import append_log
from backend.organizer import FileOrganizer
from backend.reports import show_report
from backend.watcher import FolderWatcher
from backend.worker import OrganizerWorker, PreviewScanner
from ui.dialogs import confirm_organize
from ui.sidebar import build_left_panel
from ui.topbar import build_header
from ui.widgets import build_bottom_bar, build_right_panel
from utils.constants import COLORS
from utils.helpers import timestamp


class MainWindow(QMainWindow):
    """
    The application's main window.
    Hosts all panels: folder list, preview, log, report, and auto-mode controls.
    """

    # Qt signals used by background threads to update the GUI safely
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int, int)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart File Manager")
        self.setMinimumSize(1100, 700)
        self.resize(1280, 800)

        # State
        self._selected_folders: list[Path] = []
        self._organizer_worker: OrganizerWorker | None = None
        self._preview_scanner: PreviewScanner | None = None
        self._observer: Observer | None = None   # watchdog observer
        self._watcher: FolderWatcher | None = None  # our event handler
        self._auto_mode_active = False

        # Load persistent settings
        self._settings = load_settings()

        # Connect our own signals (used by background threads)
        self.log_signal.connect(self._append_log)
        self.progress_signal.connect(self._update_progress)

        self._build_ui()
        self._set_initial_state()

    # ── UI Construction ──────────────────────────────────────────────────────

    def _build_ui(self):
        """Assemble all widgets and layouts."""
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(12, 12, 12, 8)
        root_layout.setSpacing(8)

        # Header
        root_layout.addWidget(build_header(self))

        # Main splitter: left panel | right tabs
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(6)
        splitter.addWidget(build_left_panel(self))
        splitter.addWidget(build_right_panel(self))
        splitter.setSizes([340, 900])
        root_layout.addWidget(splitter, stretch=1)

        # Bottom bar: progress + status
        root_layout.addWidget(build_bottom_bar(self))

        # Status bar (window footer)
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
        self._status_bar.showMessage("Ready — add folders to get started.")

    # ── Initial State ────────────────────────────────────────────────────────

    def _set_initial_state(self):
        """Disable buttons that require folders or that must not run concurrently."""
        self.btn_remove_folder.setEnabled(False)
        self.btn_preview.setEnabled(False)
        self.btn_organize.setEnabled(False)
        self.btn_stop_auto.setEnabled(False)
        self.btn_start_auto.setEnabled(False)

    def _refresh_button_states(self):
        """Enable / disable buttons based on current application state."""
        print("Selected folders:", self._selected_folders)
        has_folders = bool(self._selected_folders)
        print("Has folders:", has_folders)
        is_busy = (
            self._organizer_worker is not None and self._organizer_worker.isRunning()
        )
        auto_active = self._auto_mode_active
        has_selected = bool(self.folder_list.selectedItems())

        self.btn_add_folder.setEnabled(not is_busy)
        self.btn_remove_folder.setEnabled(
            has_folders and has_selected and not is_busy and not auto_active
        )
        self.btn_preview.setEnabled(has_folders and not is_busy and not auto_active)
        self.btn_organize.setEnabled(has_folders and not is_busy and not auto_active)
        self.btn_start_auto.setEnabled(has_folders and not auto_active and not is_busy)
        self.btn_stop_auto.setEnabled(auto_active)

    # ── Folder Management ────────────────────────────────────────────────────

    def _add_folders(self):
        """Open a dialog to choose one folder; can call multiple times."""
        folder_str = QFileDialog.getExistingDirectory(
            self, "Select Folder to Organize", str(Path.home())
        )
        if not folder_str:
            return  # User cancelled

        folder = Path(folder_str)
        # Avoid duplicates
        if folder in self._selected_folders:
            self._status_bar.showMessage(f"Folder already added: {folder}")
            return

        self._selected_folders.append(folder)
        self._settings["selected_folders"] = [
            str(p) for p in self._selected_folders
        ]
        save_settings(self._settings)
        print(self._settings["selected_folders"])

        # Show only the folder name in the list; full path in tooltip
        item = QListWidgetItem(folder.name)
        item.setToolTip(str(folder))
        item.setData(Qt.ItemDataRole.UserRole, folder)
        self.folder_list.addItem(item)

        self._append_log(f"[{timestamp()}] Added folder: {folder}")
        self._status_bar.showMessage(f"Added: {folder}")
        self._refresh_button_states()

    def _remove_selected_folder(self):
        """Remove the currently highlighted folder from the list."""
        items = self.folder_list.selectedItems()
        if not items:
            return
        for item in items:
            folder = item.data(Qt.ItemDataRole.UserRole)
            self._selected_folders.remove(folder)
            self.folder_list.takeItem(self.folder_list.row(item))
            self._append_log(f"[{timestamp()}] Removed folder: {folder}")
        self._refresh_button_states()

    # ── Preview ──────────────────────────────────────────────────────────────

    def _run_preview(self):
        """Scan selected folders in the background and populate the preview tree."""
        if not self._selected_folders:
            return

        self.preview_tree.clear()
        self.preview_count_lbl.setText("Scanning…")
        self.btn_preview.setEnabled(False)
        self.tabs.setCurrentIndex(0)  # Switch to Preview tab

        self._preview_scanner = PreviewScanner(self._selected_folders, parent=self)
        self._preview_scanner.item_found.connect(self._add_preview_item)
        self._preview_scanner.done_signal.connect(self._preview_done)
        self._preview_scanner.start()

    def _add_preview_item(self, folder: str, name: str, category: str, size: str):
        """Slot: add one row to the preview tree (called from scanner thread via signal)."""
        from PyQt6.QtWidgets import QTreeWidgetItem

        item = QTreeWidgetItem([Path(folder).name, name, category, size])
        item.setToolTip(0, folder)

        # Color-code the category column
        cat_colors = {
            "Documents": "#60a5fa",
            "Images": "#f472b6",
            "Videos": "#fb923c",
            "Audio": "#a78bfa",
            "Archives": "#facc15",
            "Applications": "#f87171",
            "Android APKs": "#4ade80",
            "Scripts": "#67e8f9",
            "Code": "#86efac",
            "Others": "#94a3b8",
        }
        color = cat_colors.get(category, COLORS["text_muted"])
        item.setForeground(2, QColor(color))

        self.preview_tree.addTopLevelItem(item)

    def _preview_done(self, total: int):
        """Slot: called when the preview scanner finishes."""
        self.preview_count_lbl.setText(f"Preview complete — {total} file(s) found.")
        self._status_bar.showMessage(f"Preview: {total} file(s) ready to organize.")
        self._refresh_button_states()

    # ── Organize ─────────────────────────────────────────────────────────────

    def _run_organize(self):
        """Start the organizer worker thread."""
        if not self._selected_folders:
            return

        # Confirm with user
        if not confirm_organize(self, len(self._selected_folders)):
            return

        # Reset progress
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(1)  # Will be updated as files are counted
        self.progress_label.setText("Organizing…")
        self._append_log(f"\n[{timestamp()}] ═══ Starting organization ═══")

        # Launch worker
        self._organizer_worker = OrganizerWorker(
            list(self._selected_folders), parent=self
        )
        self._organizer_worker.log_signal.connect(self._append_log)
        self._organizer_worker.progress_signal.connect(self._update_progress)
        self._organizer_worker.done_signal.connect(self._organize_done)
        self._organizer_worker.start()

        self.tabs.setCurrentIndex(1)  # Switch to log tab
        self._refresh_button_states()

    def _update_progress(self, current: int, total: int):
        """Update the progress bar (called from worker thread via signal)."""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.progress_label.setText(f"Moving file {current} of {total}…")

    def _organize_done(self, report: dict):
        """Slot: called when the organizer worker finishes."""
        self.progress_label.setText("Done!")
        self._status_bar.showMessage("Organization complete.")
        self._append_log(f"[{timestamp()}] ═══ Organization complete ═══\n")
        self._show_report(report)
        self.tabs.setCurrentIndex(2)  # Switch to report tab
        self._refresh_button_states()

    # ── Report ───────────────────────────────────────────────────────────────

    def _show_report(self, report: dict):
        """Populate the Report tab with results from the organizer."""
        show_report(self.report_tree, self.report_summary_lbl, report)

    # ── Auto Mode ────────────────────────────────────────────────────────────

    def _start_auto_mode(self):
        """Start watchdog observers for all selected folders."""
        if not self._selected_folders:
            return
        if self._auto_mode_active:
            return

        # Build a shared FileOrganizer that logs via our signal
        organizer = FileOrganizer(
            on_log=lambda msg: self.log_signal.emit(msg),
        )

        self._watcher = FolderWatcher(
            on_log=lambda msg: self.log_signal.emit(msg),
            organizer=organizer,
        )

        self._observer = Observer()
        for folder in self._selected_folders:
            try:
                self._observer.schedule(self._watcher, str(folder), recursive=False)
                self._append_log(f"[{timestamp()}] [AUTO] Watching: {folder}")
            except Exception as exc:
                self._append_log(f"[ERROR] Cannot watch {folder}: {exc}")

        self._observer.start()
        self._auto_mode_active = True

        self.auto_status_lbl.setText("● Active")
        self.auto_status_lbl.setStyleSheet(
            f"color: {COLORS['success']}; font-weight: 600;"
            "border: none; background: transparent;"
        )
        self._status_bar.showMessage(
            "Auto Mode active — monitoring folders for new files."
        )
        self.tabs.setCurrentIndex(1)  # Show log tab
        self._refresh_button_states()

    def _stop_auto_mode(self):
        """Stop watchdog and cancel all pending timers."""
        if not self._auto_mode_active:
            return

        # Cancel any pending move timers
        if self._watcher:
            self._watcher.cancel_all()
            self._watcher = None

        # Stop the watchdog observer
        if self._observer:
            self._observer.stop()
            self._observer.join(timeout=3)
            self._observer = None

        self._auto_mode_active = False

        self.auto_status_lbl.setText("● Inactive")
        self.auto_status_lbl.setStyleSheet(
            f"color: {COLORS['text_muted']}; font-weight: 600;"
            "border: none; background: transparent;"
        )
        self._append_log(f"[{timestamp()}] [AUTO] Stopped monitoring.")
        self._status_bar.showMessage("Auto Mode stopped.")
        self._refresh_button_states()

    # ── Log Helpers ──────────────────────────────────────────────────────────

    def _append_log(self, message: str):
        """
        Append a line to the log text area.
        Color-codes lines that contain keywords for quick scanning.
        Safe to call from any thread (connected via Qt signal).
        """
        append_log(self.log_text, message)

    def _clear_log(self):
        """Clear the activity log."""
        self.log_text.clear()

    # ── Close Event ──────────────────────────────────────────────────────────

    def closeEvent(self, event):
        """Ensure background threads are stopped before the window closes."""
        # Stop auto mode first (cancels timers, stops observer)
        if self._auto_mode_active:
            self._stop_auto_mode()

        # Wait for organizer worker if running
        if self._organizer_worker and self._organizer_worker.isRunning():
            self._organizer_worker.quit()
            self._organizer_worker.wait(3000)

        # Wait for preview scanner if running
        if self._preview_scanner and self._preview_scanner.isRunning():
            self._preview_scanner.quit()
            self._preview_scanner.wait(3000)

        event.accept()
