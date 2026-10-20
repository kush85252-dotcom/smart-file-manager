# Smart File Manager

[![Latest Release](https://img.shields.io/github/v/release/kush85252-dotcom/smart-file-manager?label=latest%20release)](https://github.com/kush85252-dotcom/smart-file-manager/releases)
[![License](https://img.shields.io/github/license/kush85252-dotcom/smart-file-manager)](https://github.com/kush85252-dotcom/smart-file-manager/blob/smart-file-manager-main/LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/kush85252-dotcom/smart-file-manager?style=flat)](https://github.com/kush85252-dotcom/smart-file-manager/stargazers)
[![GitHub Issues](https://img.shields.io/github/issues/kush85252-dotcom/smart-file-manager)](https://github.com/kush85252-dotcom/smart-file-manager/issues)
[![Last Commit](https://img.shields.io/github/last-commit/kush85252-dotcom/smart-file-manager?branch=smart-file-manager-main)](https://github.com/kush85252-dotcom/smart-file-manager/commits/smart-file-manager-main)
[![Platform](https://img.shields.io/badge/platform-Windows-0078D4?logo=windows)](https://github.com/kush85252-dotcom/smart-file-manager)
[![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)](https://www.python.org/)

A local-first file manager and organizer for Windows, built with Python and PyQt6.

Smart File Manager (SFM) brings file browsing, scanning, categorization, monitoring, and organization tools together in one desktop application. It uses deterministic rules rather than AI, and keeps supported file operations under the user's control.

## Features

### Smart Sense

Smart Sense provides rule-based file organization suggestions to help users decide how to handle files. Suggestions are designed to be reviewed by the user rather than silently moving files.

### Custom Rule Builder

Create custom file-organization rules to tailor supported organization behavior to your needs. Rules are stored locally and can be adjusted as your workflow changes.

### File Explorer and Preview

- Browse files and folders.
- Navigate directories and access supported file operations.
- Preview supported files before taking relevant actions.
- Use available context-menu actions where supported.

### File Categorization

SFM categorizes supported files using local rules based on file types and extensions.

| Category | Examples |
| --- | --- |
| Documents | `.pdf`, `.docx`, `.txt` |
| Images | `.png`, `.jpg`, `.webp` |
| Videos | `.mp4`, `.mkv`, `.avi` |
| Audio | `.mp3`, `.wav`, `.flac` |
| Archives | `.zip`, `.7z`, `.rar` |
| Applications | `.exe`, `.msi` |
| Android APKs | `.apk` |
| Scripts | `.bat`, `.ps1`, `.sh` |
| Code | `.py`, `.cpp`, `.js`, `.html` |
| Others | Other supported or unrecognized file types |

Actual categorization depends on the application's supported extensions and configured rules.

### Scanning and Monitoring

- Scan selected folders to discover and categorize files.
- Optionally include subfolders in scans.
- Configure whether hidden files are displayed.
- Monitor supported filesystem changes while monitoring is enabled.
- Review available activity information.

### Settings and Organization

- Light and dark themes.
- Adjustable interface scaling.
- Persistent JSON-based settings.
- Favorites and recent folders.
- Review and confirmation steps for supported operations.
- Undo support for eligible operations.

Undo availability depends on the operation. Not every filesystem change can necessarily be reversed, so keep backups of important files.

## What's New in v2.2.0

- **Smart Sense:** Adds rule-based file-organization suggestions for users to review.
- **Custom Rule Builder:** Adds configurable rules for supported file-organization workflows.

For earlier changes, see the [changelog](changelog.md).

## Local-First Design

SFM is designed to keep core file-management workflows on your computer.

- File categorization uses deterministic, rule-based logic.
- Core workflows do not require a cloud backend.
- Settings and custom rules are stored locally.
- Proposed operations can be reviewed before supported changes are applied.
- SFM does not use AI for file categorization.

## Technology Stack

| Technology | Purpose |
| --- | --- |
| Python | Application logic |
| PyQt6 | Desktop interface |
| `pathlib` | Filesystem path handling |
| Watchdog | Filesystem event monitoring |
| JSON | Settings and custom-rule configuration |

## Installation

### Requirements

- Windows 10 or newer.
- Python available from your terminal.
- Dependencies listed in `requirements.txt`.

### Run from Source

Clone the repository:

```powershell
git clone https://github.com/kush85252-dotcom/smart-file-manager.git
cd smart-file-manager
```

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
python -m pip install -r requirements.txt
```

Launch the application from the repository root:

```powershell
python -m smart_file_manager
```

### Download a Release

For packaged builds and release-specific instructions, visit [GitHub Releases](https://github.com/kush85252-dotcom/smart-file-manager/releases).

## Project Status

**Current release: v2.2.0**

Smart File Manager is an actively developed desktop project. Features and workflows may change between versions. Please report reproducible bugs through [GitHub Issues](https://github.com/kush85252-dotcom/smart-file-manager/issues).

## Contributing

Bug reports, practical suggestions, and contributions are welcome.

1. Check existing issues before opening a new one.
2. Describe the problem or proposed improvement clearly.
3. Include reproducible steps and relevant error messages for bug reports.
4. Avoid including private file paths or sensitive information in reports.

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidance.

## Security and Data Safety

Always keep backups of important files. Review proposed operations and confirmation prompts before applying changes. Report suspected security vulnerabilities through the project's configured reporting process, if available.

## License

Smart File Manager is distributed under the [MIT License](LICENSE).

## Links

- [GitHub Repository](https://github.com/kush85252-dotcom/smart-file-manager)
- [Latest Releases](https://github.com/kush85252-dotcom/smart-file-manager/releases)
- [Report a Bug](https://github.com/kush85252-dotcom/smart-file-manager/issues)
- [Changelog](changelog.md)
