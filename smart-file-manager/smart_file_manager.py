"""
Smart File Manager
==================
A modern PyQt6 desktop application for organizing files into categories.

Features:
- Select multiple folders to organize
- Preview files before moving them
- Organize into Documents, Images, Videos, Audio, Archives,
  Applications, Android APKs, Scripts, Code, Others
- Auto Mode using watchdog to monitor folders in real time
- Live status log and move report
- Safe error handling — never crashes on bad files

Usage:
    python main.py
"""
import json
import os
import tkinter as tk
from tkinter import messagebox
import sys

with open("startup.json", "r") as f:
    settings = json.load(f)
print("JSON LOADED")
print(settings["app_settings"]["auto_mode"])
if settings["app_settings"]["auto_mode"]:
    current_folder = settings["folders"]["downloads"]
    print("AUTO MODE:", current_folder)
# Load config


with open("startup.json", "r") as f:
    settings = json.load(f)
print("TEST JSON")
app = settings["app_settings"]
folders = settings["folders"]

if app["auto_start"]:
    print("Smart File Manager starting automatically 😎")

if app["auto_mode"]:
    current_folder = folders["downloads"]
else:
    current_folder = folders["desktop"]

print("Opening:", current_folder)
print("JSON WORKS")
print(settings["app_settings"]["auto_mode"])
print(settings["folders"]["downloads"])
def open_folder(current_folder):
    os.startfile(current_folder)

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

base_path = get_base_path()
json_path = os.path.join(base_path, "startup.json")

print("LOADING JSON FROM:", json_path)
from pathlib import Path
files = os.listdir(settings["folders"]["downloads"])

print("Folder added:", settings["folders"]["downloads"])
print(files)
SETTINGS_PATH = Path("settings.json")

def load_settings():
    if SETTINGS_PATH.exists():
        with open(SETTINGS_PATH, "r") as file:
            return json.load(file)

    return {}


def save_settings(settings):
    with open(SETTINGS_PATH, "w") as file:
        json.dump(settings, file, indent=4)


settings = load_settings()


print("SETTINGS LOADED:")
print(settings)

theme = settings.get("app_settings", {}).get("theme", "dark")
print("Theme:", theme)
json_path = r"C:\Users\kush\OneDrive\Documents\smart_file_manager\startup.json"

print("Exists:", os.path.exists(json_path))
print("Folder exists:", os.path.exists(os.path.dirname(json_path)))

with open(json_path, "r") as f:
    data = f.read()

print("Loaded")
try:
    with open(json_path, "r", encoding="utf-8") as f:
        config = json.load(f)
except Exception as e:
    print("JSON LOAD FAILED:", e)
    raise

# Create window
root = tk.Tk()
root.title(config["appName"])
root.geometry("500x400")

title = tk.Label(root, text="📁 Smart File Manager", font=("Arial", 16))
title.pack(pady=10)

frame = tk.Frame(root)
frame.pack(fill="both", expand=True)

def open_folder(path):
    if os.path.exists(path):
        files = os.listdir(path)

        popup = tk.Toplevel(root)
        popup.title("Folder View")
        popup.geometry("400x300")

        label = tk.Label(popup, text=f"📂 {path}", font=("Arial", 12))
        label.pack(pady=10)

        for file in files:
            tk.Label(popup, text="📄 " + file).pack(anchor="w")
    else:
        messagebox.showerror("Error", "Folder not found!")

# Create buttons from JSON
for shortcut in config["shortcuts"]:
    btn = tk.Button(
        frame,
        text=shortcut["name"],
        width=30,
        command=lambda p=shortcut["path"]: open_folder(p)
    )
    command=lambda p=shortcut["path"]: open_folder(p)
    btn.pack(pady=5)

# root.mainloop()  # DISABLED TEMPORARILY (prevents blocking PyQt app)
import shutil
import time
import threading
from datetime import datetime
from win32com.client import Dispatch
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QFileDialog,
    QTreeWidget,
    QTreeWidgetItem,
    QTextEdit,
    QSplitter,
    QGroupBox,
    QProgressBar,
    QMessageBox,
    QTabWidget,
    QHeaderView,
    QFrame,
    QScrollArea,
    QStatusBar,
    QCheckBox,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QIcon, QFont, QColor, QPalette, QTextCursor

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
def add_to_startup():
    print("Startup")
# ---------------------------------------------------------------------------
# FILE CATEGORY DEFINITIONS
# ---------------------------------------------------------------------------

