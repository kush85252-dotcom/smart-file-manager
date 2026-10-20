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
    QDialog,
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
    MAX_FAVORITES,
    RECENT_LIMIT_CHOICES,
    VERSION,
    AppConfig,
    apply_startup_setting,
    default_start_folder,
)
from ..logging_config import configure_logging
from ..services.activity_history import HistoryStore, HistoryStoreError
from ..services.custom_rules import (
    CustomRule,
    RuleStore,
    RuleValidationError,
    resolve_matching_rules,
    rule_matches,
)
from ..services.file_operations import (
    available_destination,
    delete_path,
    is_hidden,
    open_file as open_file_operation,
    rename_path,
)
from ..services.folder_lists import (
    add_favorite,
    folder_exists,
    push_recent,
    remove_favorite,
)
from ..services.organizer import (
    PlanEntry,
    build_rule_aware_plan,
    organize_plan,
    preflight_history_undo,
    undo_history_record_detailed,
)
from ..services.scanner import iter_files
from ..services.smart_sense import SmartSuggestion, suggest_for_files
from ..utils import format_size, modified_date
from .folder_list_page import FolderListPage
from .monitor_page import MonitorPage
from .rule_dialog import RuleEditorDialog
from .scan_panel import ScanPanel
from .styles import LIGHT_STYLESHEET, STYLESHEET

# Stack positions.  The first four keep their original order.
PAGE_OVERVIEW, PAGE_FILES, PAGE_ORGANIZE, PAGE_SETTINGS = 0, 1, 2, 3
PAGE_FAVORITES, PAGE_RECENT, PAGE_MONITOR = 4, 5, 6
PAGE_RULES, PAGE_SMART_SENSE = 7, 8


