"""Main Qt window for Smart File Manager."""

from pathlib import Path
import logging
import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QFont
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
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
    QScrollArea,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..categorization import category_for
from ..config import (
    APP_NAME,
    GITHUB_URL,
    VERSION,
    AppConfig,
    apply_startup_setting,
    default_start_folder,
)
from ..logging_config import configure_logging
from ..services.file_operations import (
    delete_path,
    is_hidden,
    open_file as open_file_operation,
    rename_path,
)
from ..services.organizer import (
    build_organize_plan as build_organize_plan_service,
    organize_plan,
    undo_operation,
)
from ..utils import format_size, modified_date
from .styles import LIGHT_STYLESHEET, STYLESHEET


class SFM_Lite(QMainWindow):
    """The original Smart File Manager window, split from application logic."""

    def __init__(self, config: AppConfig | None = None):
        super().__init__()

        self.setWindowTitle(f"{APP_NAME} {VERSION}")
        self.resize(1150, 700)
        self.config = config or AppConfig()
        self.logger = logging.getLogger(__name__)
        self.settings_widgets = {}
        self.base_font = QFont(QApplication.font())

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
        self.settings_button = self.sidebar_button("⚙  Settings")

        sidebar_layout.addWidget(self.dashboard_button)
        sidebar_layout.addWidget(self.files_button)
        sidebar_layout.addWidget(self.organize_button)
        sidebar_layout.addWidget(self.settings_button)

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
        self.settings_page = self.create_settings_page()

        self.stack.addWidget(self.dashboard_page)
        self.stack.addWidget(self.files_page)
        self.stack.addWidget(self.organize_page)
        self.stack.addWidget(self.settings_page)

        self.dashboard_button.clicked.connect(
            lambda: self.stack.setCurrentIndex(0)
        )

        self.files_button.clicked.connect(
            lambda: self.stack.setCurrentIndex(1)
        )

        self.organize_button.clicked.connect(
            lambda: self.stack.setCurrentIndex(2)
        )
        self.settings_button.clicked.connect(
            lambda: self.stack.setCurrentIndex(3)
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
    # SETTINGS
    # ========================================================

    def create_settings_page(self):
        page = QWidget()
        outer = QVBoxLayout(page)
        outer.setContentsMargins(30, 30, 30, 30)
        outer.setSpacing(12)

        heading = QLabel("Settings")
        heading.setObjectName("heading")
        intro = QLabel(
            "SFM saves changes automatically. Settings are local to this computer."
        )
        intro.setObjectName("description")
        outer.addWidget(heading)
        outer.addWidget(intro)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 10, 10, 10)
        layout.setSpacing(14)

        general = self.settings_section("General")
        self.add_setting_checkbox(
            general, "start_with_windows", "Start SFM with Windows",
            "Launch SFM automatically after signing in (Windows only).",
            enabled=os.name == "nt",
        )
        self.add_setting_checkbox(
            general, "show_hidden_files", "Show hidden files",
            "Include hidden and dot-prefixed files in folder listings.",
        )
        self.add_setting_checkbox(
            general, "confirm_before_organizing", "Confirm before organizing",
            "Ask for confirmation before moving files.",
        )
        self.add_setting_checkbox(
            general, "create_category_folders", "Create category folders automatically",
            "Create missing destination folders during organization.",
        )
        layout.addWidget(general)

        organization = self.settings_section("Organization")
        self.add_setting_checkbox(
            organization, "scan_subfolders", "Scan subfolders",
            "Include files in nested folders when organizing.",
        )
        mode_row = QHBoxLayout()
        mode_label = QLabel("Organization mode")
        mode_label.setMinimumWidth(250)
        mode_combo = QComboBox()
        mode_combo.addItem("By category (recommended)", "category")
        mode_combo.addItem("By file extension", "extension")
        mode_combo.currentIndexChanged.connect(
            lambda: self.save_combo_setting("organization_mode", mode_combo)
        )
        self.settings_widgets["organization_mode"] = mode_combo
        mode_row.addWidget(mode_label)
        mode_row.addWidget(mode_combo, 1)
        organization.layout().addLayout(mode_row)
        layout.addWidget(organization)

        appearance = self.settings_section("Appearance")
        theme_row = QHBoxLayout()
        theme_label = QLabel("Theme")
        theme_label.setMinimumWidth(250)
        theme_combo = QComboBox()
        theme_combo.addItem("Dark", "dark")
        theme_combo.addItem("Light", "light")
        theme_combo.currentIndexChanged.connect(
            lambda: self.save_combo_setting("theme", theme_combo)
        )
        self.settings_widgets["theme"] = theme_combo
        theme_row.addWidget(theme_label)
        theme_row.addWidget(theme_combo, 1)
        appearance.layout().addLayout(theme_row)

        scale_row = QHBoxLayout()
        scale_label = QLabel("UI scaling")
        scale_label.setMinimumWidth(250)
        scale_combo = QComboBox()
        for value in (100, 110, 125, 150):
            scale_combo.addItem(f"{value}%", value)
        scale_combo.currentIndexChanged.connect(
            lambda: self.save_combo_setting("ui_scale", scale_combo)
        )
        self.settings_widgets["ui_scale"] = scale_combo
        scale_row.addWidget(scale_label)
        scale_row.addWidget(scale_combo, 1)
        appearance.layout().addLayout(scale_row)
        layout.addWidget(appearance)

        safety = self.settings_section("Safety")
        self.add_setting_checkbox(
            safety, "preview_before_apply", "Preview operations before applying",
            "Show the planned moves before an organization operation runs.",
        )
        self.add_setting_checkbox(
            safety, "keep_undo_history", "Keep undo history",
            "Keep completed organization operations available for Undo.",
        )
        self.add_setting_checkbox(
            safety, "use_recycle_bin",
            "Send deleted files to the Recycle Bin instead of permanently deleting them",
            "Uses the native desktop trash when deleting from the file browser.",
        )
        layout.addWidget(safety)

        activity = self.settings_section("Notifications / Activity")
        self.add_setting_checkbox(
            activity, "show_notifications", "Show operation notifications",
            "Show completion dialogs after organization, undo, and delete actions.",
        )
        self.add_setting_checkbox(
            activity, "activity_logging", "Keep activity logging enabled",
            "Write operation events to SFM's local activity log.",
        )
        layout.addWidget(activity)

        about = self.settings_section("About")
        about_text = QLabel(
            f"<b>{APP_NAME}</b><br>"
            f"Version {VERSION}<br><br>"
            "A lightweight, local-first file manager for organizing files safely.<br><br>"
            f'<a href="{GITHUB_URL}">GitHub</a><br>'
            "License: not specified in this source distribution."
        )
        about_text.setOpenExternalLinks(True)
        about_text.setObjectName("description")
        about.layout().addWidget(about_text)
        layout.addWidget(about)

        reset_button = QPushButton("Reset to Defaults")
        reset_button.clicked.connect(self.reset_settings)
        layout.addWidget(reset_button, 0, Qt.AlignmentFlag.AlignLeft)
        self.settings_status = QLabel("Changes are saved automatically.")
        self.settings_status.setObjectName("status")
        layout.addWidget(self.settings_status)
        layout.addStretch()

        scroll.setWidget(content)
        outer.addWidget(scroll)
        self.load_settings_into_widgets()
        return page

    def settings_section(self, title):
        section = QFrame()
        section.setObjectName("settingsCard")
        section.setLayout(QVBoxLayout())
        section.layout().setContentsMargins(18, 14, 18, 14)
        section.layout().setSpacing(10)
        heading = QLabel(title)
        heading.setObjectName("sectionTitle")
        section.layout().addWidget(heading)
        return section

    def add_setting_checkbox(self, section, key, text, description, enabled=True):
        row = QHBoxLayout()
        checkbox = QCheckBox(text)
        checkbox.setEnabled(enabled)
        checkbox.stateChanged.connect(
            lambda state, setting=key: self.save_checkbox_setting(setting, state)
        )
        details = QLabel(description)
        details.setObjectName("description")
        details.setWordWrap(True)
        row.addWidget(checkbox)
        row.addWidget(details, 1)
        section.layout().addLayout(row)
        self.settings_widgets[key] = checkbox

    def load_settings_into_widgets(self):
        for key, widget in self.settings_widgets.items():
            value = self.config.get(key)
            if isinstance(widget, QCheckBox):
                widget.blockSignals(True)
                widget.setChecked(bool(value))
                widget.blockSignals(False)
            elif isinstance(widget, QComboBox):
                index = widget.findData(value)
                widget.blockSignals(True)
                widget.setCurrentIndex(max(index, 0))
                widget.blockSignals(False)

    def save_checkbox_setting(self, key, state):
        self.save_setting(key, bool(state))

    def save_combo_setting(self, key, combo):
        self.save_setting(key, combo.currentData())

    def save_setting(self, key, value):
        self.config.set(key, value)
        try:
            self.config.save()
            if key == "start_with_windows":
                applied, message = apply_startup_setting(bool(value))
                if not applied and os.name == "nt":
                    self.settings_status.setText(f"Could not update Windows startup: {message}")
            elif key == "activity_logging":
                configure_logging(bool(value))
            elif key in {"show_hidden_files", "scan_subfolders"}:
                self.refresh()
            elif key in {"theme", "ui_scale"}:
                self.apply_style()
            self.settings_status.setText("Saved just now.")
        except OSError as error:
            self.settings_status.setText(f"Could not save settings: {error}")

    def reset_settings(self):
        answer = QMessageBox.question(
            self,
            "Reset Settings",
            "Reset all SFM settings to their safe defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self.config.reset()
        self.load_settings_into_widgets()
        self.apply_style()
        self.refresh()
        if os.name == "nt":
            apply_startup_setting(False)
        configure_logging(True)
        self.settings_status.setText("Settings reset to defaults.")

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

        if not self.config.get("show_hidden_files"):
            items = [item for item in items if not is_hidden(item)]

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
            delete_path(path, use_recycle_bin=self.config.get("use_recycle_bin"))
            self.logger.info(
                "Deleted %s (%s)",
                path,
                "recycle bin" if self.config.get("use_recycle_bin") else "permanent",
            )
            self.refresh()
            self.notify_operation(
                "Delete Complete",
                f"{path.name} was sent to the Recycle Bin."
                if self.config.get("use_recycle_bin")
                else f"{path.name} was permanently deleted.",
            )
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
        files = self.files
        if self.config.get("scan_subfolders"):
            files = []
            try:
                for path in self.current_folder.rglob("*"):
                    if path.is_file() and (
                        self.config.get("show_hidden_files") or not is_hidden(path)
                    ):
                        files.append(path)
            except OSError as error:
                self.logger.warning("Could not scan subfolders: %s", error)
        return build_organize_plan_service(
            files,
            self.current_folder,
            self.config.get("organization_mode"),
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
        needs_prompt = (
            self.config.get("preview_before_apply")
            or self.config.get("confirm_before_organizing")
        )
        if needs_prompt:
            title = (
                "Preview Organization"
                if self.config.get("preview_before_apply")
                else "Confirm Organization"
            )
            prompt = (
                f"These files will be organized:\n\n{preview}\n\n"
                f"Apply this operation?"
                if self.config.get("preview_before_apply")
                else f"Organize {len(plan)} files now?"
            )
            answer = QMessageBox.question(
                self,
                title,
                prompt,
                QMessageBox.StandardButton.Yes |
                QMessageBox.StandardButton.No
            )
            if answer != QMessageBox.StandardButton.Yes:
                return

        self.progress.setValue(0)
        moved_files = organize_plan(
            plan,
            progress_callback=self.progress.setValue,
            create_category_folders=self.config.get("create_category_folders"),
        )

        if moved_files and self.config.get("keep_undo_history"):
            self.undo_history.append(moved_files)
        self.logger.info("Organized %d files in %s.", len(moved_files), self.current_folder)

        self.refresh()

        self.notify_operation(
            "Organization Complete",
            f"Moved {len(moved_files)} files.\n\n"
            "You can use Undo to reverse this operation.",
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
        self.logger.info("Undid organization and restored %d files.", restored)
        self.refresh()

        self.notify_operation("Undo Complete", f"Restored {restored} files.")

    def notify_operation(self, title, message):
        """Show a dialog only when the user enabled operation notifications."""
        self.status_label.setText(message.split("\n", 1)[0])
        if self.config.get("show_notifications"):
            QMessageBox.information(self, title, message)

    # ========================================================
    # STYLES
    # ========================================================

    def apply_style(self):
        scale = self.config.get("ui_scale") / 100
        font = QFont(self.base_font)
        font.setPointSizeF(max(9.0, 14.0 * scale))
        QApplication.instance().setFont(font)
        self.setStyleSheet(
            LIGHT_STYLESHEET
            if self.config.get("theme") == "light"
            else STYLESHEET
        )