"""
backend/worker.py
=================
Background QThread workers:
  • OrganizerWorker  — runs organize_folders() off the main thread
  • PreviewScanner   — scans folders and emits file info for the preview tree
"""

from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal

from backend.organizer import FileOrganizer
from utils.helpers import format_size, get_category


class OrganizerWorker(QThread):
    """
    Runs FileOrganizer.organize_folders() on a background thread.
    Communicates with the main thread via Qt signals.
    """

    # Emitted for each log line
    log_signal = pyqtSignal(str)
    # Emitted as files are processed (current, total)
    progress_signal = pyqtSignal(int, int)
    # Emitted when all folders are done; carries the merged report dict
    done_signal = pyqtSignal(dict)

    def __init__(self, folders: list[Path], parent=None):
        super().__init__(parent)
        self.folders = folders

    def run(self):
        """Entry point for the background thread."""
        organizer = FileOrganizer(
            on_log=self.log_signal.emit,
            on_progress=self.progress_signal.emit,
            on_done=lambda report: None,  # we emit done_signal after all folders
        )
        combined = organizer.organize_folders(self.folders)
        self.done_signal.emit(combined)


class PreviewScanner(QThread):
    """
    Background thread that scans the selected folders and emits
    (folder, name, category, size) tuples for the preview tree.
    """

    item_found = pyqtSignal(str, str, str, str)  # folder, name, category, size
    done_signal = pyqtSignal(int)                 # total file count

    def __init__(self, folders: list[Path], parent=None):
        super().__init__(parent)
        self.folders = folders

    def run(self):
        total = 0
        for folder in self.folders:
            organizer = FileOrganizer()  # callbacks not needed here
            files = organizer.scan_folder(folder)
            for f in files:
                category = get_category(f)
                try:
                    size = format_size(f.stat().st_size)
                except OSError:
                    size = "?"
                self.item_found.emit(str(folder), f.name, category, size)
                total += 1
        self.done_signal.emit(total)
