"""
backend/reports.py
==================
Report rendering — populates the Report tab QTreeWidget after organizing
is complete and updates the summary label.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import QTreeWidgetItem

from utils.constants import COLORS, FILE_CATEGORIES, OTHERS_CATEGORY


def show_report(report_tree, report_summary_lbl, report: dict) -> None:
    """
    Populate *report_tree* (QTreeWidget) with results from the organizer.
    Updates *report_summary_lbl* (QLabel) with the summary line.

    Parameters
    ----------
    report_tree        : QTreeWidget  — the Report tab tree widget
    report_summary_lbl : QLabel       — summary label below the tree
    report             : dict         — {category: count, '_errors': count}
    """
    report_tree.clear()

    total_moved = 0
    errors = report.get("_errors", 0)

    # All categories in display order
    display_categories = list(FILE_CATEGORIES.keys()) + [OTHERS_CATEGORY]

    for category in display_categories:
        count = report.get(category, 0)
        if count == 0:
            continue
        item = QTreeWidgetItem([category, str(count)])
        item.setTextAlignment(
            1, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        report_tree.addTopLevelItem(item)
        total_moved += count

    # Totals row
    total_item = QTreeWidgetItem(["TOTAL MOVED", str(total_moved)])
    total_item.setFont(0, QFont("Segoe UI", 13, QFont.Weight.Bold))
    total_item.setFont(1, QFont("Segoe UI", 13, QFont.Weight.Bold))
    total_item.setForeground(0, QColor(COLORS["success"]))
    total_item.setForeground(1, QColor(COLORS["success"]))
    report_tree.addTopLevelItem(total_item)

    if errors:
        err_item = QTreeWidgetItem(["Errors (not moved)", str(errors)])
        err_item.setForeground(0, QColor(COLORS["danger"]))
        err_item.setForeground(1, QColor(COLORS["danger"]))
        report_tree.addTopLevelItem(err_item)

    summary = f"Moved {total_moved} file(s)"
    if errors:
        summary += f"  |  {errors} error(s)"
    report_summary_lbl.setText(summary)
