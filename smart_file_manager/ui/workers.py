"""Qt worker threads.  Workers talk to the GUI only through Qt signals."""

from __future__ import annotations

import logging
import threading

from PyQt6.QtCore import QThread, pyqtSignal

from ..services.scanner import FAST, ScanResult, scan_folder

logger = logging.getLogger(__name__)


class ScanWorker(QThread):
    """Runs one read-only scan off the GUI thread.

    Signals (queued automatically across threads, so they are thread-safe):
      progress(ScanProgress)  - throttled by the scanner
      scan_finished(ScanResult)  - normal or cancelled completion
      scan_failed(str)  - unexpected error; message is user-friendly

    ``QThread.finished`` always fires last, so the window re-enables its
    buttons there and can never stay locked after a failure.
    """

    progress = pyqtSignal(object)
    scan_finished = pyqtSignal(object)
    scan_failed = pyqtSignal(str)

    def __init__(self, root, mode: str = FAST, include_hidden: bool = False, parent=None):
        super().__init__(parent)
        self._root = root
        self._mode = mode
        self._include_hidden = include_hidden
        self._cancel = threading.Event()

    def cancel(self) -> None:
        """Ask the scan to stop; it ends at the next cancellation check."""
        self._cancel.set()

    def run(self) -> None:
        try:
            result: ScanResult = scan_folder(
                self._root,
                self._mode,
                include_hidden=self._include_hidden,
                should_cancel=self._cancel.is_set,
                on_progress=self.progress.emit,
            )
        except Exception:  # noqa: BLE001 - thread boundary: report, never crash
            logger.exception("Unexpected error during %s scan of %s", self._mode, self._root)
            self.scan_failed.emit("The scan stopped because of an unexpected error. See the log for details.")
            return
        self.scan_finished.emit(result)