# Maps each category name to the file extensions that belong to it.
# Extensions must be lowercase and include the leading dot.
FILE_CATEGORIES = {
    "Documents": [
        ".pdf",
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
        ".ppt",
        ".pptx",
        ".txt",
        ".rtf",
        ".odt",
        ".ods",
        ".odp",
        ".csv",
        ".md",
        ".epub",
        ".djvu",
        ".pages",
        ".numbers",
        ".key",
        ".tex",
        ".wps",
    ],
    "Images": [
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".svg",
        ".webp",
        ".tiff",
        ".tif",
        ".ico",
        ".heic",
        ".heif",
        ".raw",
        ".cr2",
        ".nef",
        ".arw",
        ".psd",
        ".ai",
        ".xcf",
        ".jfif",
    ],
    "Videos": [
        ".mp4",
        ".mkv",
        ".avi",
        ".mov",
        ".wmv",
        ".flv",
        ".webm",
        ".m4v",
        ".mpeg",
        ".mpg",
        ".3gp",
        ".rmvb",
        ".ts",
        ".vob",
        ".ogv",
    ],
    "Audio": [
        ".mp3",
        ".wav",
        ".flac",
        ".aac",
        ".ogg",
        ".wma",
        ".m4a",
        ".opus",
        ".aiff",
        ".ape",
        ".mid",
        ".midi",
        ".amr",
    ],
    "Archives": [
        ".zip",
        ".rar",
        ".7z",
        ".tar",
        ".gz",
        ".bz2",
        ".xz",
        ".tar.gz",
        ".tar.bz2",
        ".tar.xz",
        ".tgz",
        ".tbz2",
        ".cab",
        ".iso",
        ".dmg",
        ".deb",
        ".rpm",
    ],
    "Applications": [
        ".exe",
        ".msi",
        ".app",
        ".dmg",
        ".pkg",
        ".msix",
        ".run",
        ".bin",
        ".jar",
        ".appimage",
    ],
    "Android APKs": [
        ".apk",
        ".aab",
        ".xapk",
    ],
    "Scripts": [
        ".sh",
        ".bash",
        ".zsh",
        ".fish",
        ".ps1",
        ".psm1",
        ".bat",
        ".cmd",
        ".vbs",
        ".awk",
        ".sed",
    ],
    "Code": [
        ".py",
        ".js",
        ".ts",
        ".jsx",
        ".tsx",
        ".html",
        ".htm",
        ".css",
        ".scss",
        ".sass",
        ".less",
        ".json",
        ".xml",
        ".yaml",
        ".yml",
        ".toml",
        ".ini",
        ".cfg",
        ".conf",
        ".c",
        ".cpp",
        ".h",
        ".hpp",
        ".java",
        ".kt",
        ".swift",
        ".go",
        ".rs",
        ".php",
        ".rb",
        ".pl",
        ".lua",
        ".r",
        ".m",
        ".vue",
        ".dart",
        ".cs",
        ".vb",
        ".f90",
        ".sql",
        ".graphql",
        ".proto",
    ],
}

# Files whose extension does not match any category go here.
OTHERS_CATEGORY = "Others"


# ---------------------------------------------------------------------------
# UTILITY FUNCTIONS
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
def add_to_startup():
    startup_folder = os.path.join(
        os.environ["APPDATA"],
        r"Microsoft\Windows\Start Menu\Programs\Startup"
    )

    exe_path = sys.executable

    shortcut_path = os.path.join(
        startup_folder,
        "SmartFileManager.lnk"
    )

    shell = Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.Targetpath = exe_path
    shortcut.WorkingDirectory = os.path.dirname(exe_path)
    shortcut.save()

    print("Startup shortcut created!")\

