"""Live folder monitoring service built on the optional ``watchdog`` package.

This module has no Qt dependency.  Watchdog delivers events on its own
observer thread; the handler here only appends to a thread-safe queue, and
the GUI drains that queue from its own thread with :meth:`FolderMonitor.drain`.
No widget is ever touched from the observer thread.

Watchdog is optional: if it is not installed, importing this module still
works and :data:`WATCHDOG_AVAILABLE` is False.
"""

from __future__ import annotations

import logging
import os
import queue
import threading
import time
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

try:  # pragma: no cover - exercised by tests only when watchdog is installed
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer

    WATCHDOG_AVAILABLE = True
except ImportError:  # pragma: no cover
    FileSystemEventHandler = object  # type: ignore[assignment,misc]
    Observer = None  # type: ignore[assignment]
    WATCHDOG_AVAILABLE = False

CREATED = "created"
MODIFIED = "modified"
DELETED = "deleted"
MOVED = "moved"

DEBOUNCE_SECONDS = 0.75
MAX_QUEUE_SIZE = 5000
STOP_TIMEOUT_SECONDS = 3.0
_MAX_DEBOUNCE_KEYS = 2000


class MonitorError(RuntimeError):
    """Monitoring could not start or has failed (message is user-friendly)."""


class MonitorUnavailableError(MonitorError):
    """The optional watchdog package is not installed."""


@dataclass(frozen=True)
class MonitorEvent:
    timestamp: float
    kind: str
    path: str
    destination: str = ""
    is_directory: bool = False


class Debouncer:
    """Drop repeats of the same (kind, path) seen within ``window`` seconds.

    Editors and downloads emit bursts of "modified" events for one file; this
    shows the first and suppresses the rest.  Time is injectable for tests.
    """

    def __init__(self, window: float = DEBOUNCE_SECONDS):
        self.window = window
        self._seen: dict[tuple[str, str], float] = {}
        self.suppressed = 0

    def allow(self, kind: str, path: str, now: float | None = None) -> bool:
        now = time.monotonic() if now is None else now
        key = (kind, path)
        last = self._seen.get(key)
        self._seen[key] = now
        if last is not None and now - last < self.window:
            self.suppressed += 1
            return False
        if len(self._seen) > _MAX_DEBOUNCE_KEYS:
            cutoff = now - self.window
            self._seen = {k: t for k, t in self._seen.items() if t >= cutoff}
        return True


class _Handler(FileSystemEventHandler):  # type: ignore[misc,valid-type]
    def __init__(self, sink: "queue.Queue[MonitorEvent]", debouncer: Debouncer, lock: threading.Lock):
        super().__init__()
        self._sink = sink
        self._debouncer = debouncer
        self._lock = lock
        self.dropped = 0

    def on_any_event(self, event) -> None:  # runs on watchdog's thread
        kind = event.event_type
        if kind not in {CREATED, MODIFIED, DELETED, MOVED}:
            return  # e.g. "opened"/"closed" events from newer watchdog versions
        is_dir = bool(event.is_directory)
        if kind == MODIFIED and is_dir:
            return  # parent-folder "modified" noise for every child change
        src = os.fsdecode(event.src_path)
        dest = os.fsdecode(getattr(event, "dest_path", "") or "")
        with self._lock:
            if not self._debouncer.allow(kind, src):
                return
        try:
            self._sink.put_nowait(MonitorEvent(time.time(), kind, src, dest, is_dir))
        except queue.Full:
            self.dropped += 1


class FolderMonitor:
    """Start/stop wrapper around a watchdog ``Observer`` for one folder."""

    def __init__(self, debounce_seconds: float = DEBOUNCE_SECONDS):
        self._queue: "queue.Queue[MonitorEvent]" = queue.Queue(maxsize=MAX_QUEUE_SIZE)
        self._debouncer = Debouncer(debounce_seconds)
        self._lock = threading.Lock()
        self._observer = None
        self._handler: _Handler | None = None
        self.folder: Path | None = None
        self.recursive = False

    # -- state ---------------------------------------------------------
    def is_running(self) -> bool:
        observer = self._observer
        return observer is not None and observer.is_alive()

    @property
    def suppressed_count(self) -> int:
        return self._debouncer.suppressed

    @property
    def dropped_count(self) -> int:
        return self._handler.dropped if self._handler else 0

    # -- control -------------------------------------------------------
    def start(self, folder: str | os.PathLike[str], recursive: bool = False) -> None:
        """Begin watching ``folder``.  Raises :class:`MonitorError` on failure."""
        if not WATCHDOG_AVAILABLE:
            raise MonitorUnavailableError(
                "Live Monitor needs the 'watchdog' package. Install it with: pip install watchdog"
            )
        if self._observer is not None:
            raise MonitorError("Monitoring is already running.")

        path = Path(folder)
        try:
            if not path.is_dir():
                raise MonitorError("That folder does not exist or is not a folder.")
        except OSError as error:
            raise MonitorError(f"Cannot access that folder: {error.strerror or error}") from error

        self.drain()  # discard stale events from an earlier session
        handler = _Handler(self._queue, self._debouncer, self._lock)
        observer = Observer()
        try:
            observer.schedule(handler, str(path), recursive=recursive)
            observer.start()
        except (OSError, RuntimeError) as error:
            logger.error("Live monitor failed to start on %s: %s", path, error)
            try:
                observer.stop()
            except (RuntimeError, OSError):
                pass
            raise MonitorError(
                f"Could not start monitoring: {getattr(error, 'strerror', None) or error}"
            ) from error

        self._observer, self._handler = observer, handler
        self.folder, self.recursive = path, recursive
        logger.info("Live monitor started on %s (recursive=%s)", path, recursive)

    def stop(self) -> bool:
        """Stop watching and join the observer thread.  Safe to call twice.

        Returns True if the observer thread ended cleanly within the timeout.
        """
        observer, self._observer = self._observer, None
        if observer is None:
            return True
        clean = True
        try:
            observer.stop()
            if observer.is_alive():
                observer.join(timeout=STOP_TIMEOUT_SECONDS)
            clean = not observer.is_alive()
        except (RuntimeError, OSError) as error:
            logger.error("Live monitor did not stop cleanly: %s", error)
            clean = False
        if not clean:
            logger.warning("Live monitor thread still alive after %.1fs", STOP_TIMEOUT_SECONDS)
        logger.info("Live monitor stopped (suppressed %d duplicate events)", self._debouncer.suppressed)
        return clean

    def drain(self, limit: int = 200) -> list[MonitorEvent]:
        """Return up to ``limit`` queued events (call from the GUI thread)."""
        events: list[MonitorEvent] = []
        while len(events) < limit:
            try:
                events.append(self._queue.get_nowait())
            except queue.Empty:
                break
        return events
