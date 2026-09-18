"""Main Qt window for Smart File Manager."""

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..categorization import category_for
from ..config import APP_NAME, VERSION, default_start_folder
from ..services.file_operations import (
    delete_path,
    open_file as open_file_operation,
    rename_path,
)
from ..services.organizer import (
    build_organize_plan as build_organize_plan_service,
    organize_plan,
    undo_operation,
)
from ..utils import format_size, modified_date
from .styles import STYLESHEET


class SFM_Lite(QMainWindow):
    """The original Smart File Manager window, split from application logic."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle(f"{APP_NAME} {VERSION}")
        self.resize(1150, 700)

        self.current_folder = default_start_folder()

        # Used for navigation
        self.history = []
        self.history_index = -1

        # Undo operations
        self.undo_history = []

        self.files = []

        self.build_ui()
        self.apply_style()

        self.navigate_to(self.current_folder, save_history=True)

    # ========================================================
    # UI
    # ========================================================

    def build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)

        main_layout = QHBoxLayout(root)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ----------------------------------------------------
        # SIDEBAR
        # ----------------------------------------------------

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(210)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(15, 20, 15, 20)

        title = QLabel("SFM 2.0")
        title.setObjectName("appTitle")

        version = QLabel("Smart File Manager 2.0")
        version.setObjectName("version")

        sidebar_layout.addWidget(title)
        sidebar_layout.addWidget(version)
        sidebar_layout.addSpacing(25)

        self.dashboard_button = self.sidebar_button("📊  Dashboard")
        self.files_button = self.sidebar_button("📁  Files")
        self.organize_button = self.sidebar_button("🧹  Organize")

        sidebar_layout.addWidget(self.dashboard_button)
        sidebar_layout.addWidget(self.files_button)
        sidebar_layout.addWidget(self.organize_button)

        sidebar_layout.addStretch()

        info = QLabel(
            "SFM 2.0\n"
            "Fast • Simple • Safe"
        )
        info.setObjectName("sidebarInfo")

        sidebar_layout.addWidget(info)

        # ----------------------------------------------------
        # CONTENT
        # ----------------------------------------------------

        self.stack = QStackedWidget()

        self.dashboard_page = self.create_dashboard()
        self.files_page = self.create_files_page()
        self.organize_page = self.create_organize_page()

        self.stack.addWidget(self.dashboard_page)
        self.stack.addWidget(self.files_page)
        self.stack.addWidget(self.organize_page)

        self.dashboard_button.clicked.connect(
            lambda: self.stack.setCurrentIndex(0)
        )

        self.files_button.clicked.connect(
            lambda: self.stack.setCurrentIndex(1)
        )

        self.organize_button.clicked.connect(
            lambda: self.stack.setCurrentIndex(2)
        )

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stack)

    # ========================================================
    # SIDEBAR BUTTON
    # ========================================================

    def sidebar_button(self, text):
        button = QPushButton(text)
        button.setObjectName("sidebarButton")
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        return button

    # ========================================================
    # DASHBOARD
    # ========================================================

    def create_dashboard(self):
        page = QWidget()

        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        heading = QLabel("Dashboard")
        heading.setObjectName("heading")

        self.location_label = QLabel()
        self.location_label.setObjectName("location")

        layout.addWidget(heading)
        layout.addWidget(self.location_label)

        # Cards
        cards = QHBoxLayout()

        self.files_card = self.create_card("📄 Files", "0")
        self.folders_card = self.create_card("📁 Folders", "0")
        self.size_card = self.create_card("💾 Size", "0 B")

        cards.addWidget(self.files_card)
        cards.addWidget(self.folders_card)
        cards.addWidget(self.size_card)

        layout.addLayout(cards)

        category_title = QLabel("File Categories")
        category_title.setObjectName("sectionTitle")

        layout.addWidget(category_title)

        self.category_label = QLabel()
        self.category_label.setObjectName("categoryInfo")

        layout.addWidget(self.category_label)
        layout.addStretch()

        return page

    # ========================================================
    # CARD
    # ========================================================

    def create_card(self, title, value):
        card = QFrame()
        card.setObjectName("card")

        layout = QVBoxLayout(card)

        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")

        value_label = QLabel(value)
        value_label.setObjectName("cardValue")

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        card.value_label = value_label
        return card

    # ========================================================
    # FILES PAGE
    # ========================================================

    def create_files_page(self):
        page = QWidget()

        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(12)

        top = QHBoxLayout()

        heading = QLabel("Files")
        heading.setObjectName("heading")

        top.addWidget(heading)
        top.addStretch()

        self.choose_button = QPushButton("📂 Choose Folder")
        self.choose_button.clicked.connect(self.choose_folder)

        self.refresh_button = QPushButton("⟳ Refresh")
        self.refresh_button.clicked.connect(self.refresh)

        top.addWidget(self.choose_button)
        top.addWidget(self.refresh_button)
        layout.addLayout(top)

        # Navigation
        nav = QHBoxLayout()

        self.back_button = QPushButton("← Back")
        self.back_button.clicked.connect(self.go_back)

        self.forward_button = QPushButton("Forward →")
        self.forward_button.clicked.connect(self.go_forward)

        self.up_button = QPushButton("↑ Up")
        self.up_button.clicked.connect(self.go_up)

        nav.addWidget(self.back_button)
        nav.addWidget(self.forward_button)
        nav.addWidget(self.up_button)

        self.path_label = QLineEdit()
        self.path_label.setReadOnly(True)
        nav.addWidget(self.path_label)
        layout.addLayout(nav)

        # Search
        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍 Search files...")
        self.search.textChanged.connect(self.filter_files)
        layout.addWidget(self.search)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Name",
            "Type",
            "Size",
            "Category",
            "Modified",
        ])
        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.table.setSelectionMode(
            QTableWidget.SelectionMode.ExtendedSelection
        )
        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.table.setAlternatingRowColors(True)

        self.table.horizontalHeader().setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.Stretch
        )
        for column in (1, 2, 3, 4):
            self.table.horizontalHeader().setSectionResizeMode(
                column,
                QHeaderView.ResizeMode.ResizeToContents
            )

        self.table.cellDoubleClicked.connect(self.double_click_item)
        self.table.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.table.customContextMenuRequested.connect(
            self.show_context_menu
        )
        layout.addWidget(self.table)

        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("status")
        layout.addWidget(self.status_label)

        return page

    # ========================================================
    # ORGANIZE PAGE
    # ========================================================

    def create_organize_page(self):
        page = QWidget()

        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        heading = QLabel("Organize Files")
        heading.setObjectName("heading")

        description = QLabel(
            "Move files into folders based on their file type."
        )
        description.setObjectName("description")

        layout.addWidget(heading)
        layout.addWidget(description)

        self.organize_location = QLabel()
        self.organize_location.setObjectName("location")
        layout.addWidget(self.organize_location)

        self.organize_preview = QLabel(
            "Press the button below to preview what will happen."
        )
        self.organize_preview.setObjectName("preview")
        layout.addWidget(self.organize_preview)

        self.progress = QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        self.organize_action_button = QPushButton("🧹 Organize Files")
        self.organize_action_button.clicked.connect(self.organize_files)
        layout.addWidget(self.organize_action_button)

        self.undo_button = QPushButton("↩ Undo Last Organization")
        self.undo_button.clicked.connect(self.undo_last)
        layout.addWidget(self.undo_button)

        layout.addStretch()
        return page

    # ========================================================
    # NAVIGATION
    # ========================================================

    def navigate_to(self, folder, save_history=True):
        folder = Path(folder)

        if not folder.exists() or not folder.is_dir():
            return

        if save_history:
            # Remove future history
            if self.history_index < len(self.history) - 1:
                self.history = self.history[:self.history_index + 1]

            self.history.append(folder)
            self.history_index += 1

        self.current_folder = folder
        self.load_folder()

    def load_folder(self):
        try:
            items = list(self.current_folder.iterdir())
        except PermissionError:
            QMessageBox.warning(
                self,
                "Permission denied",
                "You don't have permission to open this folder."
            )
            return
        except OSError as error:
            QMessageBox.warning(
                self,
                "Couldn't open folder",
                str(error)
            )
            return

        self.files = sorted(
            items,
            key=lambda x: (
                not x.is_dir(),
                x.name.lower()
            )
        )

        self.path_label.setText(str(self.current_folder))
        self.location_label.setText(f"📍 {self.current_folder}")
        self.organize_location.setText(
            f"📍 Organizing: {self.current_folder}"
        )

        self.display_files(self.files)
        self.update_dashboard()

        self.back_button.setEnabled(self.history_index > 0)
        self.forward_button.setEnabled(
            self.history_index < len(self.history) - 1
        )
        self.up_button.setEnabled(
            self.current_folder.parent != self.current_folder
        )
        self.status_label.setText(f"{len(self.files)} items")

    # ========================================================
    # DISPLAY FILES
    # ========================================================

    def display_files(self, items):
        self.table.setRowCount(0)

        for path in items:
            row = self.table.rowCount()
            self.table.insertRow(row)
            name_item = QTableWidgetItem(path.name)
            # Keep the real Path attached to the row.  This prevents filtered
            # views from acting on the wrong file when row numbers no longer
            # match self.files.
            name_item.setData(Qt.ItemDataRole.UserRole, str(path))

            if path.is_dir():
                name_item.setText(f"📁 {path.name}")
                file_type = "Folder"
                size = "-"
                category = "Folder"
            else:
                file_type = path.suffix.lower() or "File"

                try:
                    size = format_size(path.stat().st_size)
                except Exception:
                    size = "-"

                category = category_for(path)

            type_item = QTableWidgetItem(file_type)
            size_item = QTableWidgetItem(size)
            category_item = QTableWidgetItem(category)
            modified_item = QTableWidgetItem(modified_date(path))

            self.table.setItem(row, 0, name_item)
            self.table.setItem(row, 1, type_item)
            self.table.setItem(row, 2, size_item)
            self.table.setItem(row, 3, category_item)
            self.table.setItem(row, 4, modified_item)

    # ========================================================
    # SEARCH
    # ========================================================

    def filter_files(self, text):
        text = text.lower().strip()

        if not text:
            self.display_files(self.files)
            return

        filtered = [
            path
            for path in self.files
            if text in path.name.lower()
        ]

        self.display_files(filtered)
        self.status_label.setText(f"{len(filtered)} matching items")

    # ========================================================
    # DOUBLE CLICK
    # ========================================================

    def double_click_item(self, row, column):
        path = self.path_from_row(row)

        if not path:
            return

        if path.is_dir():
            self.navigate_to(path, save_history=True)
        elif path.is_file():
            self.open_file(path)

    # ========================================================
    # OPEN FILE
    # ========================================================

    def open_file(self, path):
        try:
            open_file_operation(path)
        except Exception as error:
            QMessageBox.warning(
                self,
                "Couldn't open file",
                str(error)
            )

    # ========================================================
    # CHOOSE FOLDER / REFRESH / NAVIGATION
    # ========================================================

    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Choose Folder",
            str(self.current_folder)
        )

        if folder:
            self.navigate_to(Path(folder), save_history=True)

    def refresh(self):
        self.load_folder()

    def go_back(self):
        if self.history_index <= 0:
            return

        self.history_index -= 1
        self.current_folder = self.history[self.history_index]
        self.load_folder()

    def go_forward(self):
        if self.history_index >= len(self.history) - 1:
            return

        self.history_index += 1
        self.current_folder = self.history[self.history_index]
        self.load_folder()

    def go_up(self):
        parent = self.current_folder.parent

        if parent != self.current_folder:
            self.navigate_to(parent, save_history=True)

    # ========================================================
    # CONTEXT MENU
    # ========================================================

    def show_context_menu(self, position):
        row = self.table.rowAt(position.y())

        if row < 0:
            return

        menu = QMenu(self)

        open_action = QAction("📂 Open", self)
        rename_action = QAction("✏ Rename", self)
        copy_action = QAction("📋 Copy Path", self)
        delete_action = QAction("🗑 Delete", self)

        open_action.triggered.connect(lambda: self.context_open(row))
        rename_action.triggered.connect(lambda: self.context_rename(row))
        copy_action.triggered.connect(
            lambda: self.context_copy_path(row)
        )
        delete_action.triggered.connect(lambda: self.context_delete(row))

        menu.addAction(open_action)
        menu.addAction(rename_action)
        menu.addAction(copy_action)
        menu.addSeparator()
        menu.addAction(delete_action)

        menu.exec(self.table.viewport().mapToGlobal(position))

    def path_from_row(self, row):
        item = self.table.item(row, 0)

        if not item:
            return None

        stored_path = item.data(Qt.ItemDataRole.UserRole)
        if stored_path:
            return Path(stored_path)

        # Backward-compatible fallback for rows created by older UI state.
        name = item.text()
        if name.startswith("📁 "):
            name = name[2:]

        return self.current_folder / name

    def context_open(self, row):
        path = self.path_from_row(row)

        if not path:
            return

        if path.is_dir():
            self.navigate_to(path, save_history=True)
        else:
            self.open_file(path)

    def context_rename(self, row):
        path = self.path_from_row(row)

        if not path:
            return

        old_name = path.name
        new_name, ok = QInputDialog.getText(
            self,
            "Rename",
            "New name:",
            text=old_name
        )

        new_name = new_name.strip()

        if not ok or not new_name:
            return

        # A rename must stay inside the current directory.  Explicitly reject
        # path separators so a user cannot turn the rename field into a move.
        if new_name in {".", ".."} or "/" in new_name or "\\\\" in new_name:
            QMessageBox.warning(
                self,
                "Invalid name",
                "A file or folder name cannot contain path separators."
            )
            return

        new_path = path.parent / new_name

        if new_path == path:
            return

        if new_path.exists():
            QMessageBox.warning(
                self,
                "Already exists",
                "A file or folder with that name already exists."
            )
            return

        try:
            rename_path(path, new_path)
            self.refresh()
        except Exception as error:
            QMessageBox.critical(
                self,
                "Rename failed",
                str(error)
            )

    def context_copy_path(self, row):
        path = self.path_from_row(row)

        if path:
            QApplication.clipboard().setText(str(path))
            self.status_label.setText("Path copied to clipboard.")

    def context_delete(self, row):
        path = self.path_from_row(row)

        if not path:
            return

        answer = QMessageBox.question(
            self,
            "Delete",
            f"Delete:\n\n{path.name}?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        try:
            delete_path(path)
            self.refresh()
        except Exception as error:
            QMessageBox.critical(
                self,
                "Delete failed",
                str(error)
            )

    # ========================================================
    # DASHBOARD / ORGANIZATION
    # ========================================================

    def update_dashboard(self):
        file_count = 0
        folder_count = 0
        total_size = 0
        categories = {}

        for path in self.files:
            if path.is_dir():
                folder_count += 1
                continue

            file_count += 1

            try:
                total_size += path.stat().st_size
            except Exception:
                pass

            category = category_for(path)
            categories[category] = categories.get(category, 0) + 1

        self.files_card.value_label.setText(str(file_count))
        self.folders_card.value_label.setText(str(folder_count))
        self.size_card.value_label.setText(format_size(total_size))

        if categories:
            category_text = "\n".join(
                f"• {category}: {count}"
                for category, count in sorted(categories.items())
            )
        else:
            category_text = "No files found."

        self.category_label.setText(category_text)

    def build_organize_plan(self):
        return build_organize_plan_service(
            self.files,
            self.current_folder,
        )

    def organize_files(self):
        plan = self.build_organize_plan()

        if not plan:
            QMessageBox.information(
                self,
                "Nothing to organize",
                "There are no files to organize."
            )
            return

        preview_lines = []
        for source, folder, destination in plan[:15]:
            preview_lines.append(f"{source.name}  →  {folder.name}/")

        if len(plan) > 15:
            preview_lines.append(f"\n...and {len(plan) - 15} more.")

        preview = "\n".join(preview_lines)
        answer = QMessageBox.question(
            self,
            "Confirm Organization",
            f"These files will be organized:\n\n"
            f"{preview}\n\n"
            f"Continue?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        self.progress.setValue(0)
        moved_files = organize_plan(
            plan,
            progress_callback=self.progress.setValue,
        )

        if moved_files:
            self.undo_history.append(moved_files)

        self.refresh()

        QMessageBox.information(
            self,
            "Organization Complete",
            f"Moved {len(moved_files)} files.\n\n"
            "You can use Undo to reverse this operation."
        )

    def undo_last(self):
        if not self.undo_history:
            QMessageBox.information(
                self,
                "Nothing to undo",
                "There is no organization operation to undo."
            )
            return

        operation = self.undo_history.pop()
        restored = undo_operation(operation)
        self.refresh()

        QMessageBox.information(
            self,
            "Undo Complete",
            f"Restored {restored} files."
        )

    # ========================================================
    # STYLES
    # ========================================================

    def apply_style(self):
        self.setStyleSheet(STYLESHEET)