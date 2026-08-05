"""
backend/config.py
=================
Settings persistence — load and save the JSON settings file.
"""

import json
from pathlib import Path

# The settings file lives next to main.py (i.e. the project root).
SETTINGS_PATH = Path(__file__).resolve().parent.parent / "startup.json"


def load_settings() -> dict:
    """
    Load settings from SETTINGS_PATH.
    Returns an empty dict if the file does not exist.
    """
    if SETTINGS_PATH.exists():
        with open(SETTINGS_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    return {}


def save_settings(settings: dict) -> None:
    """
    Persist *settings* to SETTINGS_PATH as formatted JSON.
    Prints the path and the saved selected_folders key for debugging.
    """
    print("Saving to:", SETTINGS_PATH)
    print("selected_folders =", settings.get("selected_folders"))

    with open(SETTINGS_PATH, "w", encoding="utf-8") as file:
        json.dump(settings, file, indent=4)

    print("Reloaded:", load_settings())
