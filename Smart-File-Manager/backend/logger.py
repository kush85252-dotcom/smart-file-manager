"""
backend/logger.py
=================
Log-panel helper — colour-codes and appends a message to the QTextEdit log widget.
Safe to call from any thread when connected via a Qt signal.
"""

from PyQt6.QtGui import QTextCursor
from utils.constants import COLORS


def append_log(log_text_widget, message: str) -> None:
    """
    Append *message* to *log_text_widget* (a QTextEdit).

    Lines are colour-coded based on content keywords:
      [ERROR]  → danger red
      [AUTO]   → warning yellow
      ═══      → accent purple  (section headers)
      ✔        → success green
      (other)  → default text colour
    """
    cursor = log_text_widget.textCursor()
    cursor.movePosition(QTextCursor.MoveOperation.End)

    # Choose colour based on content
    if "[ERROR]" in message:
        color = COLORS["danger"]
    elif "[AUTO]" in message:
        color = COLORS["warning"]
    elif "═══" in message:
        color = COLORS["accent"]
    elif "✔" in message:
        color = COLORS["success"]
    else:
        color = COLORS["text"]

    html = (
        f'<span style="color:{color};">'
        f"{message.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')}"
        f"</span><br>"
    )
    cursor.insertHtml(html)

    # Auto-scroll to the bottom
    log_text_widget.verticalScrollBar().setValue(
        log_text_widget.verticalScrollBar().maximum()
    )
