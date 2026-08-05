"""
utils/helpers.py
================
Shared utility functions: file categorization, size formatting,
timestamp generation, and startup-shortcut creation.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

from utils.constants import FILE_CATEGORIES, OTHERS_CATEGORY


# ---------------------------------------------------------------------------
# FILE CATEGORIZATION
# ---------------------------------------------------------------------------

def get_category(filepath: Path) -> str:
    """
    Return the category name for a given file path.
    Checks each category's extension list in order.
    Falls back to OTHERS_CATEGORY if no match is found.
    """
    suffix = filepath.suffix.lower()  # e.g. ".mp3"

    # Special handling: catch multi-part extensions like .tar.gz
    name_lower = filepath.name.lower()
    for multi in [".tar.gz", ".tar.bz2", ".tar.xz"]:
        if name_lower.endswith(multi):
            return "Archives"

    for category, extensions in FILE_CATEGORIES.items():
        if suffix in extensions:
            return category

    return OTHERS_CATEGORY


# ---------------------------------------------------------------------------
# FORMATTING HELPERS
# ---------------------------------------------------------------------------

def format_size(size_bytes: int) -> str:
    """Convert a byte count into a human-readable string (B / KB / MB / GB)."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / 1024 ** 2:.1f} MB"
    else:
        return f"{size_bytes / 1024 ** 3:.1f} GB"


def timestamp() -> str:
    """Return the current time formatted for log messages."""
    return datetime.now().strftime("%H:%M:%S")


# ---------------------------------------------------------------------------
# PATH HELPERS
# ---------------------------------------------------------------------------

def get_base_path() -> str:
    """Return the application base directory (works for frozen executables too)."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def get_user_folder(folder_name: str) -> Path:
    """Return a Path to a named folder inside the user's home directory."""
    return Path.home() / folder_name


# ---------------------------------------------------------------------------
# WINDOWS STARTUP SHORTCUT
# ---------------------------------------------------------------------------

def add_to_startup() -> None:
    """
    Create a Windows startup shortcut so the application launches on login.
    Only works on Windows with pywin32 installed.
    """
    try:
        from win32com.client import Dispatch  # type: ignore[import]
    except ImportError:
        print("[WARN] pywin32 not available — cannot create startup shortcut.")
        return

    startup_folder = os.path.join(
        os.environ["APPDATA"],
        r"Microsoft\Windows\Start Menu\Programs\Startup",
    )

    exe_path = sys.executable
    shortcut_path = os.path.join(startup_folder, "SmartFileManager.lnk")

    shell = Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.Targetpath = exe_path
    shortcut.WorkingDirectory = os.path.dirname(exe_path)
    shortcut.save()

    print("Startup shortcut created!")
