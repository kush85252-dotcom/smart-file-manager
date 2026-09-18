"""Small, dependency-free presentation helpers."""

from datetime import datetime
from pathlib import Path


def format_size(size: int) -> str:
    """Format a byte count using the units used by the original UI."""
    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(size)

    for unit in units:
        if value < 1024:
            return f"{value:.1f} {unit}"

        value /= 1024

    return f"{value:.1f} PB"


def modified_date(path: Path) -> str:
    """Return a formatted modification date, or '-' if stat fails."""
    try:
        timestamp = path.stat().st_mtime
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return "-"