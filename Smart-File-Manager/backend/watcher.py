"""
backend/watcher.py
==================
FolderWatcher — watchdog event handler.
Detects new files in monitored folders and queues them for moving
after a configurable debounce delay (so partial downloads finish first).
"""

import threading
from pathlib import Path

from watchdog.events import FileSystemEventHandler

from utils.constants import FILE_CATEGORIES, OTHERS_CATEGORY
from utils.helpers import timestamp


class FolderWatcher(FileSystemEventHandler):
    """
    Watchdog event handler.
    When a new file appears in a monitored folder, waits DEBOUNCE_SECONDS
    before moving it (so partial downloads / in-progress writes finish first).
    """

    DEBOUNCE_SECONDS = 5  # seconds to wait before moving a newly detected file

    def __init__(self, on_log, organizer):
        """
        Parameters
        ----------
        on_log     : callable(str)     — log callback
        organizer  : FileOrganizer    — performs the actual move
        """
        super().__init__()
        self.on_log = on_log
        self.organizer = organizer
        # Track pending files: {path_str: timer_thread}
        self._pending: dict[str, threading.Timer] = {}
        self._lock = threading.Lock()

    def on_created(self, event):
        """Called by watchdog when a new file (not directory) is created."""
        if event.is_directory:
            return

        path = Path(event.src_path)

        # Ignore hidden files
        if path.name.startswith("."):
            return

        # Ignore files already inside a category sub-folder
        category_names = set(FILE_CATEGORIES.keys()) | {OTHERS_CATEGORY}
        if path.parent.name in category_names:
            return

        self.on_log(
            f"[{timestamp()}] [AUTO] Detected: {path.name} "
            f"— waiting {self.DEBOUNCE_SECONDS}s…"
        )
        self._schedule(path)

    def _schedule(self, path: Path):
        """Schedule a delayed move for *path*, cancelling any previous timer."""
        key = str(path)
        with self._lock:
            # Cancel existing timer for this file (e.g. file was modified again)
            if key in self._pending:
                self._pending[key].cancel()

            timer = threading.Timer(
                self.DEBOUNCE_SECONDS,
                self._move_file,
                args=(path,),
            )
            timer.daemon = True
            timer.start()
            self._pending[key] = timer

    def _move_file(self, path: Path):
        """Called after the debounce delay; performs the actual move."""
        key = str(path)
        with self._lock:
            self._pending.pop(key, None)

        self.organizer.move_single_file(path)

    def cancel_all(self):
        """Cancel all pending timers (called when Auto Mode is stopped)."""
        with self._lock:
            for timer in self._pending.values():
                timer.cancel()
            self._pending.clear()
