"""Persistent application settings and safe default paths."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

APP_NAME = "SFM 2.0"
VERSION = "2.0"
GITHUB_URL = "https://github.com/"

DEFAULT_SETTINGS: dict[str, Any] = {
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


def _valid_settings(data: object) -> dict[str, Any]:
    """Merge untrusted or old JSON with safe defaults."""
    result = dict(DEFAULT_SETTINGS)
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
    return result


class AppConfig:
    """Small JSON-backed configuration object shared by UI and services."""

    def __init__(self, path: Path | None = None):
        self.path = Path(path) if path else settings_path()
        self.values = dict(DEFAULT_SETTINGS)
        self.load()

    def load(self) -> None:
        try:
            self.values = _valid_settings(json.loads(self.path.read_text(encoding="utf-8")))
        except (OSError, ValueError, TypeError):
            self.values = dict(DEFAULT_SETTINGS)

    def get(self, key: str) -> Any:
        return self.values.get(key, DEFAULT_SETTINGS.get(key))

    def set(self, key: str, value: Any) -> None:
        if key in DEFAULT_SETTINGS:
            self.values[key] = value

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        # Replace the file atomically so an interrupted write cannot corrupt it.
        with NamedTemporaryFile(
            "w", encoding="utf-8", dir=self.path.parent, delete=False
        ) as temporary:
            json.dump(self.values, temporary, indent=2)
            temporary.write("\n")
            temporary_path = Path(temporary.name)
        temporary_path.replace(self.path)

    def reset(self) -> None:
        self.values = dict(DEFAULT_SETTINGS)
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
                lines = [f"@echo off", command]
            else:
                command = f'"{sys.executable}" -m smart_file_manager'
                lines = ["@echo off", f'cd /d "{Path.cwd()}"', command]
            launcher.write_text("\n".join(lines) + "\n", encoding="utf-8")
        elif launcher.exists():
            launcher.unlink()
    except OSError as error:
        return False, str(error)

    return True, ""