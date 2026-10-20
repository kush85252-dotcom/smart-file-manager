"""Planning, execution, and undo for file organization."""

import logging
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Callable, Iterable

from .file_operations import available_destination, move_path
from ..categorization import organization_folder_for
from .custom_rules import CustomRule, RuleValidationError, resolve_matching_rules

logger = logging.getLogger(__name__)

OrganizePlanItem = tuple[Path, Path, Path]
UndoOperation = list[tuple[Path, Path]]


@dataclass(frozen=True)
class PlanEntry:
    source: Path
    destination_folder: Path | None
    destination: Path | None
    reason: str
    rule_id: str | None = None
    rule_name: str | None = None
    warning: str | None = None
    issue: str | None = None


@dataclass(frozen=True)
class UndoResult:
    restored: int
    success: bool
    message: str = ""


def build_rule_aware_plan(
    files: Iterable[Path],
    current_folder: Path,
    organization_mode: str = "category",
    rules: Iterable[CustomRule] = (),
    *,
    create_category_folders: bool = True,
) -> list[PlanEntry]:
    """Combine the existing category plan with explicit custom-rule precedence."""
    files = [Path(path) for path in files]
    current_folder = Path(current_folder)
    built_in = build_organize_plan(files, current_folder, organization_mode)
    built_in_by_path = {
        os.path.normcase(str(source.resolve(strict=False))): (folder, destination)
        for source, folder, destination in built_in
    }
    entries: list[PlanEntry] = []

    for source in files:
        try:
            if source.is_symlink():
                entries.append(PlanEntry(
                    source, None, None, "Symbolic links are not moved as regular files.",
                    issue=f"Source is a symbolic link and was not followed: {source}",
                ))
                continue
            if not source.is_file():
                continue
            source_key = os.path.normcase(str(source.resolve(strict=False)))
            resolution = resolve_matching_rules(rules, source)
        except (OSError, RuntimeError, RuleValidationError) as error:
            entries.append(PlanEntry(source, None, None, "Could not inspect file.", issue=str(error)))
            continue

        if resolution.status == "conflict":
            names = ", ".join(rule.name for rule in resolution.competing_rules)
            entries.append(PlanEntry(
                source,
                None,
                None,
                "Equal-priority custom rules match this file.",
                issue=f"Review conflicting rules: {names}.",
            ))
            continue

        if resolution.status == "matched" and resolution.rule:
            rule = resolution.rule
            if rule.destination_type == "category":
                folder = current_folder / rule.destination
            else:
                folder = Path(rule.destination)
                if not folder.is_dir():
                    entries.append(PlanEntry(
                        source, folder, None, f"Matched rule: {rule.name}",
                        rule.rule_id, rule.name,
                        issue=f"Rule destination is no longer an available folder: {folder}",
                    ))
                    continue
            destination = folder / source.name
            reason = f"Matched rule '{rule.name}' using {rule.logic.upper()} conditions."
            rule_id, rule_name = rule.rule_id, rule.name
        else:
            built_in_item = built_in_by_path.get(source_key)
            if not built_in_item:
                continue
            folder, destination = built_in_item
            reason = f"Built-in file-type category: {organization_folder_for(source, organization_mode)}."
            rule_id, rule_name = None, None

        try:
            if destination.resolve(strict=False) == source.resolve(strict=False):
                continue
            if folder.exists() and not folder.is_dir():
                entries.append(PlanEntry(
                    source, folder, None, reason, rule_id, rule_name,
                    issue=f"Destination path is not a folder: {folder}",
                ))
                continue
            if not folder.exists() and not create_category_folders:
                entries.append(PlanEntry(
                    source, folder, None, reason, rule_id, rule_name,
                    issue=(
                        f"Destination folder does not exist and automatic folder "
                        f"creation is disabled: {folder}"
                    ),
                ))
                continue
            warning = None
            if destination.exists() or destination.is_symlink():
                prior_destination = destination
                destination = available_destination(destination)
                warning = (
                    f"Destination already exists; the proposed name is {destination.name} "
                    f"instead of overwriting {prior_destination.name}."
                )
            entries.append(PlanEntry(
                source=source,
                destination_folder=folder,
                destination=destination,
                reason=reason,
                rule_id=rule_id,
                rule_name=rule_name,
                warning=warning,
            ))
        except (OSError, RuntimeError) as error:
            entries.append(PlanEntry(
                source, folder, None, reason, rule_id, rule_name,
                issue=f"Could not validate destination: {error}",
            ))
    return entries


