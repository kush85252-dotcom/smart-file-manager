"""Primitive filesystem operations used by the UI and organizer."""

import os
import errno
import shutil
import subprocess
import sys
import ctypes
from ctypes import wintypes
from pathlib import Path
from tempfile import NamedTemporaryFile


def open_file(path: Path) -> None:
    """Open a file with the platform's default application."""
    path = Path(path)

    if sys.platform.startswith("win"):
        os.startfile(str(path))
    elif sys.platform == "darwin":
        subprocess.run(["open", str(path)], check=True)
    else:
        subprocess.run(["xdg-open", str(path)], check=True)


def is_hidden(path: Path) -> bool:
    """Return whether a path is hidden on the current desktop platform."""
    path = Path(path)
    if path.name.startswith("."):
        return True
    if sys.platform.startswith("win"):
        attributes = ctypes.windll.kernel32.GetFileAttributesW(str(path))
        return attributes != -1 and bool(attributes & 0x2)
    return False


def rename_path(path: Path, new_path: Path) -> None:
    """Rename a file or directory."""
    path.rename(new_path)


def delete_path(path: Path, use_recycle_bin: bool = True) -> None:
    """Delete a path, preferring the native trash/recycle bin."""
    path = Path(path)
    if use_recycle_bin:
        send_to_recycle_bin(path)
        return
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    else:
        path.unlink()


def send_to_recycle_bin(path: Path) -> None:
    """Move a path to the platform's trash without adding dependencies."""
    path = Path(path).resolve()
    if sys.platform.startswith("win"):
        class SHFILEOPSTRUCTW(ctypes.Structure):
            _fields_ = [
                ("hwnd", wintypes.HWND),
                ("wFunc", wintypes.UINT),
                ("pFrom", wintypes.LPCWSTR),
                ("pTo", wintypes.LPCWSTR),
                ("fFlags", wintypes.UINT),
                ("fAnyOperationsAborted", wintypes.BOOL),
                ("hNameMappings", wintypes.LPVOID),
                ("lpszProgressTitle", wintypes.LPCWSTR),
            ]

        operation = SHFILEOPSTRUCTW(
            None, 3, str(path) + "\0", None, 0x0040, False, None, None
        )
        result = ctypes.windll.shell32.SHFileOperationW(ctypes.byref(operation))
        if result != 0 or operation.fAnyOperationsAborted:
            raise OSError(f"Windows recycle bin operation failed ({result}).")
        return

    for command in (["gio", "trash", str(path)], ["trash-put", str(path)]):
        if shutil.which(command[0]):
            subprocess.run(command, check=True)
            return
    raise OSError("No desktop trash utility is available; disable Recycle Bin in Settings.")


def move_path(source: Path, destination: Path) -> None:
    """Move a regular file without replacing an existing destination.

    Linking then unlinking gives same-volume moves an atomic no-overwrite step.
    Across volumes, copy to a temporary file and atomically publish it before
    removing the source.
    """
    source, destination = Path(source), Path(destination)
    if source.is_symlink():
        raise OSError(f"Refusing to move a symbolic link as a regular file: {source}")
    if not source.is_file():
        raise FileNotFoundError(f"Source file is unavailable: {source}")
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(f"Destination already exists: {destination}")
    if not destination.parent.is_dir():
        raise FileNotFoundError(f"Destination folder is unavailable: {destination.parent}")

    try:
        os.link(source, destination)
    except FileExistsError:
        raise
    except OSError as error:
        # Cross-volume links and some filesystems do not support hard links.
        if error.errno not in {
            errno.EXDEV,
            errno.EPERM,
            errno.EACCES,
            getattr(errno, "ENOTSUP", -1),
            getattr(errno, "EOPNOTSUPP", -1),
        }:
            raise
        temporary_path: Path | None = None
        try:
            with NamedTemporaryFile(
                "wb",
                dir=destination.parent,
                prefix=f".{destination.name}.",
                suffix=".moving",
                delete=False,
            ) as temporary:
                temporary_path = Path(temporary.name)
                with source.open("rb") as input_file:
                    shutil.copyfileobj(input_file, temporary, length=1024 * 1024)
                temporary.flush()
                os.fsync(temporary.fileno())
            shutil.copystat(source, temporary_path, follow_symlinks=False)
            # Publishing by hard link is atomic and still fails if a competing
            # writer created the destination after the initial check.
            os.link(temporary_path, destination)
        except Exception:
            raise
        finally:
            if temporary_path is not None:
                try:
                    temporary_path.unlink()
                except OSError:
                    pass

    try:
        source.unlink()
    except Exception:
        # Keep the operation from leaving two copies while reporting a failed move.
        try:
            destination.unlink()
        except OSError:
            pass
        raise


def available_destination(path: Path, marker: str = "") -> Path:
    """Return a non-existing path by appending a numeric suffix."""
    path = Path(path)

    if not path.exists() and not path.is_symlink():
        return path

    original_stem = path.stem
    suffix = path.suffix
    counter = 1

    while True:
        candidate = path.parent / f"{original_stem}{marker}_{counter}{suffix}"
        if not candidate.exists() and not candidate.is_symlink():
            return candidate
        counter += 1
