"""Logging extension point.

The original application used ``print`` for operation failures and had no
logging configuration.  Keeping setup isolated means structured logging can
be enabled later without coupling it to Qt widgets or file operations.
"""

import logging
from logging.handlers import RotatingFileHandler

from .config import activity_log_path


def configure_logging(enabled: bool = True) -> None:
    """Configure console logging and optional persistent activity logging."""
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")

    if not any(isinstance(handler, logging.StreamHandler) for handler in root.handlers):
        console = logging.StreamHandler()
        console.setFormatter(formatter)
        root.addHandler(console)

    file_handlers = [
        handler for handler in root.handlers
        if getattr(handler, "_sfm_activity_handler", False)
    ]
    if enabled and not file_handlers:
        try:
            activity_log_path().parent.mkdir(parents=True, exist_ok=True)
            handler = RotatingFileHandler(
                activity_log_path(), maxBytes=512 * 1024, backupCount=2,
                encoding="utf-8",
            )
            handler._sfm_activity_handler = True
            handler.setFormatter(formatter)
            root.addHandler(handler)
        except OSError:
            logging.getLogger(__name__).warning("Activity log could not be opened.")
    elif not enabled:
        for handler in file_handlers:
            root.removeHandler(handler)
            handler.close()