def format_size(size_bytes: int) -> str:
    """Convert a byte count into a human-readable string (KB / MB / GB)."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024**2:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024**3:
        return f"{size_bytes / 1024**2:.1f} MB"
    else:
        return f"{size_bytes / 1024**3:.1f} GB"


def timestamp() -> str:
    """Return the current time formatted for log messages."""
    return datetime.now().strftime("%H:%M:%S")


# ---------------------------------------------------------------------------
# FILE ORGANIZER (core logic, no Qt)
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# WORKER THREAD — runs organize in background so the GUI stays responsive
# ---------------------------------------------------------------------------


class OrganizerWorker(QThread):
    """
    Runs FileOrganizer.organize_folders() on a background thread.
    Communicates with the main thread via Qt signals.
    """

    # Emitted for each log line
    log_signal = pyqtSignal(str)
    # Emitted as files are processed (current, total)
    progress_signal = pyqtSignal(int, int)
    # Emitted when all folders are done; carries the merged report dict
    done_signal = pyqtSignal(dict)

    def __init__(self, folders: list[Path], parent=None):
        super().__init__(parent)
        self.folders = folders

    def run(self):
        """Entry point for the background thread."""
        organizer = FileOrganizer(
            on_log=self.log_signal.emit,
            on_progress=self.progress_signal.emit,
            on_done=lambda report: None,  # we emit done_signal after all folders
        )
        combined = organizer.organize_folders(self.folders)
        self.done_signal.emit(combined)


# ---------------------------------------------------------------------------
# WATCHDOG EVENT HANDLER — detects new files and queues them for moving
# ---------------------------------------------------------------------------


class FolderWatcher(FileSystemEventHandler):
    """
    Watchdog event handler.
    When a new file appears in a monitored folder, waits DEBOUNCE_SECONDS
    before moving it (so partial downloads / in-progress writes finish first).
    """

    DEBOUNCE_SECONDS = 5  # seconds to wait before moving a newly detected file

    def __init__(self, on_log, organizer: FileOrganizer):
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


# ---------------------------------------------------------------------------
# PREVIEW TREE BUILDER — scans folders and populates a QTreeWidget
# ---------------------------------------------------------------------------


class PreviewScanner(QThread):
    """
    Background thread that scans the selected folders and emits
    (file_path, category, size) tuples for the preview tree.
    """

    item_found = pyqtSignal(str, str, str, str)  # folder, name, category, size
    done_signal = pyqtSignal(int)  # total file count

    def __init__(self, folders: list[Path], parent=None):
        super().__init__(parent)
        self.folders = folders

    def run(self):
        total = 0
        for folder in self.folders:
            organizer = FileOrganizer()  # callbacks not needed here
            files = organizer.scan_folder(folder)
            for f in files:
                category = get_category(f)
                try:
                    size = format_size(f.stat().st_size)
                except OSError:
                    size = "?"
                self.item_found.emit(str(folder), f.name, category, size)
                total += 1
        self.done_signal.emit(total)


# ---------------------------------------------------------------------------
# MAIN WINDOW
# ---------------------------------------------------------------------------

# Color palette (dark professional theme)
COLORS = {
    "bg": "#1e1e2e",  # main background
    "surface": "#2a2a3e",  # card / panel background
    "border": "#3a3a5c",  # subtle borders
    "accent": "#7c6af7",  # primary purple accent
    "accent_hover": "#9b8fff",  # lighter on hover
    "success": "#4ade80",  # green for success states
    "warning": "#facc15",  # yellow for warnings
    "danger": "#f87171",  # red for errors / stop
    "text": "#e2e8f0",  # primary text
    "text_muted": "#94a3b8",  # secondary / dim text
    "log_bg": "#13131f",  # log panel background
}


STYLESHEET = f"""
/* ── Global ─────────────────────────────────────────────── */
QMainWindow, QWidget {{
    background-color: {COLORS["bg"]};
    color: {COLORS["text"]};
    font-family: 'Segoe UI', 'Inter', 'Arial', sans-serif;
    font-size: 13px;
}}

/* ── Group boxes ─────────────────────────────────────────── */
QGroupBox {{
    border: 1px solid {COLORS["border"]};
    border-radius: 8px;
    margin-top: 10px;
    padding: 10px 8px 8px 8px;
    background-color: {COLORS["surface"]};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    top: -6px;
    padding: 0 4px;
    color: {COLORS["accent"]};
    font-weight: 600;
    font-size: 13px;
}}

/* ── Buttons ─────────────────────────────────────────────── */
QPushButton {{
    background-color: {COLORS["accent"]};
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
    font-size: 13px;
}}
QPushButton:hover {{
    background-color: {COLORS["accent_hover"]};
}}
QPushButton:pressed {{
    background-color: #5a4ed4;
}}
QPushButton:disabled {{
    background-color: {COLORS["border"]};
    color: {COLORS["text_muted"]};
}}

QPushButton#btn_danger {{
    background-color: {COLORS["danger"]};
}}
QPushButton#btn_danger:hover {{
    background-color: #ff8a8a;
}}

QPushButton#btn_success {{
    background-color: {COLORS["success"]};
    color: #0f1f0f;
}}
QPushButton#btn_success:hover {{
    background-color: #6ef09f;
}}

QPushButton#btn_secondary {{
    background-color: {COLORS["surface"]};
    border: 1px solid {COLORS["border"]};
    color: {COLORS["text"]};
}}
QPushButton#btn_secondary:hover {{
    background-color: {COLORS["border"]};
}}

