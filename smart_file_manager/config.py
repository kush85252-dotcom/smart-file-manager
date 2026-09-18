"""Application configuration and safe default paths.

This module intentionally keeps configuration in Python because the original
application did not have a JSON settings file.  A future settings layer can
be added here without making the UI or services responsible for path policy.
"""

from pathlib import Path

APP_NAME = "SFM 2.0"
VERSION = "2.0"


def default_start_folder() -> Path:
    """Return the original Downloads-then-home startup location."""
    downloads = Path.home() / "Downloads"
    return downloads if downloads.exists() else Path.home()