class SFM_Lite(QMainWindow):
    """The original Smart File Manager window, split from application logic."""

    def __init__(self, config: AppConfig | None = None):
        super().__init__()

        self.setWindowTitle(f"{APP_NAME} {VERSION}")
        self.resize(1150, 700)
        self.setMinimumSize(900, 620)
        self.config = config or AppConfig()
        self.logger = logging.getLogger(__name__)
        self.settings_widgets = {}
        self.base_font = QFont(QApplication.font())
        self.rule_store = RuleStore()
        self.history_store = HistoryStore()
        self.dismissed_suggestion_ids: set[str] = set()
        self.smart_suggestions: list[SmartSuggestion] = []

        self.current_folder = default_start_folder()

        # Used for navigation
        self.history = []
        self.history_index = -1

        # Undo operations
        self.undo_history = []

        self.files = []

        self.build_ui()
        self.apply_style()

        # The start-up folder is not a user "visit", so it is not added to Recent.
        self.navigate_to(self.current_folder, save_history=True, record_recent=False)
        self.refresh_folder_lists()

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

        title = QLabel(f"SFM {VERSION}")
        title.setObjectName("appTitle")

        version = QLabel(f"{APP_NAME} {VERSION}")
        version.setObjectName("version")

        sidebar_layout.addWidget(title)
        sidebar_layout.addWidget(version)
        sidebar_layout.addSpacing(25)

        # "dashboard_button"/"dashboard_page" keep their original attribute
        # names; the page is now labelled Overview.
        self.dashboard_button = self.sidebar_button("📊  Overview")
        self.files_button = self.sidebar_button("📁  Files")
        self.organize_button = self.sidebar_button("🧹  Organize")
        self.favorites_button = self.sidebar_button("⭐  Favorites")
        self.recent_button = self.sidebar_button("🕘  Recent Folders")
        self.monitor_button = self.sidebar_button("📡  Live Monitor")
        self.settings_button = self.sidebar_button("⚙  Settings")
        self.rules_button = self.sidebar_button("Custom Rules")
        self.smart_sense_button = self.sidebar_button("Smart Sense")

        self.nav_buttons = {
            PAGE_OVERVIEW: self.dashboard_button,
            PAGE_FILES: self.files_button,
            PAGE_ORGANIZE: self.organize_button,
            PAGE_FAVORITES: self.favorites_button,
            PAGE_RECENT: self.recent_button,
            PAGE_MONITOR: self.monitor_button,
            PAGE_SETTINGS: self.settings_button,
            PAGE_RULES: self.rules_button,
            PAGE_SMART_SENSE: self.smart_sense_button,
        }
        for button in self.nav_buttons.values():
            sidebar_layout.addWidget(button)

        sidebar_layout.addStretch()

        info = QLabel(
            f"SFM {VERSION}\n"
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
        self.favorites_page = self.create_favorites_page()
        self.recent_page = self.create_recent_page()
        self.monitor_page = MonitorPage(lambda: self.current_folder)
        self.rules_page = self.create_rules_page()
        self.smart_sense_page = self.create_smart_sense_page()

        # Order must match the PAGE_* constants above.
        for page in (
            self.dashboard_page, self.files_page, self.organize_page,
            self.settings_page, self.favorites_page, self.recent_page,
            self.monitor_page, self.rules_page, self.smart_sense_page,
        ):
            self.stack.addWidget(page)

        for index, button in self.nav_buttons.items():
            button.clicked.connect(lambda _checked=False, i=index: self.show_page(i))

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stack, 1)
        self.show_page(PAGE_OVERVIEW)

    def show_page(self, index):
        """Switch page and mark the matching sidebar button as current."""
        if index in (PAGE_FAVORITES, PAGE_RECENT):
            self.refresh_folder_lists()  # re-check which folders still exist
        elif index == PAGE_RULES:
            self.refresh_rule_list()
        elif index == PAGE_SMART_SENSE:
            self.refresh_smart_suggestions()
        self.stack.setCurrentIndex(index)
        for page_index, button in self.nav_buttons.items():
            button.setProperty("current", page_index == index)
            button.style().unpolish(button)
            button.style().polish(button)

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

        heading = QLabel("Overview")
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

        self.scan_panel = ScanPanel(
            folder_provider=lambda: self.current_folder,
            hidden_provider=lambda: bool(self.config.get("show_hidden_files")),
        )
        layout.addWidget(self.scan_panel)
        layout.addStretch()

        # Scrollable so the scan results stay reachable on small screens.
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(page)
        return scroll

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

    def create_rules_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(26, 26, 26, 26)
        layout.setSpacing(12)

        heading = QLabel("Custom Rules")
        heading.setObjectName("heading")
        description = QLabel(
            "Create local rules that participate in an organization preview. "
            "Saving or enabling a rule never moves files."
        )
        description.setObjectName("description")
        layout.addWidget(heading)
        layout.addWidget(description)

        self.rule_store_status = QLabel()
        self.rule_store_status.setObjectName("status")
        layout.addWidget(self.rule_store_status)

        self.rules_table = QTableWidget(0, 5)
        self.rules_table.setHorizontalHeaderLabels(
            ["Rule", "Conditions", "Destination", "Priority", "State"]
        )
        self.rules_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.rules_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.rules_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.rules_table.setAlternatingRowColors(True)
        self.rules_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.rules_table.verticalHeader().setVisible(False)
        layout.addWidget(self.rules_table, 1)

        actions = QHBoxLayout()
        self.rule_add_button = QPushButton("Create rule")
        self.rule_edit_button = QPushButton("Edit")
        self.rule_toggle_button = QPushButton("Enable / disable")
        self.rule_delete_button = QPushButton("Delete")
        self.rule_preview_button = QPushButton("Preview matches")
        for button in (
            self.rule_add_button,
            self.rule_edit_button,
            self.rule_toggle_button,
            self.rule_delete_button,
            self.rule_preview_button,
        ):
            actions.addWidget(button)
        self.rule_add_button.clicked.connect(self.create_custom_rule)
        self.rule_edit_button.clicked.connect(self.edit_custom_rule)
        self.rule_toggle_button.clicked.connect(self.toggle_custom_rule)
        self.rule_delete_button.clicked.connect(self.delete_custom_rule)
        self.rule_preview_button.clicked.connect(self.preview_custom_rule)
        layout.addLayout(actions)
        return page

    def create_smart_sense_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(26, 26, 26, 26)
        layout.setSpacing(12)

        heading = QLabel("Smart Sense")
        heading.setObjectName("heading")
        description = QLabel(
            "Local, rule-based suggestions from file type, filename, and nearby folders. "
            "Nothing moves unless you choose a suggestion and confirm it."
        )
        description.setObjectName("description")
        layout.addWidget(heading)
        layout.addWidget(description)

        self.smart_sense_status = QLabel("Choose a folder or refresh to review suggestions.")
        self.smart_sense_status.setObjectName("status")
        layout.addWidget(self.smart_sense_status)

        self.sense_table = QTableWidget(0, 4)
        self.sense_table.setHorizontalHeaderLabels(
            ["File", "Suggested destination", "Signals", "Explanation / conflicts"]
        )
        self.sense_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.sense_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.sense_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.sense_table.setAlternatingRowColors(True)
        self.sense_table.setWordWrap(True)
        self.sense_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.sense_table.verticalHeader().setVisible(False)
        layout.addWidget(self.sense_table, 1)

        actions = QHBoxLayout()
        self.sense_refresh_button = QPushButton("Refresh suggestions")
        self.sense_move_button = QPushButton("Preview and move selected")
        self.sense_dismiss_button = QPushButton("Dismiss selected")
        self.sense_refresh_button.clicked.connect(self.refresh_smart_suggestions)
        self.sense_move_button.clicked.connect(self.move_selected_suggestion)
        self.sense_dismiss_button.clicked.connect(self.dismiss_selected_suggestion)
        actions.addWidget(self.sense_refresh_button)
        actions.addWidget(self.sense_move_button)
        actions.addWidget(self.sense_dismiss_button)
        actions.addStretch()
        layout.addLayout(actions)
        return page

    # ========================================================
    # CUSTOM RULES
    # ========================================================

    @staticmethod
    def _condition_label(condition):
        labels = {
            "name_contains": "filename contains",
            "name_starts": "filename starts with",
            "extension": "extension matches",
            "location_glob": "location matches",
        }
        return f'{labels.get(condition.kind, condition.kind)} "{condition.value}"'

    def refresh_rule_list(self):
        self.rule_store.load()
        self.rules_table.setRowCount(0)
        if self.rule_store.read_only_error:
            self.rule_store_status.setText(self.rule_store.read_only_error)
            for button in (
                self.rule_add_button,
                self.rule_edit_button,
                self.rule_toggle_button,
                self.rule_delete_button,
            ):
                button.setEnabled(False)
        else:
            status_text = (
                "No rules yet. Rules only affect an organization after its preview is confirmed."
                if not self.rule_store.rules
                else f"{len(self.rule_store.rules)} saved rule(s). Lower priority numbers take precedence."
            )
            if self.rule_store.load_warnings:
                status_text = "Review required: " + " ".join(self.rule_store.load_warnings)
            self.rule_store_status.setText(status_text)
            for button in (
                self.rule_add_button,
                self.rule_edit_button,
                self.rule_toggle_button,
                self.rule_delete_button,
            ):
                button.setEnabled(True)
        self.rule_preview_button.setEnabled(bool(self.rule_store.rules))

        rules = sorted(self.rule_store.rules, key=lambda rule: (rule.priority, rule.name.casefold()))
        for row, rule in enumerate(rules):
            self.rules_table.insertRow(row)
            condition_text = f" {rule.logic.upper()} ".join(
                self._condition_label(condition) for condition in rule.conditions
            )
            destination = (
                rule.destination
                if rule.destination_type == "folder"
                else f"Category: {rule.destination}"
            )
            values = [
                rule.name,
                condition_text,
                destination,
                str(rule.priority),
                "Enabled" if rule.enabled else "Disabled",
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                if column == 0:
                    item.setData(Qt.ItemDataRole.UserRole, rule.rule_id)
                self.rules_table.setItem(row, column, item)
            self.rules_table.setRowHeight(row, 42)

    def _selected_custom_rule(self) -> CustomRule | None:
        row = self.rules_table.currentRow()
        if row < 0:
            return None
        item = self.rules_table.item(row, 0)
        if item is None:
            return None
        rule_id = item.data(Qt.ItemDataRole.UserRole)
        return next((rule for rule in self.rule_store.rules if rule.rule_id == rule_id), None)

    def create_custom_rule(self):
        dialog = RuleEditorDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted or dialog.rule is None:
            return
        try:
            self.rule_store.add(dialog.rule)
        except (OSError, RuleValidationError) as error:
            QMessageBox.critical(self, "Could not save rule", str(error))
            return
        self.refresh_rule_list()
        self.status_label.setText(f"Saved rule: {dialog.rule.name}")

    def edit_custom_rule(self):
        rule = self._selected_custom_rule()
        if rule is None:
            QMessageBox.information(self, "Select a rule", "Choose a rule to edit.")
            return
        dialog = RuleEditorDialog(self, rule)
        if dialog.exec() != QDialog.DialogCode.Accepted or dialog.rule is None:
            return
        try:
            self.rule_store.update(dialog.rule)
        except (OSError, RuleValidationError) as error:
            QMessageBox.critical(self, "Could not save rule", str(error))
            return
        self.refresh_rule_list()
        self.status_label.setText(f"Updated rule: {dialog.rule.name}")

    def toggle_custom_rule(self):
        rule = self._selected_custom_rule()
        if rule is None:
            QMessageBox.information(self, "Select a rule", "Choose a rule to enable or disable.")
            return
        try:
            self.rule_store.set_enabled(rule.rule_id, not rule.enabled)
        except (OSError, RuleValidationError) as error:
            QMessageBox.critical(self, "Could not update rule", str(error))
            return
        self.refresh_rule_list()

    def delete_custom_rule(self):
        rule = self._selected_custom_rule()
        if rule is None:
            QMessageBox.information(self, "Select a rule", "Choose a rule to delete.")
            return
        answer = QMessageBox.question(
            self,
            "Delete custom rule",
            f"Delete '{rule.name}'?\n\nThis only removes the rule; it does not change any files.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            self.rule_store.delete(rule.rule_id)
        except (OSError, RuleValidationError) as error:
            QMessageBox.critical(self, "Could not delete rule", str(error))
            return
        self.refresh_rule_list()

    def _current_scan_files(self) -> list[Path]:
        if self.config.get("scan_subfolders"):
            return list(iter_files(
                self.current_folder,
                include_hidden=bool(self.config.get("show_hidden_files")),
            ))
        return [Path(path) for path in self.files if Path(path).is_file()]

    def preview_custom_rule(self):
        rule = self._selected_custom_rule()
        if rule is None:
            QMessageBox.information(self, "Select a rule", "Choose a rule to preview.")
            return
        matches = []
        for source in self._current_scan_files():
            if not rule_matches(rule, source):
                continue
            destination_folder = (
                self.current_folder / rule.destination
                if rule.destination_type == "category"
                else Path(rule.destination)
            )
            destination = destination_folder / source.name
            resolution = resolve_matching_rules(self.rule_store.rules, source)
            note = ""
            if not rule.enabled:
                note = "  [DISABLED: this rule is not applied during organization]"
            elif resolution.status == "conflict" and any(
                candidate.rule_id == rule.rule_id for candidate in resolution.competing_rules
            ):
                note = "  [CONFLICT: equal-priority rules disagree; no destination is selected]"
            elif resolution.status == "matched" and resolution.rule:
                if resolution.rule.rule_id != rule.rule_id:
                    winner = resolution.rule
                    winner_folder = (
                        self.current_folder / winner.destination
                        if winner.destination_type == "category"
                        else Path(winner.destination)
                    )
                    note = (
                        f"  [OVERRIDDEN by higher-priority rule '{winner.name}'; "
                        f"active destination: {winner_folder / source.name}]"
                    )
                elif destination.exists() or destination.is_symlink():
                    note = f"  [EXISTS: would propose {available_destination(destination)}]"
            elif rule.destination_type == "folder" and not destination_folder.is_dir():
                note = "  [INVALID: the configured destination folder is unavailable]"
            elif (
                not destination_folder.exists()
                and not self.config.get("create_category_folders")
            ):
                note = "  [SKIP: destination folder creation is disabled]"
            elif destination.exists() or destination.is_symlink():
                note = f"  [EXISTS: would propose {available_destination(destination)}]"
            matches.append(
                f"{source}\n  → {destination}{note}\n"
                f"  Matched rule: {rule.name}; {rule.logic.upper()} conditions."
            )
        if not matches:
            text = f"No files in the current scan match '{rule.name}'."
        else:
            text = "\n\n".join(matches[:25])
            if len(matches) > 25:
                text += f"\n\n…and {len(matches) - 25} more match(es)."
        QMessageBox.information(self, f"Rule preview: {rule.name}", text)

    # ========================================================
    # SMART SENSE
    # ========================================================

    def refresh_smart_suggestions(self):
        try:
            suggestions = suggest_for_files(self._current_scan_files(), self.current_folder)
        except OSError as error:
            self.smart_sense_status.setText(f"Could not scan this folder: {error}")
            return
        self.smart_suggestions = [
            suggestion
            for suggestion in suggestions
            if suggestion.suggestion_id not in self.dismissed_suggestion_ids
        ]
        self.sense_table.setRowCount(0)
        for row, suggestion in enumerate(self.smart_suggestions):
            self.sense_table.insertRow(row)
            values = [
                str(suggestion.source),
                str(suggestion.destination) if suggestion.destination else "Needs review",
                "; ".join(suggestion.signals) or "No matching signal",
                " ".join((suggestion.explanation, *suggestion.conflicts)),
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                if column == 0:
                    item.setData(Qt.ItemDataRole.UserRole, suggestion.suggestion_id)
                self.sense_table.setItem(row, column, item)
            self.sense_table.setRowHeight(row, 72)
        if not self.smart_suggestions:
            self.smart_sense_status.setText("No suggestions for the current folder.")
        else:
            actionable = sum(suggestion.actionable for suggestion in self.smart_suggestions)
            self.smart_sense_status.setText(
                f"{len(self.smart_suggestions)} suggestion(s); {actionable} can be reviewed for a move."
            )

    def _selected_suggestion(self) -> SmartSuggestion | None:
        row = self.sense_table.currentRow()
        if row < 0:
            return None
        item = self.sense_table.item(row, 0)
        if item is None:
            return None
        suggestion_id = item.data(Qt.ItemDataRole.UserRole)
        return next(
            (suggestion for suggestion in self.smart_suggestions
             if suggestion.suggestion_id == suggestion_id),
            None,
        )

    def dismiss_selected_suggestion(self):
        suggestion = self._selected_suggestion()
        if suggestion is None:
            QMessageBox.information(self, "Select a suggestion", "Choose a suggestion to dismiss.")
            return
        self.dismissed_suggestion_ids.add(suggestion.suggestion_id)
        self.refresh_smart_suggestions()
        self.smart_sense_status.setText("Suggestion dismissed for this session.")

    def move_selected_suggestion(self):
        suggestion = self._selected_suggestion()
        if suggestion is None:
            QMessageBox.information(self, "Select a suggestion", "Choose a suggestion to review.")
            return
        if not suggestion.actionable:
            QMessageBox.warning(
                self,
                "Suggestion needs review",
                "\n".join(suggestion.conflicts) or "No safe destination is available.",
            )
            return
        if not suggestion.source.is_file():
            QMessageBox.warning(self, "File unavailable", "The source file is no longer available.")
            self.refresh_smart_suggestions()
            return

        destination = suggestion.destination
        warning = ""
        if destination.exists() or destination.is_symlink():
            prior = destination
            destination = available_destination(destination)
            warning = (
                f"\n\nThe suggested destination already exists. To avoid overwriting it, "
                f"the file would be saved as:\n{destination}"
            )
        prompt = (
            f"Source:\n{suggestion.source}\n\n"
            f"Suggested destination:\n{destination}\n\n"
            f"Reason: {suggestion.explanation}"
            + (f"\n\nReview: {'; '.join(suggestion.conflicts)}" if suggestion.conflicts else "")
            + warning
            + "\n\nMove this file now?"
        )
        answer = QMessageBox.question(
            self,
            "Confirm Smart Sense move",
            prompt,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        execution_errors = []
        moved = organize_plan(
            [(suggestion.source, destination.parent, destination)],
            error_callback=execution_errors.append,
        )
        if not moved:
            QMessageBox.warning(
                self,
                "File was not moved",
                "\n".join(execution_errors)
                or "The file or destination changed after preview. Refresh suggestions and review again.",
            )
            self.refresh_smart_suggestions()
            return
        history_error = None
        if self.config.get("keep_undo_history"):
            try:
                self.history_store.append(
                    "smart_sense",
                    moved,
                    related_suggestion_ids=[suggestion.suggestion_id],
                )
            except (OSError, HistoryStoreError) as error:
                history_error = str(error)
                QMessageBox.warning(
                    self,
                    "Move completed; history was not saved",
                    f"The file moved, but persistent Undo could not be recorded:\n{history_error}",
                )
        self.dismissed_suggestion_ids.add(suggestion.suggestion_id)
        self.refresh()
        self.refresh_smart_suggestions()
        completion_message = f"Moved {suggestion.source.name}."
        if history_error:
            self.status_label.setText(completion_message)
        else:
            self.notify_operation("Smart Sense Move Complete", completion_message)

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

        recent_row = QHBoxLayout()
        recent_label = QLabel("Recent folders to remember")
        recent_label.setMinimumWidth(250)
        recent_combo = QComboBox()
        for value in RECENT_LIMIT_CHOICES:
            recent_combo.addItem(str(value), value)
        recent_combo.currentIndexChanged.connect(
            lambda: self.save_combo_setting("recent_limit", recent_combo)
        )
        self.settings_widgets["recent_limit"] = recent_combo
        recent_row.addWidget(recent_label)
        recent_row.addWidget(recent_combo, 1)
        general.layout().addLayout(recent_row)

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
            f'<a href="{GITHUB_URL}">https://github.com/kush85252-dotcom/smart-file-manager</a><br>'
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
            elif key == "recent_limit":
                trimmed = self.config.get("recent_folders")[: int(value)]
                self.config.set("recent_folders", trimmed)
                self.config.save()
                self.refresh_folder_lists()
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
        self.config.reset()  # keeps favorites and recent folders
        self.load_settings_into_widgets()
        self.apply_style()
        self.refresh()
        self.refresh_folder_lists()
        if os.name == "nt":
            apply_startup_setting(False)
        configure_logging(True)
        self.settings_status.setText("Settings reset to defaults.")

    # ========================================================
    # NAVIGATION
    # ========================================================

    def navigate_to(self, folder, save_history=True, record_recent=True):
        folder = Path(folder)

        if not folder.exists() or not folder.is_dir():
            return

        previous = (self.current_folder, list(self.history), self.history_index)

        if save_history:
            # Remove future history
            if self.history_index < len(self.history) - 1:
                self.history = self.history[:self.history_index + 1]

            self.history.append(folder)
            self.history_index += 1

        self.current_folder = folder
        if not self.load_folder():
            # Could not open it (e.g. permission denied): stay where we were
            # instead of leaving the window pointing at an unreadable folder.
            self.current_folder, self.history, self.history_index = previous
            return
        if record_recent:
            self.record_recent_folder(folder)

    def load_folder(self):
        """Show the current folder.  Returns True if it could be listed."""
        try:
            items = list(self.current_folder.iterdir())
        except PermissionError:
            QMessageBox.warning(
                self,
                "Permission denied",
                "You don't have permission to open this folder."
            )
            return False
        except OSError as error:
            self.logger.warning("Could not list %s: %s", self.current_folder, error)
            QMessageBox.warning(
                self,
                "Couldn't open folder",
                str(error)
            )
            return False

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
        return True

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
        if self.load_folder():
            self.record_recent_folder(self.current_folder)

    def go_forward(self):
        if self.history_index >= len(self.history) - 1:
            return

        self.history_index += 1
        self.current_folder = self.history[self.history_index]
        if self.load_folder():
            self.record_recent_folder(self.current_folder)

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
        if new_name in {".", ".."} or "/" in new_name or "\\" in new_name:
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
        return build_rule_aware_plan(
            self._current_scan_files(),
            self.current_folder,
            self.config.get("organization_mode"),
            self.rule_store.rules,
            create_category_folders=bool(self.config.get("create_category_folders")),
        )

    def organize_files(self):
        if self.rule_store.read_only_error or self.rule_store.load_warnings:
            QMessageBox.warning(
                self,
                "Custom rules need review",
                self.rule_store.read_only_error
                or "One or more saved rules could not be loaded. Review the Rules page before organizing so no saved rule is ignored.",
            )
            return
        plan = self.build_organize_plan()

        if not plan:
            QMessageBox.information(
                self,
                "Nothing to organize",
                "There are no files to organize."
            )
            return

        blocking = [entry for entry in plan if entry.issue]
        preview_lines = []
        for entry in plan[:15]:
            if entry.issue:
                preview_lines.append(
                    f"REVIEW REQUIRED\n{entry.source}\n  {entry.issue}"
                )
                continue
            preview_lines.append(
                f"{entry.source}\n  → {entry.destination}\n"
                f"  Reason: {entry.reason}"
            )
            if entry.warning:
                preview_lines.append(f"  Conflict: {entry.warning}")

        if len(plan) > 15:
            preview_lines.append(f"\n...and {len(plan) - 15} more.")

        preview = "\n".join(preview_lines)
        if blocking:
            QMessageBox.warning(
                self,
                "Review organization rules",
                "No files were moved. Resolve these rule or path conflicts, then preview again:\n\n"
                + preview,
            )
            return

        needs_prompt = (
            self.config.get("preview_before_apply")
            or self.config.get("confirm_before_organizing")
            or any(entry.rule_id for entry in plan)
        )
        if needs_prompt:
            title = "Preview Organization" if self.config.get("preview_before_apply") else "Confirm Organization"
            prompt = f"Review the source, reason, and proposed destination for each file:\n\n{preview}\n\nApply this operation?"
            answer = QMessageBox.question(
                self,
                title,
                prompt,
                QMessageBox.StandardButton.Yes |
                QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return

        self.progress.setValue(0)
        execution_errors = []
        moved_files = organize_plan(
            [
                (entry.source, entry.destination_folder, entry.destination)
                for entry in plan
                if entry.destination_folder is not None and entry.destination is not None
            ],
            progress_callback=self.progress.setValue,
            create_category_folders=self.config.get("create_category_folders"),
            error_callback=execution_errors.append,
        )

        history_error = None
        if moved_files and self.config.get("keep_undo_history"):
            try:
                operation_type = "custom_rule" if any(entry.rule_id for entry in plan) else "organization"
                self.history_store.append(
                    operation_type,
                    moved_files,
                    result="completed" if len(moved_files) == len(plan) else "partial",
                    related_rule_ids=[
                        entry.rule_id for entry in plan if entry.rule_id is not None
                    ],
                )
            except (OSError, HistoryStoreError) as error:
                history_error = str(error)
        self.logger.info("Organized %d files in %s.", len(moved_files), self.current_folder)

        self.refresh()

        message = f"Moved {len(moved_files)} file(s)."
        if self.config.get("keep_undo_history") and not history_error and moved_files:
            message += "\n\nUndo is available from the Organize page."
        if history_error:
            message += f"\n\nThe move completed, but persistent Undo could not be saved:\n{history_error}"
        self.status_label.setText(message.split("\n", 1)[0])
        if execution_errors or history_error:
            if execution_errors:
                message += "\n\nFiles not moved:\n" + "\n".join(execution_errors[:10])
                if len(execution_errors) > 10:
                    message += f"\n…and {len(execution_errors) - 10} more."
            QMessageBox.warning(self, "Organization completed with warnings", message)
        elif self.config.get("show_notifications"):
            QMessageBox.information(self, "Organization Complete", message)

    def undo_last(self):
        self.history_store.load()
        if self.history_store.read_only_error:
            QMessageBox.warning(self, "Undo unavailable", self.history_store.read_only_error)
            return
        operation = self.history_store.last_undoable()
        if operation is None:
            QMessageBox.information(
                self,
                "Nothing to undo",
                "There is no saved file operation that can currently be undone."
            )
            return

        problem = preflight_history_undo(operation)
        if problem:
            try:
                self.history_store.record_undo_error(operation["operation_id"], problem)
            except (OSError, HistoryStoreError):
                self.logger.exception("Could not update the activity history after failed Undo.")
            QMessageBox.warning(self, "Undo stopped", problem)
            return

        move_count = sum(
            move.get("result") == "moved" and not move.get("reversed")
            for move in operation["moves"]
        )
        answer = QMessageBox.question(
            self,
            "Confirm Undo",
            f"Restore {move_count} file(s) to their original locations?\n\n"
            "Undo will stop rather than overwrite a file or use a different path.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        result = undo_history_record_detailed(operation)
        if not result.success:
            try:
                self.history_store.record_undo_error(
                    operation["operation_id"], result.message
                )
            except (OSError, HistoryStoreError):
                self.logger.exception("Could not update the activity history after failed Undo.")
            QMessageBox.warning(self, "Undo stopped", result.message)
            return
        try:
            self.history_store.mark_reversed(operation["operation_id"])
        except (OSError, HistoryStoreError) as error:
            QMessageBox.warning(
                self,
                "Undo completed; history update failed",
                f"Files were restored, but their history status could not be saved:\n{error}",
            )
        restored = result.restored
        self.logger.info("Undid operation and restored %d files.", restored)
        self.refresh()

        self.notify_operation("Undo Complete", f"Restored {restored} files.")

    def notify_operation(self, title, message):
        """Show a dialog only when the user enabled operation notifications."""
        self.status_label.setText(message.split("\n", 1)[0])
        if self.config.get("show_notifications"):
            QMessageBox.information(self, title, message)

    # ========================================================
    # FAVORITES / RECENT FOLDERS
    # ========================================================

    def create_favorites_page(self):
        page = FolderListPage(
            "Favorites",
            "Folders you want one click away. They are saved between sessions.",
            "No favorites yet. Open a folder in Files, then choose 'Add Current Folder'.",
            allow_add=True,
        )
        page.add_current_requested.connect(
            lambda: self.add_favorite_folder(self.current_folder)
        )
        page.add_folder_requested.connect(self.add_favorite_from_dialog)
        page.open_requested.connect(
            lambda path: self.open_folder_from_list(path, "Favorites")
        )
        page.remove_requested.connect(self.remove_favorite_folder)
        return page

    def create_recent_page(self):
        page = FolderListPage(
            "Recent Folders",
            "Folders you opened recently, newest first. Only folders are tracked, never files.",
            "No recent folders yet. Folders you open in Files appear here.",
            allow_clear=True,
        )
        page.open_requested.connect(
            lambda path: self.open_folder_from_list(path, "Recent Folders")
        )
        page.remove_requested.connect(self.remove_recent_folder)
        page.clear_requested.connect(self.clear_recent_folders)
        return page

    def refresh_folder_lists(self):
        self.favorites_page.set_paths(self.config.get("favorites"))
        self.recent_page.set_paths(self.config.get("recent_folders"))

    def save_folder_lists(self):
        """Persist favorites/recents; a failed write must never block the UI."""
        try:
            self.config.save()
        except OSError as error:
            self.logger.warning("Could not save folder lists: %s", error)

    def record_recent_folder(self, folder):
        updated = push_recent(
            self.config.get("recent_folders"),
            str(folder),
            self.config.get("recent_limit"),
        )
        self.config.set("recent_folders", updated)
        self.save_folder_lists()
        self.recent_page.set_paths(updated)

    def add_favorite_from_dialog(self):
        chosen = QFileDialog.getExistingDirectory(
            self, "Choose a folder to add to Favorites", str(self.current_folder)
        )
        if chosen:
            self.add_favorite_folder(Path(chosen))

    def add_favorite_folder(self, folder):
        favorites = self.config.get("favorites")
        updated, added = add_favorite(favorites, str(folder), MAX_FAVORITES)
        if added:
            self.config.set("favorites", updated)
            self.save_folder_lists()
            message = f"Added to Favorites: {folder}"
        elif len(favorites) >= MAX_FAVORITES:
            message = f"Favorites is full ({MAX_FAVORITES} folders). Remove one first."
        else:
            message = "That folder is already in Favorites."
        self.favorites_page.set_paths(self.config.get("favorites"))
        self.favorites_page.status_label.setText(message)

    def remove_favorite_folder(self, path):
        updated, removed = remove_favorite(self.config.get("favorites"), path)
        if removed:
            self.config.set("favorites", updated)
            self.save_folder_lists()
        self.favorites_page.set_paths(updated)

    def remove_recent_folder(self, path):
        updated, removed = remove_favorite(self.config.get("recent_folders"), path)
        if removed:
            self.config.set("recent_folders", updated)
            self.save_folder_lists()
        self.recent_page.set_paths(updated)

    def clear_recent_folders(self):
        answer = QMessageBox.question(
            self,
            "Clear Recent Folders",
            "Clear the list of recent folders? Your files and favorites are not affected.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self.config.set("recent_folders", [])
        self.save_folder_lists()
        self.recent_page.set_paths([])

    def open_folder_from_list(self, path, source):
        """Open a saved folder, or offer to drop it if it no longer exists."""
        if not folder_exists(path):
            answer = QMessageBox.question(
                self,
                "Folder not found",
                f"This folder is missing or not reachable right now "
                f"(it may be on a drive that is not connected):\n\n{path}\n\n"
                f"Remove it from {source}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer == QMessageBox.StandardButton.Yes:
                if source == "Favorites":
                    self.remove_favorite_folder(path)
                else:
                    self.remove_recent_folder(path)
            return
        self.navigate_to(Path(path), save_history=True)
        self.show_page(PAGE_FILES)

    # ========================================================
    # SHUTDOWN
    # ========================================================

    def closeEvent(self, event):
        """Stop background work before the window goes away."""
        self.monitor_page.stop_monitoring()
        self.scan_panel.shutdown()
        event.accept()

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