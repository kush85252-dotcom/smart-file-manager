"""
ui/dialogs.py
=============
Dialog helpers — thin wrappers around QMessageBox for consistent usage
across the application.
"""

from PyQt6.QtWidgets import QMessageBox


def confirm_organize(parent, folder_count: int) -> bool:
    """
    Show a Yes/No confirmation dialog before organizing.

    Returns True if the user clicked Yes, False otherwise.
    """
    reply = QMessageBox.question(
        parent,
        "Confirm Organize",
        f"This will move files in {folder_count} folder(s).\n"
        "Are you sure you want to continue?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No,
    )
    return reply == QMessageBox.StandardButton.Yes
