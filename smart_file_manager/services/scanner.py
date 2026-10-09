"""Read-only filesystem scanning service (no Qt, no GUI).

Two modes share one walker:

* **Fast scan** - the everyday summary.  Hidden files and folders are skipped
  unless ``include_hidden`` is set, and the walk stops with ``truncated=True``
  after ``max_entries`` entries so it cannot run away on a huge tree.
* **Full scan** - an explicit, broader scan.  It includes hidden items, has no
  entry cap, and additionally reports the largest files.

Safety guarantees (covered by tests):

* The scanner never modifies, moves, renames or deletes anything; it only
  calls ``os.scandir`` and reads metadata.
* Symbolic links and Windows reparse points (junctions) are *never* followed,
  so link loops cannot occur.  Directories already visited (same device and
  inode) are skipped as a second line of defence on POSIX systems.
* Permission errors, vanished folders and other ``OSError``s are counted and
  scanning continues.
* Cancellation is cooperative and checked frequently.
"""

from __future__ import annotations

import heapq
import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from ..categorization import category_for

logger = logging.getLogger(__name__)

FAST = "fast"
FULL = "full"

DEFAULT_FAST_MAX_ENTRIES = 100_000
LARGEST_FILES_KEPT = 10
MAX_ERROR_SAMPLES = 25
PROGRESS_INTERVAL_SECONDS = 0.1
CANCEL_CHECK_EVERY = 128

# Windows "reparse point" attribute: set on junctions, symlinks, and some
# cloud placeholders.  Folders carrying it are never entered.
FILE_ATTRIBUTE_REPARSE_POINT = 0x400

# Windows folders that are always access-denied for normal users.
PROTECTED_DIRECTORY_NAMES = frozenset({"$recycle.bin", "system volume information"})


@dataclass
class ScanProgress:
    """Immutable-by-convention snapshot passed to progress callbacks."""

    files: int = 0
    folders: int = 0
    total_bytes: int = 0
    access_errors: int = 0
    current_folder: str = ""


@dataclass
class ScanResult:
    """Everything a finished (or cancelled) scan learned."""

    mode: str = FAST
    root: str = ""
    files: int = 0
    folders: int = 0
    total_bytes: int = 0
    access_errors: int = 0
    skipped_links: int = 0
    skipped_protected: int = 0
    cancelled: bool = False
    truncated: bool = False
    elapsed_seconds: float = 0.0
    root_error: str | None = None
    error_samples: list[str] = field(default_factory=list)
    categories: dict[str, int] = field(default_factory=dict)
    largest_files: list[tuple[int, str]] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.root_error is None

    def summary_line(self) -> str:
        """One privacy-conscious line suitable for the log file."""
        state = "cancelled" if self.cancelled else "truncated" if self.truncated else "complete"
        return (
            f"{self.mode} scan {state} of {self.root}: {self.files} files, "
            f"{self.folders} folders, {self.total_bytes} bytes, "
            f"{self.access_errors} access errors, {self.skipped_links} links skipped, "
            f"{self.elapsed_seconds:.2f}s"
        )


def is_reparse_point(stat_result: os.stat_result) -> bool:
    """True if a Windows stat result carries the reparse-point attribute."""
    attributes = getattr(stat_result, "st_file_attributes", 0)
    return bool(attributes & FILE_ATTRIBUTE_REPARSE_POINT)


def is_drive_root(path: str | os.PathLike[str]) -> bool:
    """True for a filesystem root such as ``C:\\`` or ``/``."""
    try:
        p = Path(path)
        return p.parent == p
    except (OSError, ValueError):
        return False


def _is_hidden_entry(entry: os.DirEntry, stat_result: os.stat_result | None) -> bool:
    if entry.name.startswith("."):
        return True
    # DirEntry.stat() is free on Windows, so this adds no syscalls there.
    if stat_result is not None and getattr(stat_result, "st_file_attributes", 0) & 0x2:
        return True
    return False


def iter_files(
    root: str | os.PathLike[str],
    *,
    include_hidden: bool = False,
    should_cancel: Callable[[], bool] | None = None,
):
    """Yield every regular file under ``root`` as a :class:`~pathlib.Path`.

    Same safety rules as :func:`scan_folder`: links, junctions and protected
    system folders are never entered, unreadable folders are skipped, and
    hidden items are skipped unless ``include_hidden``.  Used by the organizer
    when "Scan subfolders" is enabled.
    """
    cancel = should_cancel or (lambda: False)
    stack = [os.fspath(root)]
    visited: set[tuple[int, int]] = set()
    while stack:
        if cancel():
            return
        directory = stack.pop()
        try:
            iterator = os.scandir(directory)
        except OSError as error:
            logger.debug("iter_files could not read %s: %s", directory, error)
            continue
        with iterator:
            while True:
                try:
                    entry = next(iterator)
                except StopIteration:
                    break
                except OSError as error:
                    logger.debug("iter_files stopped reading %s: %s", directory, error)
                    break
                try:
                    stat_result = entry.stat(follow_symlinks=False)
                    if not include_hidden and _is_hidden_entry(entry, stat_result):
                        continue
                    if entry.is_symlink() or is_reparse_point(stat_result):
                        continue
                    if entry.is_dir(follow_symlinks=False):
                        if entry.name.lower() in PROTECTED_DIRECTORY_NAMES:
                            continue
                        identity = (stat_result.st_dev, stat_result.st_ino)
                        if stat_result.st_ino and identity in visited:
                            continue
                        visited.add(identity)
                        stack.append(entry.path)
                    elif entry.is_file(follow_symlinks=False):
                        yield Path(entry.path)
                except OSError as error:
                    logger.debug("iter_files skipped %s: %s", entry.path, error)


