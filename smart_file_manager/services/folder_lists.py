"""Pure helpers for the Favorites and Recent Folders lists.

These functions never touch the filesystem or Qt, so they are trivial to
test.  They take and return plain lists of path strings; persistence is the
job of :class:`smart_file_manager.config.AppConfig`.
"""

from __future__ import annotations

import os
from pathlib import Path


def path_key(path: str | os.PathLike[str]) -> str:
    """Return a comparison key so equivalent spellings count as duplicates.

    Uses ``normpath`` and ``normcase`` (case-insensitive on Windows).  It
    deliberately does not call ``resolve()``: that would touch the disk, hang
    on disconnected network drives, and follow symlinks.
    """
    return os.path.normcase(os.path.normpath(os.fspath(path)))


def add_favorite(favorites: list[str], path: str | os.PathLike[str], limit: int) -> tuple[list[str], bool]:
    """Append ``path`` unless it is already present.

    Returns ``(new_list, added)``.  The input list is not modified.
    """
    text = os.fspath(path)
    key = path_key(text)
    if any(path_key(existing) == key for existing in favorites):
        return list(favorites), False
    if len(favorites) >= limit:
        return list(favorites), False
    return [*favorites, text], True


def remove_favorite(favorites: list[str], path: str | os.PathLike[str]) -> tuple[list[str], bool]:
    """Remove ``path`` if present.  Returns ``(new_list, removed)``."""
    key = path_key(path)
    kept = [existing for existing in favorites if path_key(existing) != key]
    return kept, len(kept) != len(favorites)


def push_recent(recent: list[str], path: str | os.PathLike[str], limit: int) -> list[str]:
    """Put ``path`` at the top of the recent list.

    An existing equivalent entry is moved rather than duplicated, and the
    list is trimmed to ``limit`` entries (oldest dropped).
    """
    text = os.fspath(path)
    key = path_key(text)
    rest = [existing for existing in recent if path_key(existing) != key]
    return [text, *rest][: max(1, limit)]


def folder_exists(path: str | os.PathLike[str]) -> bool:
    """Return True if ``path`` is currently an accessible directory."""
    try:
        return Path(path).is_dir()
    except OSError:
        return False
