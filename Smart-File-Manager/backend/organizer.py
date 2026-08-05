"""
backend/organizer.py
====================
FileOrganizer — core file-moving logic, completely independent of the GUI.
Communicates progress via callback functions so it can be used from any thread.
"""

import shutil
from pathlib import Path

from utils.constants import FILE_CATEGORIES, OTHERS_CATEGORY
from utils.helpers import get_category, timestamp


class FileOrganizer:
    """
    Handles all file-moving logic independently from the GUI.
    Emits progress via callback functions so it can be used from any thread.
    """

    def __init__(self, on_log=None, on_progress=None, on_done=None):
        """
        Parameters
        ----------
        on_log      : callable(str)        — receives a log message string
        on_progress : callable(int, int)   — receives (current, total) counts
        on_done     : callable(dict)       — receives the final report dict
        """
        self.on_log = on_log or (lambda msg: None)
        self.on_progress = on_progress or (lambda cur, tot: None)
        self.on_done = on_done or (lambda report: None)

    def scan_folder(self, folder: Path) -> list[Path]:
        """
        Return a flat list of all files directly inside *folder*
        (not recursive — only the immediate children).
        Skips hidden files and the category sub-folders themselves.
        """
        files = []
        try:
            category_names = set(FILE_CATEGORIES.keys()) | {OTHERS_CATEGORY}
            for entry in folder.iterdir():
                # Skip hidden files (start with dot)
                if entry.name.startswith("."):
                    continue
                # Skip if it's a sub-folder that we created
                if entry.is_dir() and entry.name in category_names:
                    continue
                # Only include files (not sub-directories)
                if entry.is_file():
                    files.append(entry)
        except PermissionError as exc:
            self.on_log(f"[ERROR] Cannot read {folder}: {exc}")
        return files

    def move_file(self, source: Path, destination_folder: Path) -> bool:
        """
        Move *source* into *destination_folder*, creating the folder if needed.
        If a file with the same name already exists, appends a counter suffix.
        Returns True on success, False on failure.
        """
        try:
            destination_folder.mkdir(parents=True, exist_ok=True)

            dest = destination_folder / source.name

            # Resolve name conflicts by appending _1, _2, … before the extension
            if dest.exists():
                stem = source.stem
                suffix = source.suffix
                counter = 1
                while dest.exists():
                    dest = destination_folder / f"{stem}_{counter}{suffix}"
                    counter += 1

            shutil.move(str(source), str(dest))
            return True

        except (PermissionError, OSError, shutil.Error) as exc:
            self.on_log(f"[ERROR] Could not move {source.name}: {exc}")
            return False

    def organize_folder(self, folder: Path) -> dict:
        """
        Scan *folder* and move every file into its category sub-folder.
        Returns a report dict: {category: count_moved, '_errors': count_errors}
        """
        self.on_log(f"[{timestamp()}] Scanning: {folder}")

        files = self.scan_folder(folder)
        total = len(files)
        report = {cat: 0 for cat in list(FILE_CATEGORIES.keys()) + [OTHERS_CATEGORY]}
        report["_errors"] = 0

        if total == 0:
            self.on_log(f"[{timestamp()}] No files found in {folder.name}.")
            self.on_done(report)
            return report

        self.on_log(f"[{timestamp()}] Found {total} file(s). Starting…")

        for index, file_path in enumerate(files, start=1):
            self.on_progress(index, total)

            category = get_category(file_path)
            destination = folder / category

            success = self.move_file(file_path, destination)
            if success:
                report[category] += 1
                self.on_log(f"[{timestamp()}] ✔  {file_path.name}  →  {category}/")
            else:
                report["_errors"] += 1

        self.on_log(f"[{timestamp()}] Done organizing {folder.name}.")
        self.on_done(report)
        return report

    def organize_folders(self, folders: list[Path]) -> dict:
        """
        Organize a list of folders in sequence.
        Merges all individual reports into one combined report.
        """
        combined = {cat: 0 for cat in list(FILE_CATEGORIES.keys()) + [OTHERS_CATEGORY]}
        combined["_errors"] = 0

        for folder in folders:
            single = self.organize_folder(folder)
            for key in combined:
                combined[key] += single.get(key, 0)

        return combined

    def move_single_file(self, source: Path) -> bool:
        """
        Move a single file into its category sub-folder inside its parent directory.
        Used by the auto-monitor after the debounce delay.
        """
        if not source.exists() or not source.is_file():
            return False  # File may have been deleted before we processed it

        category = get_category(source)
        destination = source.parent / category
        success = self.move_file(source, destination)

        if success:
            self.on_log(f"[{timestamp()}] [AUTO] ✔  {source.name}  →  {category}/")
        return success