/* ── List widgets ────────────────────────────────────────── */
QListWidget {{
    background-color: {COLORS["log_bg"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 6px;
    padding: 4px;
    color: {COLORS["text"]};
}}
QListWidget::item {{
    padding: 6px 8px;
    border-radius: 4px;
}}
QListWidget::item:selected {{
    background-color: {COLORS["accent"]};
    color: white;
}}
QListWidget::item:hover:!selected {{
    background-color: {COLORS["border"]};
}}

/* ── Tree widget ─────────────────────────────────────────── */
QTreeWidget {{
    background-color: {COLORS["log_bg"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 6px;
    color: {COLORS["text"]};
    alternate-background-color: {COLORS["surface"]};
}}
QTreeWidget::item {{
    padding: 4px 4px;
}}
QTreeWidget::item:selected {{
    background-color: {COLORS["accent"]};
    color: white;
}}
QHeaderView::section {{
    background-color: {COLORS["surface"]};
    color: {COLORS["text_muted"]};
    border: none;
    border-bottom: 1px solid {COLORS["border"]};
    padding: 6px 8px;
    font-weight: 600;
}}

/* ── Text area (log) ─────────────────────────────────────── */
QTextEdit {{
    background-color: {COLORS["log_bg"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 6px;
    padding: 6px;
    color: {COLORS["text"]};
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
}}

/* ── Progress bar ────────────────────────────────────────── */
QProgressBar {{
    border: 1px solid {COLORS["border"]};
    border-radius: 6px;
    background-color: {COLORS["log_bg"]};
    text-align: center;
    color: {COLORS["text"]};
    height: 20px;
}}
QProgressBar::chunk {{
    background-color: {COLORS["accent"]};
    border-radius: 5px;
}}

/* ── Tabs ────────────────────────────────────────────────── */
QTabWidget::pane {{
    border: 1px solid {COLORS["border"]};
    border-radius: 6px;
    background-color: {COLORS["surface"]};
}}
QTabBar::tab {{
    background-color: {COLORS["surface"]};
    color: {COLORS["text_muted"]};
    border: 1px solid {COLORS["border"]};
    border-bottom: none;
    border-radius: 6px 6px 0 0;
    padding: 8px 18px;
    margin-right: 3px;
    font-weight: 500;
}}
QTabBar::tab:selected {{
    background-color: {COLORS["accent"]};
    color: white;
    font-weight: 700;
}}
QTabBar::tab:hover:!selected {{
    background-color: {COLORS["border"]};
    color: {COLORS["text"]};
}}

/* ── Scroll bars ─────────────────────────────────────────── */
QScrollBar:vertical {{
    background-color: {COLORS["bg"]};
    width: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background-color: {COLORS["border"]};
    border-radius: 4px;
    min-height: 20px;
}}
QScrollBar::handle:vertical:hover {{
    background-color: {COLORS["accent"]};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background-color: {COLORS["bg"]};
    height: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:horizontal {{
    background-color: {COLORS["border"]};
    border-radius: 4px;
    min-width: 20px;
}}

/* ── Status bar ──────────────────────────────────────────── */
QStatusBar {{
    background-color: {COLORS["surface"]};
    color: {COLORS["text_muted"]};
    border-top: 1px solid {COLORS["border"]};
}}

/* ── Separator ───────────────────────────────────────────── */
QFrame[frameShape="4"],   /* HLine */
QFrame[frameShape="5"] {{ /* VLine */
    color: {COLORS["border"]};
}}
"""


class MainWindow(QMainWindow):
    """
    The application's main window.
    Hosts all panels: folder list, preview, log, report, and auto-mode controls.
    """

    # Qt signals used by background threads to update the GUI safely
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int, int)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart File Manager")
        self.setMinimumSize(1100, 700)
        self.resize(1280, 800)

        # State
        self._selected_folders: list[Path] = []
        self._organizer_worker: OrganizerWorker | None = None
        self._preview_scanner: PreviewScanner | None = None
        self._observer: Observer | None = None  # watchdog observer
        self._watcher: FolderWatcher | None = None  # our event handler
        self._auto_mode_active = False

        # Connect our own signals (used by background threads)
        self.log_signal.connect(self._append_log)
        self.progress_signal.connect(self._update_progress)

        self._build_ui()
        self._set_initial_state()

    # ── UI Construction ──────────────────────────────────────────────────────

    def _build_ui(self):
        """Assemble all widgets and layouts."""
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(12, 12, 12, 8)
        root_layout.setSpacing(8)

        # Header
        root_layout.addWidget(self._build_header())

        # Main splitter: left panel | right tabs
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(6)
        splitter.addWidget(self._build_left_panel())
        splitter.addWidget(self._build_right_panel())
        splitter.setSizes([340, 900])
        root_layout.addWidget(splitter, stretch=1)

        # Bottom bar: progress + status
        root_layout.addWidget(self._build_bottom_bar())

        # Status bar (window footer)
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
        self._status_bar.showMessage("Ready — add folders to get started.")

    def _build_header(self) -> QWidget:
        """Top banner with title and action buttons."""
        frame = QFrame()
        frame.setStyleSheet(
            f"background-color: {COLORS['surface']};"
            f"border: 1px solid {COLORS['border']};"
            f"border-radius: 8px;"
        )
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(16, 10, 16, 10)

        # App name
        title = QLabel("Smart File Manager")
        title.setStyleSheet(
            f"font-size: 20px; font-weight: 700; color: {COLORS['accent']};"
            "border: none; background: transparent;"
        )
        subtitle = QLabel("Organize your files automatically")
        subtitle.setStyleSheet(
            f"font-size: 12px; color: {COLORS['text_muted']};"
            "border: none; background: transparent;"
        )

        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        title_col.addWidget(title)
        title_col.addWidget(subtitle)
        layout.addLayout(title_col)
        layout.addStretch()

        # Action buttons
        self.btn_add_folder = QPushButton("＋  Add Folder")
        self.btn_remove_folder = QPushButton("－  Remove")
        self.btn_preview = QPushButton("🔍  Preview")
        self.btn_organize = QPushButton("▶  Organize Now")
        self.btn_clear_log = QPushButton("🗑  Clear Log")

        self.btn_remove_folder.setObjectName("btn_secondary")
        self.btn_clear_log.setObjectName("btn_secondary")
        self.btn_organize.setObjectName("btn_success")

        for btn in (
            self.btn_add_folder,
            self.btn_remove_folder,
            self.btn_preview,
            self.btn_organize,
            self.btn_clear_log,
        ):
            layout.addWidget(btn)

        # Connect
        self.btn_add_folder.clicked.connect(self._add_folders)
        self.btn_remove_folder.clicked.connect(self._remove_selected_folder)
        self.btn_preview.clicked.connect(self._run_preview)
        self.btn_organize.clicked.connect(self._run_organize)
        self.btn_clear_log.clicked.connect(self._clear_log)

        return frame

    def _build_left_panel(self) -> QGroupBox:
        """Left panel: selected folders list + auto-mode controls."""
        group = QGroupBox("Selected Folders")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)

        # Folder list
        self.folder_list = QListWidget()
        self.folder_list.setToolTip("Folders to organize")
        layout.addWidget(self.folder_list, stretch=1)

        # Auto-mode group
        auto_group = QGroupBox("Auto Mode  (Watchdog)")
        auto_layout = QVBoxLayout(auto_group)
        auto_layout.setSpacing(6)

        info_lbl = QLabel(
            f"Monitors selected folders for new files.\n"
            f"Waits {FolderWatcher.DEBOUNCE_SECONDS}s before moving them."
        )
        info_lbl.setStyleSheet(
            f"color: {COLORS['text_muted']}; font-size: 11px; border: none; background: transparent;"
        )
        info_lbl.setWordWrap(True)
        auto_layout.addWidget(info_lbl)

        self.btn_start_auto = QPushButton("▶  Start Auto Mode")
        self.btn_stop_auto = QPushButton("■  Stop Auto Mode")
        self.btn_stop_auto.setObjectName("btn_danger")

        self.btn_start_auto.clicked.connect(self._start_auto_mode)
        self.btn_stop_auto.clicked.connect(self._stop_auto_mode)

        auto_layout.addWidget(self.btn_start_auto)
        auto_layout.addWidget(self.btn_stop_auto)

        # Auto-mode status indicator
        self.auto_status_lbl = QLabel("● Inactive")
        self.auto_status_lbl.setStyleSheet(
            f"color: {COLORS['text_muted']}; font-weight: 600; border: none; background: transparent;"
        )
        auto_layout.addWidget(self.auto_status_lbl)

        layout.addWidget(auto_group)
        return group

    def _build_right_panel(self) -> QTabWidget:
        """Right panel: tabbed view for Preview, Log, and Report."""
        self.tabs = QTabWidget()

        self.tabs.addTab(self._build_preview_tab(), "📁  Preview")
        self.tabs.addTab(self._build_log_tab(), "📋  Activity Log")
        self.tabs.addTab(self._build_report_tab(), "📊  Report")

        return self.tabs

    def _build_preview_tab(self) -> QWidget:
        """Preview tab: shows files and their target categories before organizing."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)

        hint = QLabel(
            "Click  🔍 Preview  to scan your selected folders and see "
            "where each file will be moved before you start organizing."
        )
        hint.setWordWrap(True)
        hint.setStyleSheet(
            f"color: {COLORS['text_muted']}; font-size: 12px;"
            f"border: 1px solid {COLORS['border']}; border-radius: 6px;"
            f"background: {COLORS['surface']}; padding: 8px;"
        )
        layout.addWidget(hint)

        # Tree columns: Folder | File Name | Category | Size
        self.preview_tree = QTreeWidget()
        self.preview_tree.setHeaderLabels(["Folder", "File Name", "Category", "Size"])
        self.preview_tree.setAlternatingRowColors(True)
        self.preview_tree.setSortingEnabled(True)
        header = self.preview_tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        self.preview_tree.setColumnWidth(0, 180)
        self.preview_tree.setColumnWidth(2, 120)
        self.preview_tree.setColumnWidth(3, 80)
        layout.addWidget(self.preview_tree, stretch=1)

        self.preview_count_lbl = QLabel("No preview loaded.")
        self.preview_count_lbl.setStyleSheet(
            f"color: {COLORS['text_muted']}; font-size: 12px;"
        )
        layout.addWidget(self.preview_count_lbl)

        return widget

    def _build_log_tab(self) -> QWidget:
        """Log tab: scrollable text area showing all actions in real time."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setPlaceholderText("Activity log will appear here…")
        layout.addWidget(self.log_text)

        return widget

    def _build_report_tab(self) -> QWidget:
        """Report tab: shows a summary after organizing is complete."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)

        self.report_tree = QTreeWidget()
        self.report_tree.setHeaderLabels(["Category", "Files Moved"])
        self.report_tree.setAlternatingRowColors(True)
        header = self.report_tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.report_tree.setColumnWidth(1, 120)
        layout.addWidget(self.report_tree, stretch=1)

        self.report_summary_lbl = QLabel(
            "No report yet — run Organize to generate one."
        )
        self.report_summary_lbl.setStyleSheet(
            f"color: {COLORS['text_muted']}; font-size: 12px;"
        )
        layout.addWidget(self.report_summary_lbl)

        return widget

    def _build_bottom_bar(self) -> QWidget:
        """Bottom bar with progress bar and current-operation label."""
        frame = QFrame()
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(0, 4, 0, 0)
        layout.setSpacing(10)

        self.progress_label = QLabel("Idle")
        self.progress_label.setStyleSheet(
            f"color: {COLORS['text_muted']}; font-size: 12px;"
        )
        self.progress_label.setFixedWidth(220)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%v / %m files")

        layout.addWidget(self.progress_label)
        layout.addWidget(self.progress_bar, stretch=1)

        return frame

    # ── Initial State ────────────────────────────────────────────────────────

    def _set_initial_state(self):
        """Disable buttons that require folders or that must not run concurrently."""
        self.btn_remove_folder.setEnabled(False)
        self.btn_preview.setEnabled(False)
        self.btn_organize.setEnabled(False)
        self.btn_stop_auto.setEnabled(False)
        self.btn_start_auto.setEnabled(False)

    def _refresh_button_states(self):
        """Enable / disable buttons based on current application state."""
        has_folders = bool(self._selected_folders)
        is_busy = (
            self._organizer_worker is not None and self._organizer_worker.isRunning()
        )
        auto_active = self._auto_mode_active
        has_selected = bool(self.folder_list.selectedItems())

        self.btn_add_folder.setEnabled(not is_busy)
        self.btn_remove_folder.setEnabled(
            has_folders and has_selected and not is_busy and not auto_active
        )
        self.btn_preview.setEnabled(has_folders and not is_busy and not auto_active)
        self.btn_organize.setEnabled(has_folders and not is_busy and not auto_active)
        self.btn_start_auto.setEnabled(has_folders and not auto_active and not is_busy)
        self.btn_stop_auto.setEnabled(auto_active)

    # ── Folder Management ────────────────────────────────────────────────────

    def _add_folders(self):

        """Open a dialog to choose one folder; can call multiple times."""
        
        folder_str = QFileDialog.getExistingDirectory(
            self, "Select Folder to Organize", str(Path.home())
        )
        if not folder_str:
            return  # User cancelled

        folder = Path(folder_str)

        # Avoid duplicates
        if folder in self._selected_folders:
            self._status_bar.showMessage(f"Folder already added: {folder}")
            return

        self._selected_folders.append(folder)

        # Show only the folder name in the list; full path in tooltip
        item = QListWidgetItem(folder.name)
        item.setToolTip(str(folder))
        item.setData(Qt.ItemDataRole.UserRole, folder)
        self.folder_list.addItem(item)

        self._append_log(f"[{timestamp()}] Added folder: {folder}")
        self._status_bar.showMessage(f"Added: {folder}")
        self._refresh_button_states()

    def _remove_selected_folder(self):
        """Remove the currently highlighted folder from the list."""
        items = self.folder_list.selectedItems()
        if not items:
            return
        for item in items:
            folder = item.data(Qt.ItemDataRole.UserRole)
            self._selected_folders.remove(folder)
            self.folder_list.takeItem(self.folder_list.row(item))
            self._append_log(f"[{timestamp()}] Removed folder: {folder}")
        self._refresh_button_states()

    # ── Preview ──────────────────────────────────────────────────────────────

    def _run_preview(self):
        """Scan selected folders in the background and populate the preview tree."""
        if not self._selected_folders:
            return

        self.preview_tree.clear()
        self.preview_count_lbl.setText("Scanning…")
        self.btn_preview.setEnabled(False)
        self.tabs.setCurrentIndex(0)  # Switch to Preview tab

        self._preview_scanner = PreviewScanner(self._selected_folders, parent=self)
        self._preview_scanner.item_found.connect(self._add_preview_item)
        self._preview_scanner.done_signal.connect(self._preview_done)
        self._preview_scanner.start()

    def _add_preview_item(self, folder: str, name: str, category: str, size: str):
        """Slot: add one row to the preview tree (called from scanner thread via signal)."""
        item = QTreeWidgetItem([Path(folder).name, name, category, size])
        item.setToolTip(0, folder)

        # Color-code the category column
        cat_colors = {
            "Documents": "#60a5fa",
            "Images": "#f472b6",
            "Videos": "#fb923c",
            "Audio": "#a78bfa",
            "Archives": "#facc15",
            "Applications": "#f87171",
            "Android APKs": "#4ade80",
            "Scripts": "#67e8f9",
            "Code": "#86efac",
            "Others": "#94a3b8",
        }
        color = cat_colors.get(category, COLORS["text_muted"])
        item.setForeground(2, QColor(color))

        self.preview_tree.addTopLevelItem(item)

    def _preview_done(self, total: int):
        """Slot: called when the preview scanner finishes."""
        self.preview_count_lbl.setText(f"Preview complete — {total} file(s) found.")
        self._status_bar.showMessage(f"Preview: {total} file(s) ready to organize.")
        self._refresh_button_states()

    # ── Organize ─────────────────────────────────────────────────────────────

    def _run_organize(self):
        """Start the organizer worker thread."""
        if not self._selected_folders:
            return

        # Confirm with user
        reply = QMessageBox.question(
            self,
            "Confirm Organize",
            f"This will move files in {len(self._selected_folders)} folder(s).\n"
            "Are you sure you want to continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        # Reset progress
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(1)  # Will be updated as files are counted
        self.progress_label.setText("Organizing…")
        self._append_log(f"\n[{timestamp()}] ═══ Starting organization ═══")

        # Launch worker
        self._organizer_worker = OrganizerWorker(
            list(self._selected_folders), parent=self
        )
        self._organizer_worker.log_signal.connect(self._append_log)
        self._organizer_worker.progress_signal.connect(self._update_progress)
        self._organizer_worker.done_signal.connect(self._organize_done)
        self._organizer_worker.start()

        self.tabs.setCurrentIndex(1)  # Switch to log tab
        self._refresh_button_states()

    def _update_progress(self, current: int, total: int):
        """Update the progress bar (called from worker thread via signal)."""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.progress_label.setText(f"Moving file {current} of {total}…")

    def _organize_done(self, report: dict):
        """Slot: called when the organizer worker finishes."""
        self.progress_label.setText("Done!")
        self._status_bar.showMessage("Organization complete.")
        self._append_log(f"[{timestamp()}] ═══ Organization complete ═══\n")
        self._show_report(report)
        self.tabs.setCurrentIndex(2)  # Switch to report tab
        self._refresh_button_states()

    # ── Report ───────────────────────────────────────────────────────────────

    def _show_report(self, report: dict):
        """Populate the Report tab with results from the organizer."""
        self.report_tree.clear()

        total_moved = 0
        errors = report.get("_errors", 0)

        # All categories in display order
        display_categories = list(FILE_CATEGORIES.keys()) + [OTHERS_CATEGORY]

        for category in display_categories:
            count = report.get(category, 0)
            if count == 0:
                continue
            item = QTreeWidgetItem([category, str(count)])
            item.setTextAlignment(
                1, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
            self.report_tree.addTopLevelItem(item)
            total_moved += count

        # Totals row
        total_item = QTreeWidgetItem(["TOTAL MOVED", str(total_moved)])
        total_item.setFont(0, QFont("Segoe UI", 13, QFont.Weight.Bold))
        total_item.setFont(1, QFont("Segoe UI", 13, QFont.Weight.Bold))
        total_item.setForeground(0, QColor(COLORS["success"]))
        total_item.setForeground(1, QColor(COLORS["success"]))
        self.report_tree.addTopLevelItem(total_item)

        if errors:
            err_item = QTreeWidgetItem(["Errors (not moved)", str(errors)])
            err_item.setForeground(0, QColor(COLORS["danger"]))
            err_item.setForeground(1, QColor(COLORS["danger"]))
            self.report_tree.addTopLevelItem(err_item)

        summary = f"Moved {total_moved} file(s)"
        if errors:
            summary += f"  |  {errors} error(s)"
        self.report_summary_lbl.setText(summary)

    # ── Auto Mode ────────────────────────────────────────────────────────────

    def _start_auto_mode(self):
        """Start watchdog observers for all selected folders."""
        if not self._selected_folders:
            return
        if self._auto_mode_active:
            return

        # Build a shared FileOrganizer that logs via our signal
        organizer = FileOrganizer(
            on_log=lambda msg: self.log_signal.emit(msg),
        )

        self._watcher = FolderWatcher(
            on_log=lambda msg: self.log_signal.emit(msg),
            organizer=organizer,
        )

        self._observer = Observer()
        for folder in self._selected_folders:
            try:
                self._observer.schedule(self._watcher, str(folder), recursive=False)
                self._append_log(f"[{timestamp()}] [AUTO] Watching: {folder}")
            except Exception as exc:
                self._append_log(f"[ERROR] Cannot watch {folder}: {exc}")

        self._observer.start()
        self._auto_mode_active = True

        self.auto_status_lbl.setText("● Active")
        self.auto_status_lbl.setStyleSheet(
            f"color: {COLORS['success']}; font-weight: 600; border: none; background: transparent;"
        )
        self._status_bar.showMessage(
            "Auto Mode active — monitoring folders for new files."
        )
        self.tabs.setCurrentIndex(1)  # Show log tab
        self._refresh_button_states()

    def _stop_auto_mode(self):
        """Stop watchdog and cancel all pending timers."""
        if not self._auto_mode_active:
            return

        # Cancel any pending move timers
        if self._watcher:
            self._watcher.cancel_all()
            self._watcher = None

        # Stop the watchdog observer
        if self._observer:
            self._observer.stop()
            self._observer.join(timeout=3)
            self._observer = None

        self._auto_mode_active = False

        self.auto_status_lbl.setText("● Inactive")
        self.auto_status_lbl.setStyleSheet(
            f"color: {COLORS['text_muted']}; font-weight: 600; border: none; background: transparent;"
        )
        self._append_log(f"[{timestamp()}] [AUTO] Stopped monitoring.")
        self._status_bar.showMessage("Auto Mode stopped.")
        self._refresh_button_states()

    # ── Log Helpers ──────────────────────────────────────────────────────────

    def _append_log(self, message: str):
        """
        Append a line to the log text area.
        Color-codes lines that contain keywords for quick scanning.
        Safe to call from any thread (connected via Qt signal).
        """
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        # Choose color based on content
        if "[ERROR]" in message:
            color = COLORS["danger"]
        elif "[AUTO]" in message:
            color = COLORS["warning"]
        elif "═══" in message:
            color = COLORS["accent"]
        elif "✔" in message:
            color = COLORS["success"]
        else:
            color = COLORS["text"]

        html = (
            f'<span style="color:{color};">'
            f"{message.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')}"
            f"</span><br>"
        )
        cursor.insertHtml(html)

        # Auto-scroll to the bottom
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )

    def _clear_log(self):
        """Clear the activity log."""
        self.log_text.clear()

    # ── Close Event ──────────────────────────────────────────────────────────

    def closeEvent(self, event):
        """Ensure background threads are stopped before the window closes."""
        # Stop auto mode first (cancels timers, stops observer)
        if self._auto_mode_active:
            self._stop_auto_mode()

        # Wait for organizer worker if running
        if self._organizer_worker and self._organizer_worker.isRunning():
            self._organizer_worker.quit()
            self._organizer_worker.wait(3000)

        # Wait for preview scanner if running
        if self._preview_scanner and self._preview_scanner.isRunning():
            self._preview_scanner.quit()
            self._preview_scanner.wait(3000)

        event.accept()


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------


def main():
    """Create the QApplication and show the main window."""
    app = QApplication(sys.argv)
    app.setApplicationName("Smart File Manager")
    app.setApplicationVersion("1.0.0")

    # Apply our dark stylesheet globally
    app.setStyleSheet (STYLESHEET)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()