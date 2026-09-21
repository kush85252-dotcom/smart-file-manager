"""Planning, execution, and undo for file organization."""

import logging
import shutil
from pathlib import Path
from typing import Callable, Iterable

from .file_operations import available_destination, move_path
from ..categorization import category_for

logger = logging.getLogger(__name__)

OrganizePlanItem = tuple[Path, Path, Path]
UndoOperation = list[tuple[Path, Path]]


def build_organize_plan(
    files: Iterable[Path],
    current_folder: Path,
) -> list[OrganizePlanItem]:
    """Build source/category-folder/destination tuples for files in a folder."""
    plan = []

    for path in files:
        try:
            if not path.is_file():
                continue
            category = category_for(path)
        except OSError as error:
            logger.warning("Could not inspect %s: %s", path, error)
            continue

        destination_folder = current_folder / category
        destination = destination_folder / path.name
        plan.append((path, destination_folder, destination))

    return plan


def organize_plan(
    plan: Iterable[OrganizePlanItem],
    progress_callback: Callable[[int], None] | None = None,
) -> UndoOperation:
    """Execute an organization plan and return records usable by undo."""
    plan = list(plan)
    moved_files: UndoOperation = []
    total = len(plan)

    for index, (source, folder, destination) in enumerate(plan):
        try:
            folder.mkdir(parents=True, exist_ok=True)
            destination = available_destination(destination)
            move_path(source, destination)
            moved_files.append((destination, source))
        except (OSError, shutil.Error) as error:
            logger.warning("Could not move %s: %s", source, error)
        except Exception:
            logger.exception("Unexpected error while moving %s", source)

        if progress_callback is not None and total:
            progress_callback(int(((index + 1) / total) * 100))

    return moved_files


def undo_operation(operation: UndoOperation) -> int:
    """Reverse one organization operation and return restored file count."""
    restored = 0

    for current_path, original_path in reversed(operation):
        try:
            if not current_path.exists():
                continue

            target = available_destination(original_path, marker="_restored")
            move_path(current_path, target)
            restored += 1
        except (OSError, shutil.Error) as error:
            logger.warning("Undo failed for %s: %s", current_path, error)
        except Exception:
            logger.exception("Unexpected undo error for %s", current_path)

    return restored
