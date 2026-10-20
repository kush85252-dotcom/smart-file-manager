"""Persistent application settings and safe default paths."""

from __future__ import annotations

import copy
import json
import logging
import os
import shutil
import sys
import time
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

APP_NAME = "Smart File Manager"
VERSION = "2.2.0"
GITHUB_URL = "https://github.com/"
SETTINGS_SCHEMA_VERSION = 2

logger = logging.getLogger(__name__)

# Limits for the user-data lists added in 2.1.
MAX_FAVORITES = 200
RECENT_LIMIT_CHOICES = (10, 20, 50, 100)
DEFAULT_RECENT_LIMIT = 20

DEFAULT_SETTINGS: dict[str, Any] = {
    "schema_version": SETTINGS_SCHEMA_VERSION,
    "start_with_windows": False,
    "show_hidden_files": False,
    "confirm_before_organizing": True,
    "create_category_folders": True,
    "scan_subfolders": False,
    "organization_mode": "category",
    "theme": "dark",
    "ui_scale": 100,
    "preview_before_apply": True,
    "keep_undo_history": True,
    "use_recycle_bin": True,
    "show_notifications": True,
    "activity_logging": True,
    # --- added in 2.1 (older settings files simply lack these keys) ---
    "favorites": [],
    "recent_folders": [],
    "recent_limit": DEFAULT_RECENT_LIMIT,
}

BOOL_SETTINGS = {
    "start_with_windows",
    "show_hidden_files",
    "confirm_before_organizing",
    "create_category_folders",
    "scan_subfolders",
    "preview_before_apply",
    "keep_undo_history",
    "use_recycle_bin",
    "show_notifications",
    "activity_logging",
}

# User data (not preferences): "Reset to Defaults" must never wipe these.
USER_DATA_KEYS = ("favorites", "recent_folders")


def default_settings() -> dict[str, Any]:
    """Return a fresh copy of the defaults (the lists must not be shared)."""
    return copy.deepcopy(DEFAULT_SETTINGS)


def default_start_folder() -> Path:
    """Return the original Downloads-then-home startup location."""
    downloads = Path.home() / "Downloads"
    return downloads if downloads.exists() else Path.home()


def settings_directory() -> Path:
    """Return a per-user settings directory on each supported desktop OS."""
    if sys.platform.startswith("win"):
        root = os.environ.get("APPDATA") or str(Path.home() / "AppData/Roaming")
        return Path(root) / "SmartFileManager"
    if sys.platform == "darwin":
        return Path.home() / "Library/Application Support/SmartFileManager"
    return Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "smart-file-manager"


def settings_path() -> Path:
    """Return the JSON settings file path.

    ``SFM_SETTINGS_PATH`` is intentionally supported for portable installs and
    tests, while normal users get a conventional per-user config location.
    """
    override = os.environ.get("SFM_SETTINGS_PATH")
    return Path(override).expanduser() if override else settings_directory() / "settings.json"


def activity_log_path() -> Path:
    return settings_directory() / "activity.log"


def custom_rules_path() -> Path:
    """Return the versioned custom-rule document in the per-user data folder."""
    return settings_directory() / "custom_rules.json"


def activity_history_path() -> Path:
    """Return persistent undo-capable operation history (separate from text logs)."""
    return settings_directory() / "activity_history.json"


def _clean_path_list(value: object, limit: int) -> list[str]:
    """Keep only non-empty path strings, without duplicates, up to ``limit``."""
    if not isinstance(value, list):
        return []
    # Imported here to keep config.py importable without the services package
    # having side effects at import time.
    from .services.folder_lists import path_key

    cleaned: list[str] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, str) or not item.strip():
            continue
        key = path_key(item)
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(item)
        if len(cleaned) >= limit:
            break
    return cleaned


