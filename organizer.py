"""Backwards-compatible Smart File Manager entry point.

The original uploaded application was a single ``organizer.py`` file.  Keep
this import surface so existing launch commands and imports continue to work,
while the implementation now lives in the package.
"""

from smart_file_manager.categorization import CATEGORIES, category_for
from smart_file_manager.config import APP_NAME, VERSION
from smart_file_manager.utils import format_size, modified_date

__all__ = [
    "APP_NAME",
    "VERSION",
    "CATEGORIES",
    "SFM_Lite",
    "category_for",
    "format_size",
    "modified_date",
    "run",
]


def run() -> int:
    """Start the application while keeping helper imports lightweight."""
    from smart_file_manager.app import run as application_run

    return application_run()


def __getattr__(name):
    """Load the Qt window only when callers actually request it."""
    if name == "SFM_Lite":
        from smart_file_manager.ui.main_window import SFM_Lite

        return SFM_Lite

    raise AttributeError(name)


if __name__ == "__main__":
    raise SystemExit(run())