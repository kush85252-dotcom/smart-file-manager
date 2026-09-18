"""Primitive filesystem operations used by the UI and organizer."""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def open_file(path: Path) -> None:
    """Open a file with the platform's default application."""
    path = Path(path)

    if sys.platform.startswith("win"):
        os.startfile(str(path))
    elif sys.platform == "darwin":
        subprocess.run(["open", str(path)], check=True)
    else:
        subprocess.run(["xdg-open", str(path)], check=True)


def rename_path(path: Path, new_path: Path) -> None:
    """Rename a file or directory."""
    path.rename(new_path)


def delete_path(path: Path) -> None:
    """Delete a directory tree or a single file."""
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    else:
        path.unlink()


def move_path(source: Path, destination: Path) -> None:
    """Move a path without replacing an existing destination."""
    shutil.move(str(source), str(destination))


def available_destination(path: Path, marker: str = "") -> Path:
    """Return a non-existing path by appending a numeric suffix."""
    path = Path(path)

    if not path.exists():
        return path

    original_stem = path.stem
    suffix = path.suffix
    counter = 1

    while True:
        candidate = path.parent / f"{original_stem}{marker}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1
