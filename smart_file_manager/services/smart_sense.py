"""Explainable local Smart Sense suggestions using deterministic signals."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
import re

from ..categorization import category_for

_NAME_CATEGORIES = {
    "Documents": {
        "document", "documents", "doc", "docs", "note", "notes", "report",
        "invoice", "receipt", "bill", "contract", "school", "homework",
        "assignment", "lecture", "resume", "cv", "passport", "manual",
    },
    "Images": {
        "photo", "photos", "image", "images", "screenshot", "screenshots",
        "camera", "picture", "pictures",
    },
    "Videos": {"video", "videos", "movie", "movies", "film", "recording"},
    "Audio": {"audio", "music", "song", "songs", "podcast", "voice"},
    "Spreadsheets": {"spreadsheet", "workbook", "budget", "finance"},
    "Presentations": {"presentation", "presentations", "slides", "deck"},
    "Archives": {"backup", "backups", "archive", "archives", "compressed"},
    "Code": {"source", "code", "project", "projects", "script", "scripts"},
}

# Folder cues can supply a category and optionally a useful subfolder label.
_LOCATION_CATEGORIES = {
    "school": ("Documents", "School"),
    "college": ("Documents", "College"),
    "university": ("Documents", "University"),
    "work": ("Documents", "Work"),
    "office": ("Documents", "Work"),
    "documents": ("Documents", None),
    "document": ("Documents", None),
    "papers": ("Documents", None),
    "images": ("Images", None),
    "photos": ("Images", None),
    "pictures": ("Images", None),
    "camera": ("Images", "Camera"),
    "videos": ("Videos", None),
    "movies": ("Videos", None),
    "music": ("Audio", None),
    "audio": ("Audio", None),
    "spreadsheets": ("Spreadsheets", None),
    "presentations": ("Presentations", None),
    "archives": ("Archives", None),
    "projects": ("Code", "Projects"),
}

_TOKEN_RE = re.compile(r"[a-z0-9]+")


@dataclass(frozen=True)
class SmartSuggestion:
    suggestion_id: str
    source: Path
    category: str | None
    destination: Path | None
    signals: tuple[str, ...]
    explanation: str
    conflicts: tuple[str, ...] = ()

    @property
    def actionable(self) -> bool:
        return self.destination is not None and not self.conflicts


def _name_evidence(path: Path) -> set[str]:
    tokens = set(_TOKEN_RE.findall(path.stem.casefold()))
    return {
        category
        for category, keywords in _NAME_CATEGORIES.items()
        if tokens.intersection(keywords)
    }


def _location_evidence(path: Path) -> tuple[str | None, str | None, str | None]:
    """Use the nearest recognized folder; avoid letting distant ancestors dominate."""
    for parent in path.parents:
        cue = _LOCATION_CATEGORIES.get(parent.name.casefold())
        if cue:
            return cue[0], cue[1], parent.name
    return None, None, None


def suggest_for_file(path: Path, organization_root: Path) -> SmartSuggestion | None:
    """Return a recommendation without modifying the file or its directories."""
    path = Path(path)
    root = Path(organization_root)
    if not path.is_file():
        return None

    evidence: list[tuple[str, str]] = []
    file_category = category_for(path)
    if file_category != "Others":
        evidence.append(("file type", file_category))

    name_categories = _name_evidence(path)
    if len(name_categories) == 1:
        evidence.append(("file name", next(iter(name_categories))))
    elif len(name_categories) > 1:
        evidence.append(("file name", " / ".join(sorted(name_categories))))

    location_category, location_subfolder, location_name = _location_evidence(path)
    if location_category:
        evidence.append(("current folder", location_category))

    categories = {category for _, category in evidence if " / " not in category}
    conflicting_name = any(" / " in category for _, category in evidence)
    conflict_categories = sorted(categories)
    conflicts: list[str] = []
    if conflicting_name:
        conflicts.append("The filename contains keywords for more than one category.")
    if len(conflict_categories) > 1:
        conflicts.append(
            "Signals disagree: " + ", ".join(
                f"{signal} → {category}" for signal, category in evidence
            )
        )
    if conflicts:
        category = None
        destination = None
    elif conflict_categories:
        category = conflict_categories[0]
        target = root / category
        if location_category == category and location_subfolder:
            target = target / location_subfolder
        destination = target / path.name
        try:
            if destination.resolve(strict=False) == path.resolve(strict=False):
                return None
        except (OSError, RuntimeError):
            pass
    else:
        # With no evidence, abstain instead of guessing.
        return None

    signal_text = tuple(
        f"{signal}: {category}"
        for signal, category in evidence
    )
    if category is None:
        explanation = "No destination is selected because the available signals conflict."
    else:
        parts = [f"{signal} indicates {category}" for signal, category in evidence]
        if location_name and location_subfolder and location_category == category:
            parts.append(f"the {location_name} folder suggests a {location_subfolder} subfolder")
        explanation = "Suggested from " + "; ".join(parts) + "."

    digest_source = (
        f"{path.resolve(strict=False)}|{category}|{destination}|{'|'.join(signal_text)}"
    )
    suggestion_id = hashlib.sha256(digest_source.encode("utf-8", "replace")).hexdigest()[:24]
    return SmartSuggestion(
        suggestion_id=suggestion_id,
        source=path,
        category=category,
        destination=destination,
        signals=signal_text,
        explanation=explanation,
        conflicts=tuple(conflicts),
    )


def suggest_for_files(paths: list[Path], organization_root: Path) -> list[SmartSuggestion]:
    """Analyze a file collection in input order without filesystem changes."""
    suggestions = [
        suggestion
        for path in paths
        if (suggestion := suggest_for_file(Path(path), organization_root)) is not None
    ]
    return suggestions
