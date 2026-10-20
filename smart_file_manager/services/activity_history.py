"""Persistent operation records used for safe, cross-session Undo."""

from __future__ import annotations

from datetime import datetime, timezone
import logging
from pathlib import Path
import uuid
from typing import Iterable

from ..config import activity_history_path
from .json_store import backup_file, read_json, write_json

logger = logging.getLogger(__name__)

HISTORY_SCHEMA_VERSION = 1
MAX_HISTORY_OPERATIONS = 250


class HistoryStoreError(ValueError):
    """History cannot be safely updated."""


class HistoryStore:
    """Validated JSON history; file state is always rechecked before undo."""

    def __init__(self, path: Path | None = None):
        self.path = Path(path) if path else activity_history_path()
        self.operations: list[dict] = []
        self.read_only_error: str | None = None
        self.load()

    @staticmethod
    def _valid_operation(raw: object) -> dict | None:
        if not isinstance(raw, dict):
            return None
        operation_id = raw.get("operation_id")
        operation_type = raw.get("operation_type")
        moves = raw.get("moves")
        if not isinstance(operation_id, str) or not operation_id.strip() or len(operation_id) > 80:
            return None
        if (
            not isinstance(operation_type, str)
            or operation_type not in {"organization", "custom_rule", "smart_sense"}
        ):
            return None
        if not isinstance(moves, list):
            return None

        clean_moves: list[dict] = []
        for move in moves:
            if not isinstance(move, dict):
                continue
            source = move.get("source_path")
            destination = move.get("destination_path")
            if not isinstance(source, str) or not source or not isinstance(destination, str) or not destination:
                continue
            size = move.get("size_bytes")
            modified = move.get("mtime_ns")
            clean_moves.append({
                "source_path": source,
                "destination_path": destination,
                "result": "moved" if move.get("result") == "moved" else "failed",
                "reversed": move.get("reversed", False) is True,
                "size_bytes": size if isinstance(size, int) and not isinstance(size, bool) else None,
                "mtime_ns": modified if isinstance(modified, int) and not isinstance(modified, bool) else None,
                "device_id": (
                    move.get("device_id")
                    if isinstance(move.get("device_id"), int) and not isinstance(move.get("device_id"), bool)
                    else None
                ),
                "file_id": (
                    move.get("file_id")
                    if isinstance(move.get("file_id"), int) and not isinstance(move.get("file_id"), bool)
                    else None
                ),
            })

        timestamp = raw.get("timestamp")
        if not isinstance(timestamp, str) or not timestamp:
            timestamp = "unknown"
        result = raw.get("result")
        if not isinstance(result, str) or result not in {"completed", "partial", "failed", "reversed"}:
            result = "completed"
        related_rule_ids = raw.get("related_rule_ids", [])
        related_suggestion_ids = raw.get("related_suggestion_ids", [])
        if not isinstance(related_rule_ids, list):
            related_rule_ids = []
        if not isinstance(related_suggestion_ids, list):
            related_suggestion_ids = []

        return {
            "operation_id": operation_id,
            "operation_type": operation_type,
            "timestamp": timestamp,
            "result": result,
            "related_rule_ids": [item for item in related_rule_ids if isinstance(item, str)],
            "related_suggestion_ids": [
                item for item in related_suggestion_ids if isinstance(item, str)
            ],
            "moves": clean_moves,
            "reversed": raw.get("reversed", result == "reversed") is True,
            "undone_at": raw.get("undone_at") if isinstance(raw.get("undone_at"), str) else None,
            "undo_error": raw.get("undo_error") if isinstance(raw.get("undo_error"), str) else None,
        }

    def load(self) -> list[dict]:
        document = read_json(self.path, None)
        self.read_only_error = None
        if document is None:
            self.operations = []
            return list(self.operations)
        if not isinstance(document, dict):
            backup_file(self.path, "invalid")
            self.operations = []
            logger.warning("Activity history has an invalid top-level value.")
            return list(self.operations)

        version = document.get("schema_version", 1)
        if not isinstance(version, int) or isinstance(version, bool) or version > HISTORY_SCHEMA_VERSION:
            self.read_only_error = "Activity history was saved by a newer SFM version."
            self.operations = []
            return list(self.operations)

        raw_operations = document.get("operations")
        if not isinstance(raw_operations, list):
            backup_file(self.path, "invalid")
            self.operations = []
            logger.warning("Activity history has no valid operations list.")
            return list(self.operations)

        operations: list[dict] = []
        seen: set[str] = set()
        invalid_records = False
        for raw in raw_operations[-MAX_HISTORY_OPERATIONS:]:
            operation = self._valid_operation(raw)
            if operation is None:
                invalid_records = True
                continue
            if operation["operation_id"] in seen:
                logger.warning("Skipping duplicate history operation identifier.")
                invalid_records = True
                continue
            seen.add(operation["operation_id"])
            operations.append(operation)
        if len(raw_operations) > MAX_HISTORY_OPERATIONS:
            invalid_records = True
        if invalid_records:
            backup_file(self.path, "invalid")
        self.operations = operations
        return list(self.operations)

    def _save(self, operations: list[dict]) -> None:
        if self.read_only_error:
            raise HistoryStoreError(self.read_only_error)
        write_json(
            self.path,
            {
                "schema_version": HISTORY_SCHEMA_VERSION,
                "operations": operations[-MAX_HISTORY_OPERATIONS:],
            },
        )
        self.operations = operations[-MAX_HISTORY_OPERATIONS:]

    def append(
        self,
        operation_type: str,
        moved_files: Iterable[tuple[Path, Path]],
        *,
        result: str = "completed",
        related_rule_ids: Iterable[str] = (),
        related_suggestion_ids: Iterable[str] = (),
    ) -> dict | None:
        """Record each actual move as original source -> final destination."""
        if (
            not isinstance(operation_type, str)
            or operation_type not in {"organization", "custom_rule", "smart_sense"}
        ):
            raise HistoryStoreError("Unsupported operation type.")
        if not isinstance(result, str) or result not in {"completed", "partial", "failed"}:
            raise HistoryStoreError("Unsupported operation result.")

        move_records = []
        for destination, source in moved_files:
            destination = Path(destination)
            source = Path(source)
            try:
                stat = destination.stat()
                size_bytes, mtime_ns = stat.st_size, stat.st_mtime_ns
                device_id, file_id = stat.st_dev, stat.st_ino
            except OSError:
                size_bytes, mtime_ns, device_id, file_id = None, None, None, None
            move_records.append({
                "source_path": str(source),
                "destination_path": str(destination),
                "result": "moved",
                "reversed": False,
                "size_bytes": size_bytes,
                "mtime_ns": mtime_ns,
                "device_id": device_id,
                "file_id": file_id,
            })
        if not move_records:
            return None

        record = {
            "operation_id": uuid.uuid4().hex,
            "operation_type": operation_type,
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "result": result,
            "related_rule_ids": sorted(set(related_rule_ids)),
            "related_suggestion_ids": sorted(set(related_suggestion_ids)),
            "moves": move_records,
            "reversed": False,
            "undone_at": None,
            "undo_error": None,
        }
        self._save([*self.operations, record])
        return record

    def last_undoable(self) -> dict | None:
        for operation in reversed(self.operations):
            if operation["reversed"] or operation["result"] == "reversed":
                continue
            if any(move["result"] == "moved" and not move["reversed"] for move in operation["moves"]):
                return operation
        return None

    def mark_reversed(self, operation_id: str) -> None:
        updated: list[dict] = []
        found = False
        for operation in self.operations:
            item = dict(operation)
            if item["operation_id"] == operation_id:
                found = True
                item["reversed"] = True
                item["result"] = "reversed"
                item["undone_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
                item["undo_error"] = None
                item["moves"] = [dict(move, reversed=True) for move in item["moves"]]
            updated.append(item)
        if not found:
            raise HistoryStoreError("The operation is no longer in history.")
        self._save(updated)

    def record_undo_error(self, operation_id: str, message: str) -> None:
        updated: list[dict] = []
        for operation in self.operations:
            item = dict(operation)
            if item["operation_id"] == operation_id:
                item["undo_error"] = message[:1000]
            updated.append(item)
        self._save(updated)
