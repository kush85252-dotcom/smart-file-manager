"""Small, dependency-free helpers for safe JSON persistence."""

from __future__ import annotations

from contextlib import contextmanager
import json
import logging
import os
from pathlib import Path
import shutil
import threading
import time
from tempfile import NamedTemporaryFile
from typing import Any, Iterator

logger = logging.getLogger(__name__)

_LOCKS: dict[str, threading.RLock] = {}
_LOCKS_GUARD = threading.Lock()


@contextmanager
def _exclusive_lock(path: Path) -> Iterator[None]:
    """Serialize writes in this process and across processes where supported."""
    key = str(path.resolve(strict=False))
    with _LOCKS_GUARD:
        thread_lock = _LOCKS.setdefault(key, threading.RLock())

    with thread_lock:
        lock_path = path.with_name(f".{path.name}.lock")
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        with lock_path.open("a+b") as lock_file:
            if os.name == "nt":
                import msvcrt

                lock_file.seek(0, os.SEEK_END)
                if lock_file.tell() == 0:
                    lock_file.write(b"\0")
                    lock_file.flush()
                lock_file.seek(0)
                msvcrt.locking(lock_file.fileno(), msvcrt.LK_LOCK, 1)
                try:
                    yield
                finally:
                    lock_file.seek(0)
                    msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
                try:
                    yield
                finally:
                    fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def backup_file(path: Path, label: str = "corrupt") -> Path | None:
    """Keep a timestamped copy before recovering or replacing unreadable data."""
    path = Path(path)
    if not path.exists():
        return None
    stamp = time.strftime("%Y%m%d-%H%M%S")
    candidate = path.with_name(f"{path.name}.{label}-{stamp}")
    suffix = 1
    while candidate.exists():
        candidate = path.with_name(f"{path.name}.{label}-{stamp}-{suffix}")
        suffix += 1
    try:
        shutil.copy2(path, candidate)
        return candidate
    except OSError:
        logger.exception("Could not back up %s before recovery.", path)
        return None


def read_json(path: Path, default: Any) -> Any:
    """Read a complete JSON snapshot, backing up malformed text and recovering."""
    path = Path(path)
    try:
        with path.open("r", encoding="utf-8") as source:
            return json.load(source)
    except FileNotFoundError:
        return default
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        logger.warning("Could not read JSON data at %s: %s", path, error)
        backup_file(path)
        return default


def write_json(path: Path, data: Any) -> None:
    """Atomically replace a JSON document and serialize concurrent writers."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with _exclusive_lock(path):
        temporary_path: Path | None = None
        try:
            with NamedTemporaryFile(
                "w",
                encoding="utf-8",
                dir=path.parent,
                delete=False,
                prefix=f".{path.name}.",
                suffix=".tmp",
            ) as temporary:
                temporary_path = Path(temporary.name)
                json.dump(data, temporary, indent=2, ensure_ascii=False, allow_nan=False)
                temporary.write("\n")
                temporary.flush()
                os.fsync(temporary.fileno())
            os.replace(temporary_path, path)
            temporary_path = None
        finally:
            if temporary_path is not None:
                try:
                    temporary_path.unlink()
                except OSError:
                    logger.warning("Could not remove temporary JSON file %s.", temporary_path)