def scan_folder(
    root: str | os.PathLike[str],
    mode: str = FAST,
    *,
    include_hidden: bool = False,
    max_entries: int | None = None,
    should_cancel: Callable[[], bool] | None = None,
    on_progress: Callable[[ScanProgress], None] | None = None,
) -> ScanResult:
    """Walk ``root`` read-only and return a :class:`ScanResult`.

    ``max_entries`` defaults to :data:`DEFAULT_FAST_MAX_ENTRIES` for fast scans
    and to unlimited for full scans.  Full scans always include hidden items.
    This function never raises for filesystem problems; they are recorded in
    the result (``root_error`` for the starting folder itself).
    """
    started = time.monotonic()
    root_path = Path(root)
    full = mode == FULL
    result = ScanResult(mode=FULL if full else FAST, root=str(root_path))
    include_hidden = include_hidden or full
    if max_entries is None and not full:
        max_entries = DEFAULT_FAST_MAX_ENTRIES
    cancel = should_cancel or (lambda: False)

    try:
        root_is_dir = root_path.is_dir()
    except OSError as error:
        result.root_error = f"Cannot access folder: {error.strerror or error}"
        result.elapsed_seconds = time.monotonic() - started
        return result
    if not root_is_dir:
        result.root_error = "Folder does not exist or is not a folder."
        result.elapsed_seconds = time.monotonic() - started
        return result

    largest: list[tuple[int, str]] = []  # min-heap of (size, path)
    visited: set[tuple[int, int]] = set()
    try:
        root_stat = os.stat(root_path)
        if root_stat.st_ino:
            visited.add((root_stat.st_dev, root_stat.st_ino))
    except OSError:
        pass  # the walk below reports a real access problem
    stack: list[str] = [str(root_path)]
    entries_seen = 0
    last_report = 0.0
    current = str(root_path)

    def note_error(path: str, error: OSError) -> None:
        result.access_errors += 1
        if len(result.error_samples) < MAX_ERROR_SAMPLES:
            result.error_samples.append(f"{path}: {error.strerror or error.__class__.__name__}")
        logger.debug("Scan could not read %s: %s", path, error)

    def report(force: bool = False) -> None:
        nonlocal last_report
        if on_progress is None:
            return
        now = time.monotonic()
        if not force and now - last_report < PROGRESS_INTERVAL_SECONDS:
            return
        last_report = now
        on_progress(ScanProgress(
            result.files, result.folders, result.total_bytes,
            result.access_errors, current,
        ))

    while stack:
        if cancel():
            result.cancelled = True
            break
        directory = stack.pop()
        current = directory

        try:
            iterator = os.scandir(directory)
        except OSError as error:
            note_error(directory, error)
            continue

        with iterator:
            while True:
                try:
                    entry = next(iterator)
                except StopIteration:
                    break
                except OSError as error:
                    note_error(directory, error)
                    break

                entries_seen += 1
                if entries_seen % CANCEL_CHECK_EVERY == 0 and cancel():
                    result.cancelled = True
                    break
                if max_entries is not None and entries_seen > max_entries:
                    result.truncated = True
                    break

                try:
                    stat_result = entry.stat(follow_symlinks=False)
                except OSError as error:
                    note_error(entry.path, error)
                    continue

                if not include_hidden and _is_hidden_entry(entry, stat_result):
                    continue

                try:
                    is_link = entry.is_symlink() or is_reparse_point(stat_result)
                    is_dir = entry.is_dir(follow_symlinks=False)
                except OSError as error:
                    note_error(entry.path, error)
                    continue

                if is_link:
                    # Never follow, never count size: it is not a real file here.
                    result.skipped_links += 1
                    continue

                if is_dir:
                    if entry.name.lower() in PROTECTED_DIRECTORY_NAMES:
                        result.skipped_protected += 1
                        continue
                    identity = (stat_result.st_dev, stat_result.st_ino)
                    if stat_result.st_ino and identity in visited:
                        result.skipped_links += 1  # directory loop / bind mount
                        continue
                    visited.add(identity)
                    result.folders += 1
                    stack.append(entry.path)
                else:
                    result.files += 1
                    result.total_bytes += stat_result.st_size
                    if full:
                        category = category_for(Path(entry.name))
                        result.categories[category] = result.categories.get(category, 0) + 1
                        item = (stat_result.st_size, entry.path)
                        if len(largest) < LARGEST_FILES_KEPT:
                            heapq.heappush(largest, item)
                        elif item > largest[0]:
                            heapq.heapreplace(largest, item)

                report()

        if result.cancelled or result.truncated:
            break

    result.largest_files = sorted(largest, reverse=True)
    result.elapsed_seconds = time.monotonic() - started
    report(force=True)
    logger.info(result.summary_line())
    return result
