"""Validated, deterministic custom organization rules."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import fnmatch
import logging
import os
from pathlib import Path
import re
import uuid
from typing import Any, Iterable

from ..categorization import CATEGORIES
from ..config import custom_rules_path
from .json_store import backup_file, read_json, write_json

logger = logging.getLogger(__name__)

RULE_SCHEMA_VERSION = 1
MAX_RULES = 500
MAX_CONDITIONS = 8
CONDITION_KINDS = {
    "name_contains",
    "name_starts",
    "extension",
    "location_glob",
}
DESTINATION_TYPES = {"category", "folder"}
_VALID_EXTENSION = re.compile(r"^\.[A-Za-z0-9][A-Za-z0-9._+-]*$")
_GLOB_CHARS = set("*?[")


class RuleValidationError(ValueError):
    """A rule cannot be safely saved or executed."""


class UnsupportedRuleSchemaError(RuleValidationError):
    """The saved file was written by a newer version of the application."""


@dataclass(frozen=True)
class RuleCondition:
    kind: str
    value: str


@dataclass(frozen=True)
class CustomRule:
    rule_id: str
    name: str
    conditions: tuple[RuleCondition, ...]
    logic: str
    destination_type: str
    destination: str
    priority: int = 100
    enabled: bool = True


@dataclass(frozen=True)
class RuleResolution:
    status: str
    rule: CustomRule | None = None
    competing_rules: tuple[CustomRule, ...] = ()


def new_rule(
    name: str,
    conditions: Iterable[RuleCondition],
    destination_type: str,
    destination: str,
    *,
    logic: str = "all",
    priority: int = 100,
    enabled: bool = True,
) -> CustomRule:
    return CustomRule(
        rule_id=uuid.uuid4().hex,
        name=name,
        conditions=tuple(conditions),
        logic=logic,
        destination_type=destination_type,
        destination=destination,
        priority=priority,
        enabled=enabled,
    )


def _condition_from(value: RuleCondition | dict[str, Any]) -> RuleCondition:
    if isinstance(value, RuleCondition):
        return value
    if not isinstance(value, dict):
        raise RuleValidationError("Each condition must be an object.")
    kind, text = value.get("kind"), value.get("value")
    if not isinstance(kind, str) or not isinstance(text, str):
        raise RuleValidationError("Each condition needs a type and a text value.")
    return RuleCondition(kind, text)


def validate_rule(value: CustomRule | dict[str, Any]) -> CustomRule:
    """Return a normalized rule or raise a useful validation error."""
    if isinstance(value, CustomRule):
        raw = asdict(value)
    elif isinstance(value, dict):
        raw = value
    else:
        raise RuleValidationError("Rule data must be an object.")

    rule_id = raw.get("rule_id")
    name = raw.get("name")
    conditions_raw = raw.get("conditions")
    logic = raw.get("logic", "all")
    destination_type = raw.get("destination_type")
    destination = raw.get("destination")
    priority = raw.get("priority", 100)
    enabled = raw.get("enabled", True)

    if not isinstance(rule_id, str) or not rule_id.strip() or len(rule_id) > 80:
        raise RuleValidationError("Rule identifier is missing or invalid.")
    if not isinstance(name, str) or not name.strip() or len(name.strip()) > 120:
        raise RuleValidationError("Enter a rule name of 1 to 120 characters.")
    if not isinstance(conditions_raw, (list, tuple)) or not 1 <= len(conditions_raw) <= MAX_CONDITIONS:
        raise RuleValidationError(f"Add between 1 and {MAX_CONDITIONS} conditions.")
    if not isinstance(logic, str) or logic not in {"all", "any"}:
        raise RuleValidationError("Condition matching must be AND (all) or OR (any).")
    if (
        not isinstance(destination_type, str)
        or destination_type not in DESTINATION_TYPES
        or not isinstance(destination, str)
    ):
        raise RuleValidationError("Choose a valid category or destination folder.")
    if isinstance(priority, bool) or not isinstance(priority, int) or not -1000 <= priority <= 1000:
        raise RuleValidationError("Priority must be an integer from -1000 to 1000.")
    if not isinstance(enabled, bool):
        raise RuleValidationError("Rule enabled state must be true or false.")

    conditions = tuple(_condition_from(item) for item in conditions_raw)
    cleaned: list[RuleCondition] = []
    for condition in conditions:
        if not isinstance(condition.kind, str) or not isinstance(condition.value, str):
            raise RuleValidationError("Each condition needs a valid type and text value.")
        text = condition.value.strip()
        if condition.kind not in CONDITION_KINDS:
            raise RuleValidationError(f"Unsupported condition type: {condition.kind!r}.")
        if not text or len(text) > 512 or "\0" in text:
            raise RuleValidationError("Condition values must contain 1 to 512 characters.")
        if condition.kind == "extension":
            if not text.startswith("."):
                text = "." + text
            if not _VALID_EXTENSION.fullmatch(text):
                raise RuleValidationError("Enter a valid extension, such as .pdf.")
        if condition.kind == "location_glob":
            normalized = text.replace("\\", "/")
            if any(part == ".." for part in normalized.split("/")):
                raise RuleValidationError("Location patterns cannot contain '..' path segments.")
            text = normalized
        cleaned.append(RuleCondition(condition.kind, text))

    if destination_type == "category":
        if destination not in {*CATEGORIES.keys(), "Others"}:
            raise RuleValidationError("Choose an existing SFM category.")
    else:
        folder = _validated_folder(destination)
        destination = str(folder)

    return CustomRule(
        rule_id=rule_id.strip(),
        name=name.strip(),
        conditions=tuple(cleaned),
        logic=logic,
        destination_type=destination_type,
        destination=destination,
        priority=priority,
        enabled=enabled,
    )


def _validated_folder(value: str | Path) -> Path:
    raw = str(value)
    if not raw.strip() or "\0" in raw:
        raise RuleValidationError("Choose a valid destination folder.")
    path = Path(raw).expanduser()
    if not path.is_absolute():
        raise RuleValidationError("Destination folders must be absolute paths.")
    if ".." in path.parts:
        raise RuleValidationError("Destination folders cannot contain '..' path segments.")
    try:
        resolved = path.resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise RuleValidationError("The destination folder is unavailable.") from error
    if not resolved.is_dir():
        raise RuleValidationError("The destination must be an existing folder.")
    if resolved.parent == resolved or _is_protected_folder(resolved):
        raise RuleValidationError("Choose a regular destination folder, not a system location.")
    return resolved


def _is_protected_folder(path: Path) -> bool:
    """Reject OS and application-data roots that are unsafe organization targets."""
    normalized = str(path).replace("\\", "/").casefold().rstrip("/")
    protected_names = (
        "/etc", "/usr", "/bin", "/sbin", "/lib", "/lib64", "/boot",
        "/dev", "/proc", "/sys", "/var", "/run", "/windows",
        "/program files", "/program files (x86)",
    )
    if any(normalized == item or normalized.startswith(item + "/") for item in protected_names):
        return True
    try:
        config_dir = custom_rules_path().parent.resolve(strict=False)
        path.relative_to(config_dir)
        return True
    except (OSError, ValueError):
        return False


def condition_matches(condition: RuleCondition, path: Path) -> bool:
    """Evaluate one supported condition without reading file contents."""
    path = Path(path)
    value = condition.value
    name = path.name.casefold()
    if condition.kind == "name_contains":
        return value.casefold() in name
    if condition.kind == "name_starts":
        return name.startswith(value.casefold())
    if condition.kind == "extension":
        return path.name.casefold().endswith(value.casefold())
    if condition.kind == "location_glob":
        pattern = value.replace("\\", "/").casefold()
        location = path.parent.as_posix().casefold()
        if _GLOB_CHARS.intersection(pattern):
            return fnmatch.fnmatchcase(location, pattern)
        # A plain folder name matches that path component anywhere; a path
        # pattern without wildcards matches the exact trailing path.
        if "/" not in pattern:
            return any(part.casefold() == pattern for part in path.parent.parts)
        return location == pattern or location.endswith("/" + pattern)
    return False


def rule_matches(rule: CustomRule, path: Path) -> bool:
    rule = validate_rule(rule)
    checks = [condition_matches(condition, Path(path)) for condition in rule.conditions]
    return all(checks) if rule.logic == "all" else any(checks)


def resolve_matching_rules(rules: Iterable[CustomRule], path: Path) -> RuleResolution:
    """Lowest numeric priority wins; tied conflicting destinations require review."""
    matches = [
        validate_rule(rule)
        for rule in rules
        if rule.enabled and rule_matches(rule, path)
    ]
    if not matches:
        return RuleResolution("no_match")
    top_priority = min(rule.priority for rule in matches)
    winners = sorted(
        (rule for rule in matches if rule.priority == top_priority),
        key=lambda rule: rule.rule_id,
    )
    destinations = {
        (rule.destination_type, os.path.normcase(rule.destination))
        for rule in winners
    }
    if len(destinations) > 1:
        return RuleResolution("conflict", competing_rules=tuple(winners))
    return RuleResolution("matched", rule=winners[0], competing_rules=tuple(winners))


class RuleStore:
    """Persistent custom-rule collection with schema validation and recovery."""

    def __init__(self, path: Path | None = None):
        self.path = Path(path) if path else custom_rules_path()
        self.rules: list[CustomRule] = []
        self.read_only_error: str | None = None
        self.load_warnings: list[str] = []
        self.load()

    def load(self) -> list[CustomRule]:
        existed = self.path.exists()
        document = read_json(self.path, None)
        self.read_only_error = None
        self.load_warnings = []
        if document is None:
            self.rules = []
            if existed:
                self.load_warnings.append(
                    "The custom rule file could not be read. A backup was kept; review rules before organizing."
                )
            return list(self.rules)
        if not isinstance(document, dict):
            backup_file(self.path, "invalid")
            self.rules = []
            self.load_warnings.append("The custom rule file has invalid data; a backup was kept.")
            logger.warning("Custom rules file has an invalid top-level value.")
            return list(self.rules)
        version = document.get("schema_version", 1)
        if not isinstance(version, int) or isinstance(version, bool) or version > RULE_SCHEMA_VERSION:
            self.read_only_error = "Custom rules were saved by a newer SFM version."
            self.rules = []
            return list(self.rules)
        raw_rules = document.get("rules")
        if not isinstance(raw_rules, list):
            backup_file(self.path, "invalid")
            self.rules = []
            self.load_warnings.append("The saved rules list is invalid; a backup was kept.")
            logger.warning("Custom rules file has no valid rules list.")
            return list(self.rules)

        loaded: list[CustomRule] = []
        identifiers: set[str] = set()
        invalid_records = False
        for raw in raw_rules[:MAX_RULES]:
            try:
                rule = validate_rule(raw)
            except RuleValidationError as error:
                logger.warning("Skipping invalid saved custom rule: %s", error)
                invalid_records = True
                self.load_warnings.append(f"An invalid saved rule was skipped: {error}")
                continue
            if rule.rule_id in identifiers:
                logger.warning("Skipping duplicate custom rule identifier %s.", rule.rule_id)
                invalid_records = True
                self.load_warnings.append("A duplicate saved rule identifier was skipped.")
                continue
            identifiers.add(rule.rule_id)
            loaded.append(rule)
        if len(raw_rules) > MAX_RULES:
            invalid_records = True
            self.load_warnings.append(f"Only the first {MAX_RULES} saved rules were loaded.")
        if invalid_records:
            backup_file(self.path, "invalid")
        self.rules = loaded
        return list(self.rules)

    def _save(self, updated: list[CustomRule]) -> None:
        if self.read_only_error:
            raise UnsupportedRuleSchemaError(self.read_only_error)
        if len(updated) > MAX_RULES:
            raise RuleValidationError(f"A maximum of {MAX_RULES} custom rules is supported.")
        normalized = [validate_rule(rule) for rule in updated]
        identifiers = [rule.rule_id for rule in normalized]
        if len(identifiers) != len(set(identifiers)):
            raise RuleValidationError("Rule identifiers must be unique.")
        write_json(
            self.path,
            {
                "schema_version": RULE_SCHEMA_VERSION,
                "rules": [asdict(rule) for rule in normalized],
            },
        )
        self.rules = normalized
        self.load_warnings = []

    def add(self, rule: CustomRule) -> None:
        self._save([*self.rules, validate_rule(rule)])

    def update(self, rule: CustomRule) -> None:
        rule = validate_rule(rule)
        if not any(existing.rule_id == rule.rule_id for existing in self.rules):
            raise RuleValidationError("The rule no longer exists.")
        self._save([rule if existing.rule_id == rule.rule_id else existing for existing in self.rules])

    def delete(self, rule_id: str) -> None:
        self._save([rule for rule in self.rules if rule.rule_id != rule_id])

    def set_enabled(self, rule_id: str, enabled: bool) -> None:
        if not isinstance(enabled, bool):
            raise RuleValidationError("Rule enabled state must be true or false.")
        existing = next((rule for rule in self.rules if rule.rule_id == rule_id), None)
        if existing is None:
            raise RuleValidationError("The rule no longer exists.")
        self.update(CustomRule(
            rule_id=existing.rule_id,
            name=existing.name,
            conditions=existing.conditions,
            logic=existing.logic,
            destination_type=existing.destination_type,
            destination=existing.destination,
            priority=existing.priority,
            enabled=enabled,
        ))
