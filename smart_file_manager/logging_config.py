"""Logging setup: console output plus an optional rotating activity log.

The log lives next to the settings file (see ``activity_log_path``), rotates at
512 KB and keeps 2 backups, so it can never grow without bound.  Only
operational facts are logged (paths, counts, error messages); file contents
are never read for logging and no passwords or credentials exist in the app.

Logging problems must never stop the application, so every failure to open
the log file degrades to console-only logging.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler

from .config import activity_log_path

LOG_MAX_BYTES = 512 * 1024
LOG_BACKUP_COUNT = 2

_FORMAT = "%(asctime)s %(levelname)s [%(name)s]: %(message)s"


def configure_logging(enabled: bool = True) -> bool:
    """Configure logging.  Returns True if the file log is active as requested.

    ``enabled=False`` removes the file handler (the user's "activity logging"
    setting); that case returns True because nothing was asked to be written.
    """
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    formatter = logging.Formatter(_FORMAT)

    # RotatingFileHandler is a StreamHandler subclass, so tell them apart.
    has_console = any(
        type(handler) is logging.StreamHandler for handler in root.handlers
    )
    # Windowed (no-console) builds have no stderr; skip the console handler.
    if not has_console and sys.stderr is not None:
        console = logging.StreamHandler()
        console.setFormatter(formatter)
        root.addHandler(console)

    file_handlers = [
        handler for handler in root.handlers
        if getattr(handler, "_sfm_activity_handler", False)
    ]
    if not enabled:
        for handler in file_handlers:
            root.removeHandler(handler)
            handler.close()
        return True

    if file_handlers:
        return True

    try:
        activity_log_path().parent.mkdir(parents=True, exist_ok=True)
        handler = RotatingFileHandler(
            activity_log_path(), maxBytes=LOG_MAX_BYTES, backupCount=LOG_BACKUP_COUNT,
            encoding="utf-8",
        )
    except (OSError, ValueError) as error:
        logging.getLogger(__name__).warning("Activity log could not be opened: %s", error)
        return False

    handler._sfm_activity_handler = True
    handler.setFormatter(formatter)
    root.addHandler(handler)
    return True


def install_exception_hook() -> None:
    """Log uncaught exceptions (with traceback) before the default handler runs."""
    previous = sys.excepthook

    def hook(exc_type, exc_value, exc_traceback):
        if not issubclass(exc_type, KeyboardInterrupt):
            logging.getLogger("sfm.uncaught").critical(
                "Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback)
            )
        previous(exc_type, exc_value, exc_traceback)

    sys.excepthook = hook
