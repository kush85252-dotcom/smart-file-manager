"""File extension categorization rules."""

from pathlib import Path

CATEGORIES = {
    "Images": {
        ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp",
        ".svg", ".ico", ".tiff", ".tif"
    },
    "Videos": {
        ".mp4", ".mkv", ".avi", ".mov", ".webm", ".wmv",
        ".flv", ".m4v"
    },
    "Audio": {
        ".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"
    },
    "Documents": {
        ".txt", ".pdf", ".doc", ".docx", ".odt", ".rtf"
    },
    "Spreadsheets": {
        ".xls", ".xlsx", ".csv", ".ods"
    },
    "Presentations": {
        ".ppt", ".pptx", ".odp"
    },
    "Archives": {
        ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"
    },
    "Python": {
        ".py", ".pyw"
    },
    "Programs": {
        ".exe", ".msi", ".bat", ".cmd", ".com"
    },
    "Web": {
        ".html", ".htm", ".css", ".js", ".xml"
    },
    "Code": {
        ".c", ".cpp", ".h", ".hpp", ".java", ".kt",
        ".rs", ".go", ".php", ".rb", ".swift"
    },
    "Databases": {
        ".db", ".sqlite", ".sqlite3", ".sql"
    },
    "Ebooks": {
        ".epub", ".mobi", ".azw", ".azw3"
    },
    "3D Models": {
        ".obj", ".fbx", ".stl", ".blend", ".dae", ".gltf", ".glb"
    },
    "Design": {
        ".psd", ".ai", ".eps", ".indd", ".xd"
    },
    "Subtitles": {
        ".srt", ".vtt", ".ass", ".ssa"
    },
    "Fonts": {
        ".ttf", ".otf", ".woff", ".woff2"
    },
}


def category_for(path: Path) -> str:
    """Return the category for a path based on its lower-case suffix."""
    suffix = path.suffix.lower()

    for category, extensions in CATEGORIES.items():
        if suffix in extensions:
            return category

    return "Others"