def build_organize_plan(
    files: Iterable[Path],
    current_folder: Path,
    organization_mode: str = "category",
) -> list[OrganizePlanItem]:
    """Build source/category-folder/destination tuples for files in a folder."""
    plan = []

    for path in files:
        try:
            if not path.is_file():
                continue
            category = organization_folder_for(path, organization_mode)
            # A recursive scan should be idempotent: do not move files that
            # are already inside their selected destination folder.
            if path.parent.name == category:
                continue
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
    create_category_folders: bool = True,
    error_callback: Callable[[str], None] | None = None,
) -> UndoOperation:
    """Execute an organization plan and return records usable by undo."""
    plan = list(plan)
    moved_files: UndoOperation = []
    total = len(plan)

    for index, (source, folder, destination) in enumerate(plan):
        failure = None
        try:
            if not folder.exists():
                if not create_category_folders:
                    failure = f"Skipped {source}: destination folder does not exist: {folder}"
                else:
                    folder.mkdir(parents=True, exist_ok=True)
            elif not folder.is_dir():
                failure = f"Skipped {source}: destination is not a folder: {folder}"
            if failure is None and (destination.exists() or destination.is_symlink()):
                failure = f"Skipped {source}: destination already exists: {destination}"
            if failure is None:
                move_path(source, destination)
                moved_files.append((destination, source))
        except OSError as error:
            failure = f"Could not move {source}: {error}"
        except Exception:
            logger.exception("Unexpected error while moving %s", source)
            failure = f"Unexpected error while moving {source}; check the activity log."

        if failure:
            logger.warning("%s", failure)
            if error_callback is not None:
                error_callback(failure)

        if progress_callback is not None and total:
            progress_callback(int(((index + 1) / total) * 100))

    return moved_files


def undo_operation_detailed(operation: UndoOperation) -> UndoResult:
    """Preflight every path, then reverse exactly without choosing alternate names."""
    moves = [(Path(current), Path(original)) for current, original in operation]
    if not moves:
        return UndoResult(0, False, "There are no recorded file moves to reverse.")

    problems: list[str] = []
    current_paths: set[str] = set()
    original_paths: set[str] = set()
    for current_path, original_path in moves:
        current_key = os.path.normcase(str(current_path.resolve(strict=False)))
        original_key = os.path.normcase(str(original_path.resolve(strict=False)))
        if current_key in current_paths or original_key in original_paths:
            problems.append("The operation contains duplicate file paths.")
            break
        current_paths.add(current_key)
        original_paths.add(original_key)
        if not current_path.is_file():
            problems.append(f"Expected moved file is missing: {current_path}")
        if original_path.exists() or original_path.is_symlink():
            problems.append(f"Original location is occupied: {original_path}")
        if not original_path.parent.is_dir():
            problems.append(f"Original folder is unavailable: {original_path.parent}")
    if problems:
        return UndoResult(0, False, "\n".join(problems))

    restored = 0
    for current_path, original_path in reversed(moves):
        try:
            move_path(current_path, original_path)
            restored += 1
        except OSError as error:
            logger.warning("Undo failed for %s: %s", current_path, error)
            return UndoResult(
                restored,
                False,
                f"Undo stopped after restoring {restored} file(s): {error}",
            )
    return UndoResult(restored, True, "")


def preflight_history_undo(record: dict) -> str:
    """Check a persisted operation against the current filesystem before asking."""
    moves = record.get("moves")
    if not isinstance(moves, list) or not moves:
        return "There are no recorded file moves to reverse."
    problems: list[str] = []
    seen_sources: set[str] = set()
    seen_destinations: set[str] = set()
    for move in moves:
        if not isinstance(move, dict) or move.get("result") != "moved" or move.get("reversed"):
            continue
        source = move.get("source_path")
        destination = move.get("destination_path")
        if not isinstance(source, str) or not isinstance(destination, str):
            problems.append("A history record contains invalid paths.")
            continue
        original_path, current_path = Path(source), Path(destination)
        source_key = os.path.normcase(str(original_path.resolve(strict=False)))
        destination_key = os.path.normcase(str(current_path.resolve(strict=False)))
        if source_key in seen_sources or destination_key in seen_destinations:
            problems.append("The history record contains duplicate paths.")
            continue
        seen_sources.add(source_key)
        seen_destinations.add(destination_key)
        if not current_path.is_file():
            problems.append(f"Expected moved file is missing: {current_path}")
            continue
        if original_path.exists() or original_path.is_symlink():
            problems.append(f"Original location is occupied: {original_path}")
        if not original_path.parent.is_dir():
            problems.append(f"Original folder is unavailable: {original_path.parent}")
        try:
            stat = current_path.stat()
        except OSError as error:
            problems.append(f"Could not inspect {current_path}: {error}")
            continue
        expected_size = move.get("size_bytes")
        expected_mtime = move.get("mtime_ns")
        expected_device = move.get("device_id")
        expected_file_id = move.get("file_id")
        if isinstance(expected_size, int) and stat.st_size != expected_size:
            problems.append(f"The moved file's size changed: {current_path}")
        if isinstance(expected_mtime, int) and stat.st_mtime_ns != expected_mtime:
            problems.append(f"The moved file was modified: {current_path}")
        if isinstance(expected_device, int) and stat.st_dev != expected_device:
            problems.append(f"The moved file's filesystem identity changed: {current_path}")
        if isinstance(expected_file_id, int) and stat.st_ino != expected_file_id:
            problems.append(f"The moved file was replaced: {current_path}")
    return "\n".join(problems)


def undo_history_record_detailed(record: dict) -> UndoResult:
    """Validate saved file metadata and paths, then reverse one complete record."""
    problem = preflight_history_undo(record)
    if problem:
        return UndoResult(0, False, problem)
    moves = [
        (Path(move["destination_path"]), Path(move["source_path"]))
        for move in record["moves"]
        if move.get("result") == "moved" and not move.get("reversed")
    ]
    return undo_operation_detailed(moves)


def undo_operation(operation: UndoOperation) -> int:
    """Compatibility wrapper returning the safely restored file count."""
    return undo_operation_detailed(operation).restored
