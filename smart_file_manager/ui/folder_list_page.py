"""A reusable page that lists folder paths (used for Favorites and Recent)."""

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QBrush, QColor
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..services.folder_lists import folder_exists

PATH_ROLE = Qt.ItemDataRole.UserRole


class FolderListPage(QWidget):
    """Shows folders, flags missing ones, and reports what the user asked for.

    The page owns no data; the main window stores the lists and calls
    :meth:`set_paths`.  Missing folders stay in the list (greyed, marked)
    so the user decides whether to remove them.
    """

    open_requested = pyqtSignal(str)
    remove_requested = pyqtSignal(str)
    add_current_requested = pyqtSignal()
    add_folder_requested = pyqtSignal()
    clear_requested = pyqtSignal()

    def __init__(self, heading: str, description: str, empty_text: str,
                 allow_add: bool = False, allow_clear: bool = False,
                 parent: QWidget | None = None):
        super().__init__(parent)
        self._empty_text = empty_text

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(12)

        title = QLabel(heading)
        title.setObjectName("heading")
        intro = QLabel(description)
        intro.setObjectName("description")
        intro.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(intro)

        buttons = QHBoxLayout()
        self.add_current_button = QPushButton("★ Add Current Folder")
        self.add_folder_button = QPushButton("＋ Add Folder…")
        self.open_button = QPushButton("📂 Open")
        self.remove_button = QPushButton("Remove")
        self.clear_button = QPushButton("Clear All")
        if allow_add:
            buttons.addWidget(self.add_current_button)
            buttons.addWidget(self.add_folder_button)
        buttons.addWidget(self.open_button)
        buttons.addWidget(self.remove_button)
        if allow_clear:
            buttons.addWidget(self.clear_button)
        buttons.addStretch()
        layout.addLayout(buttons)

        self.list = QListWidget()
        self.list.setAlternatingRowColors(True)
        layout.addWidget(self.list, 1)

        self.status_label = QLabel("")
        self.status_label.setObjectName("status")
        layout.addWidget(self.status_label)

        self.add_current_button.clicked.connect(self.add_current_requested)
        self.add_folder_button.clicked.connect(self.add_folder_requested)
        self.open_button.clicked.connect(self._open_selected)
        self.remove_button.clicked.connect(self._remove_selected)
        self.clear_button.clicked.connect(self.clear_requested)
        self.list.itemDoubleClicked.connect(lambda item: self.open_requested.emit(item.data(PATH_ROLE)))
        self.list.itemSelectionChanged.connect(self._update_buttons)
        self._update_buttons()

    def paths(self) -> list[str]:
        return [self.list.item(i).data(PATH_ROLE) for i in range(self.list.count())]

    def set_paths(self, paths: list[str]) -> None:
        """Rebuild the list, marking folders that no longer exist."""
        selected = self._selected_path()
        self.list.clear()
        missing = 0
        for path in paths:
            exists = folder_exists(path)
            item = QListWidgetItem(path if exists else f"⚠ {path}   (folder not found)")
            item.setData(PATH_ROLE, path)
            item.setToolTip(path)
            if not exists:
                missing += 1
                item.setForeground(QBrush(QColor("#c9a227")))
            self.list.addItem(item)
            if path == selected:
                self.list.setCurrentItem(item)
        if not paths:
            self.status_label.setText(self._empty_text)
        elif missing:
            self.status_label.setText(f"{len(paths)} folders - {missing} not found right now.")
        else:
            self.status_label.setText(f"{len(paths)} folders")
        self.clear_button.setEnabled(bool(paths))
        self._update_buttons()

    def _selected_path(self) -> str | None:
        item = self.list.currentItem()
        return item.data(PATH_ROLE) if item is not None else None

    def _update_buttons(self) -> None:
        has_selection = self._selected_path() is not None
        self.open_button.setEnabled(has_selection)
        self.remove_button.setEnabled(has_selection)

    def _open_selected(self) -> None:
        path = self._selected_path()
        if path is not None:
            self.open_requested.emit(path)

    def _remove_selected(self) -> None:
        path = self._selected_path()
        if path is not None:
            self.remove_requested.emit(path)