def _valid_settings(data: object) -> dict[str, Any]:
    """Merge untrusted or old JSON with safe defaults."""
    result = default_settings()
    if not isinstance(data, dict):
        return result

    for key in BOOL_SETTINGS:
        if isinstance(data.get(key), bool):
            result[key] = data[key]

    if data.get("organization_mode") in {"category", "extension"}:
        result["organization_mode"] = data["organization_mode"]
    if data.get("theme") in {"dark", "light"}:
        result["theme"] = data["theme"]
    if isinstance(data.get("ui_scale"), int) and data["ui_scale"] in {100, 110, 125, 150}:
        result["ui_scale"] = data["ui_scale"]

    limit = data.get("recent_limit")
    if isinstance(limit, int) and not isinstance(limit, bool) and 1 <= limit <= 100:
        result["recent_limit"] = limit

    result["favorites"] = _clean_path_list(data.get("favorites"), MAX_FAVORITES)
    result["recent_folders"] = _clean_path_list(
        data.get("recent_folders"), result["recent_limit"]
    )
    return result


class AppConfig:
    """Small JSON-backed configuration object shared by UI and services."""

    def __init__(self, path: Path | None = None):
        self.path = Path(path) if path else settings_path()
        self.values = default_settings()
        self.load()

    def load(self) -> None:
        try:
            text = self.path.read_text(encoding="utf-8")
        except FileNotFoundError:
            self.values = default_settings()
            return
        except OSError as error:
            logger.warning("Could not read settings file: %s", error)
            self.values = default_settings()
            return

        try:
            self.values = _valid_settings(json.loads(text))
        except (ValueError, TypeError):
            logger.warning("Settings file is malformed; using defaults.")
            self.values = default_settings()
            self._back_up_malformed_file()

    def _back_up_malformed_file(self) -> None:
        """Keep a copy of an unreadable settings file before it is replaced.

        The next ``save()`` overwrites ``settings.json`` with defaults; without
        this copy the user's old favorites and preferences would be lost.
        """
        backup = self.path.with_name(f"{self.path.name}.corrupt-{time.strftime('%Y%m%d-%H%M%S')}")
        try:
            shutil.copy2(self.path, backup)
        except OSError as error:
            logger.warning("Could not back up malformed settings file: %s", error)

    def get(self, key: str) -> Any:
        value = self.values.get(key, DEFAULT_SETTINGS.get(key))
        # Hand out copies of lists so callers cannot mutate stored state.
        return list(value) if isinstance(value, list) else value

    def set(self, key: str, value: Any) -> None:
        if key in DEFAULT_SETTINGS:
            self.values[key] = value

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        # Replace the file atomically so an interrupted write cannot corrupt it.
        temporary_path: Path | None = None
        try:
            with NamedTemporaryFile(
                "w", encoding="utf-8", dir=self.path.parent, delete=False,
                prefix=f"{self.path.name}.", suffix=".tmp",
            ) as temporary:
                temporary_path = Path(temporary.name)
                json.dump(self.values, temporary, indent=2)
                temporary.write("\n")
                temporary.flush()
                os.fsync(temporary.fileno())
            temporary_path.replace(self.path)
            temporary_path = None
        finally:
            if temporary_path is not None:
                try:
                    temporary_path.unlink()
                except OSError:
                    pass

    def reset(self) -> None:
        """Restore preferences to defaults but keep favorites and recents."""
        kept = {key: self.values.get(key) for key in USER_DATA_KEYS}
        self.values = default_settings()
        self.values.update(kept)
        self.save()


def apply_startup_setting(enabled: bool) -> tuple[bool, str]:
    """Create or remove the Windows Startup launcher when supported."""
    if not sys.platform.startswith("win"):
        return False, "Windows startup is only available on Windows."

    startup_dir = Path(os.environ.get("APPDATA", Path.home())) / (
        "Microsoft/Windows/Start Menu/Programs/Startup"
    )
    launcher = startup_dir / "Smart File Manager.bat"

    try:
        if enabled:
            startup_dir.mkdir(parents=True, exist_ok=True)
            if getattr(sys, "frozen", False):
                command = f'"{sys.executable}"'
                lines = ["@echo off", command]
            else:
                command = f'"{sys.executable}" -m smart_file_manager'
                lines = ["@echo off", f'cd /d "{Path.cwd()}"', command]
            launcher.write_text("\n".join(lines) + "\n", encoding="utf-8")
        elif launcher.exists():
            launcher.unlink()
    except OSError as error:
        return False, str(error)

    return True, ""
