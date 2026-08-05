"""
utils/constants.py
==================
All application-wide constants: file category definitions, color palette,
and the global Qt stylesheet.
"""

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
# COLOR PALETTE  (dark professional theme)
# ---------------------------------------------------------------------------

COLORS = {
    "bg": "#1e1e2e",          # main background
    "surface": "#2a2a3e",     # card / panel background
    "border": "#3a3a5c",      # subtle borders
    "accent": "#7c6af7",      # primary purple accent
    "accent_hover": "#9b8fff",# lighter on hover
    "success": "#4ade80",     # green for success states
    "warning": "#facc15",     # yellow for warnings
    "danger": "#f87171",      # red for errors / stop
    "text": "#e2e8f0",        # primary text
    "text_muted": "#94a3b8",  # secondary / dim text
    "log_bg": "#13131f",      # log panel background
}


# ---------------------------------------------------------------------------
# GLOBAL QT STYLESHEET
# ---------------------------------------------------------------------------

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
