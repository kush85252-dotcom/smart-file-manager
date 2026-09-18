"""Logging extension point.

The original application used ``print`` for operation failures and had no
logging configuration.  Keeping setup isolated means structured logging can
be enabled later without coupling it to Qt widgets or file operations.
"""

import logging


def configure_logging() -> None:
    """Configure conservative console logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )