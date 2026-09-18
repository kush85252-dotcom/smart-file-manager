"""Allow ``python -m smart_file_manager`` to start the application."""

from .app import run


if __name__ == "__main__":
    raise SystemExit(run())