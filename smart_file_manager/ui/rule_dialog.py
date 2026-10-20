"""Create and edit custom rules without exposing executable user-supplied code."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QDialogButtonBox,
)

from ..categorization import CATEGORIES
from ..services.custom_rules import (
    CONDITION_KINDS,
    CustomRule,
    RuleCondition,
    RuleValidationError,
    new_rule,
    validate_rule,
)

_CONDITION_LABELS = {
    "name_contains": "Filename contains",
    "name_starts": "Filename starts with",
    "extension": "Extension matches",
    "location_glob": "File location matches",
}
_CONDITION_HINTS = {
    "name_contains": "text in filename",
    "name_starts": "prefix",
    "extension": ".pdf",
    "location_glob": "folder name or path pattern",
}


class RuleEditorDialog(QDialog):
    """Modal, keyboard-navigable custom rule editor."""

    def __init__(self, parent=None, rule: CustomRule | None = None):
        super().__init__(parent)
        self._original = rule
        self.rule: CustomRule | None = None
        self.setWindowTitle("Edit Custom Rule" if rule else "Create Custom Rule")
        self.setMinimumWidth(660)

        outer = QVBoxLayout(self)
        form = QFormLayout()
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        self.name_input = QLineEdit(rule.name if rule else "")
        self.name_input.setPlaceholderText("For example, School notes")
        form.addRow("Rule name", self.name_input)

        self.logic_combo = QComboBox()
        self.logic_combo.addItem("Match all conditions (AND)", "all")
        self.logic_combo.addItem("Match any condition (OR)", "any")
        self.logic_combo.setCurrentIndex(0 if not rule or rule.logic == "all" else 1)
        form.addRow("Combine conditions", self.logic_combo)

        self.priority_input = QSpinBox()
        self.priority_input.setRange(-1000, 1000)
        self.priority_input.setValue(rule.priority if rule else 100)
        self.priority_input.setToolTip("Lower numbers take precedence. Equal-priority conflicting rules require review.")
        priority_row = QHBoxLayout()
        priority_row.addWidget(self.priority_input)
        priority_row.addWidget(QLabel("Lower number wins; default is 100."))
        priority_row.addStretch()
        priority_widget = QWidget()
        priority_widget.setLayout(priority_row)
        form.addRow("Priority", priority_widget)

        self.enabled_check = QCheckBox("Enabled")
        self.enabled_check.setChecked(rule.enabled if rule else True)
        form.addRow("Rule state", self.enabled_check)

        self.destination_type = QComboBox()
        self.destination_type.addItem("SFM category", "category")
        self.destination_type.addItem("Existing folder", "folder")
        if rule:
            index = self.destination_type.findData(rule.destination_type)
            if index >= 0:
                self.destination_type.setCurrentIndex(index)
        form.addRow("Destination type", self.destination_type)

        self.category_combo = QComboBox()
        categories = sorted([*CATEGORIES.keys(), "Others"], key=str.casefold)
        self.category_combo.addItems(categories)
        if rule and rule.destination_type == "category":
            index = self.category_combo.findText(rule.destination)
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
        form.addRow("Category", self.category_combo)

        folder_row = QHBoxLayout()
        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText("Choose an existing folder")
        if rule and rule.destination_type == "folder":
            self.folder_input.setText(rule.destination)
        self.folder_browse = QPushButton("Browse…")
        self.folder_browse.clicked.connect(self._choose_folder)
        folder_row.addWidget(self.folder_input, 1)
        folder_row.addWidget(self.folder_browse)
        folder_widget = QWidget()
        folder_widget.setLayout(folder_row)
        form.addRow("Destination folder", folder_widget)
        self._category_widget = self.category_combo
        self._folder_widget = folder_widget
        self.destination_type.currentIndexChanged.connect(self._sync_destination_fields)

        outer.addLayout(form)

        condition_heading = QLabel("Conditions")
        condition_heading.setObjectName("sectionTitle")
        outer.addWidget(condition_heading)
        self.condition_table = QTableWidget(0, 2)
        self.condition_table.setHorizontalHeaderLabels(["Condition", "Value"])
        self.condition_table.horizontalHeader().setStretchLastSection(True)
        self.condition_table.setMinimumHeight(180)
        self.condition_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.condition_table.setTabKeyNavigation(True)
        outer.addWidget(self.condition_table)

        condition_buttons = QHBoxLayout()
        add_button = QPushButton("Add condition")
        remove_button = QPushButton("Remove selected")
        add_button.clicked.connect(self._add_condition)
        remove_button.clicked.connect(self._remove_condition)
        condition_buttons.addWidget(add_button)
        condition_buttons.addWidget(remove_button)
        condition_buttons.addStretch()
        outer.addLayout(condition_buttons)
        outer.addWidget(QLabel(
            "Conditions use AND/OR as selected above. Location accepts a folder name, "
            "a full path, or a wildcard pattern."
        ))

        if rule:
            for condition in rule.conditions:
                self._add_condition(condition)
        else:
            self._add_condition()

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._accept_rule)
        buttons.rejected.connect(self.reject)
        outer.addWidget(buttons)
        self._sync_destination_fields()
        self.name_input.setFocus(Qt.FocusReason.OtherFocusReason)

    def _add_condition(self, condition: RuleCondition | None = None) -> None:
        row = self.condition_table.rowCount()
        self.condition_table.insertRow(row)
        kind_combo = QComboBox()
        for kind in sorted(CONDITION_KINDS, key=lambda item: list(_CONDITION_LABELS).index(item)):
            kind_combo.addItem(_CONDITION_LABELS[kind], kind)
        value_input = QLineEdit(condition.value if condition else "")
        value_input.setPlaceholderText(
            _CONDITION_HINTS.get(condition.kind, "value") if condition else "condition value"
        )
        if condition:
            index = kind_combo.findData(condition.kind)
            if index >= 0:
                kind_combo.setCurrentIndex(index)
        kind_combo.currentIndexChanged.connect(
            lambda _index, combo=kind_combo, field=value_input: field.setPlaceholderText(
                _CONDITION_HINTS.get(combo.currentData(), "condition value")
            )
        )
        self.condition_table.setCellWidget(row, 0, kind_combo)
        self.condition_table.setCellWidget(row, 1, value_input)
        self.condition_table.setRowHeight(row, 38)

    def _remove_condition(self) -> None:
        selected = sorted({index.row() for index in self.condition_table.selectedIndexes()}, reverse=True)
        if not selected and self.condition_table.rowCount():
            selected = [self.condition_table.rowCount() - 1]
        for row in selected:
            self.condition_table.removeRow(row)

    def _choose_folder(self) -> None:
        selected = QFileDialog.getExistingDirectory(self, "Choose Rule Destination")
        if selected:
            self.folder_input.setText(selected)

    def _sync_destination_fields(self, *_args) -> None:
        is_category = self.destination_type.currentData() == "category"
        self._category_widget.setVisible(is_category)
        self._folder_widget.setVisible(not is_category)

    def _accept_rule(self) -> None:
        conditions: list[RuleCondition] = []
        for row in range(self.condition_table.rowCount()):
            kind = self.condition_table.cellWidget(row, 0).currentData()
            value = self.condition_table.cellWidget(row, 1).text()
            conditions.append(RuleCondition(kind=kind, value=value))
        destination_type = self.destination_type.currentData()
        destination = (
            self.category_combo.currentText()
            if destination_type == "category"
            else self.folder_input.text()
        )
        if self._original:
            candidate = CustomRule(
                rule_id=self._original.rule_id,
                name=self.name_input.text(),
                conditions=tuple(conditions),
                logic=self.logic_combo.currentData(),
                destination_type=destination_type,
                destination=destination,
                priority=self.priority_input.value(),
                enabled=self.enabled_check.isChecked(),
            )
        else:
            candidate = new_rule(
                name=self.name_input.text(),
                conditions=conditions,
                logic=self.logic_combo.currentData(),
                destination_type=destination_type,
                destination=destination,
                priority=self.priority_input.value(),
                enabled=self.enabled_check.isChecked(),
            )
        try:
            self.rule = validate_rule(candidate)
        except RuleValidationError as error:
            QMessageBox.warning(self, "Rule needs attention", str(error))
            return
        self.accept()
