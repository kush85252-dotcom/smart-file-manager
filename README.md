# Smart File Manager

[![Latest Release](https://img.shields.io/github/v/release/kush85252-dotcom/smart-file-manager?display_name=tag&label=latest%20release)](https://github.com/kush85252-dotcom/smart-file-manager/releases)
[![License](https://img.shields.io/github/license/kush85252-dotcom/smart-file-manager)](https://github.com/kush85252-dotcom/smart-file-manager/blob/main/LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/kush85252-dotcom/smart-file-manager?style=flat)](https://github.com/kush85252-dotcom/smart-file-manager/stargazers)
[![GitHub Issues](https://img.shields.io/github/issues/kush85252-dotcom/smart-file-manager)](https://github.com/kush85252-dotcom/smart-file-manager/issues)
[![Last Commit](https://img.shields.io/github/last-commit/kush85252-dotcom/smart-file-manager)](https://github.com/kush85252-dotcom/smart-file-manager/commits/main)
[![Platform](https://img.shields.io/badge/platform-Windows-0078D4)](https://github.com/kush85252-dotcom/smart-file-manager)
[![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)](https://www.python.org/)

A local-first file manager and organizer for Windows, built with Python and PyQt6.

Smart File Manager (SFM) brings file browsing, scanning, categorization, filesystem monitoring, and organization tools together in one desktop application. It uses deterministic, rule-based logic rather than AI and keeps supported file operations under the user's control.

## Features

### Smart Sense

Smart Sense provides rule-based file-organization suggestions to help users decide how to handle files. Suggestions are designed to be reviewed before the corresponding supported operations are applied.

### Custom Rule Builder

Create custom rules to tailor supported file-organization workflows to your needs. Rules are stored locally and can be adjusted as your workflow changes.

The example below is illustrative. Adapt it to the exact schema supported by your installed version of SFM.

```json
{
  "rule_name": "Move PDF Invoices",
  "trigger_extension": ".pdf",
  "contain_keyword": "invoice",
  "destination_folder": "C:/Users/User/Documents/Invoices"
}
```

### File Explorer and Preview

- Browse files and folders.
- Navigate directories and access supported file operations.
- Preview supported files before taking relevant actions.
- Use available context-menu actions where supported.

### File Categorization

SFM categorizes supported files using local rules based on file types and extensions.

| Category | Example extensions |
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

Actual categorization depends on the extensions and rules supported by the application.

### Scanning and Monitoring

- Scan selected folders to discover and categorize files.
- Optionally include subfolders in scans.
- Configure whether hidden files are displayed.
- Monitor filesystem changes while monitoring is enabled.
- Review available activity information.
- Use the available fast-scan and full-scan modes.

### Settings and Organization

- Light and dark themes.
- Adjustable interface scaling.
- Persistent JSON-based settings.
- Favorites and recent folders.
- Review and confirmation steps for supported operations.
- Undo support for eligible operations.

**Important:** Undo depends on the operation. Not every filesystem change can be reversed. Keep backups of important files.

## What's New in v2.2.0

- **Smart Sense:** Adds rule-based file-organization suggestions for users to review.
- **Custom Rule Builder:** Adds configurable rules for supported file-organization workflows.

For earlier changes, see the [changelog](changelog.md).

## Local-First Design

SFM is designed to keep its core file-management workflows on your computer.

- File categorization uses deterministic, rule-based logic.
- Core workflows do not require a cloud backend.
- Settings and custom rules are stored locally.
- Proposed operations can be reviewed before supported changes are applied.
- File categorization does not use AI.

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
- Python installed and available from your terminal.
- Dependencies listed in `requirements.txt`.

### Run from Source

Clone the repository:

```powershell
git clone https://github.com/kush85252-dotcom/smart-file-manager.git
cd smart-file-manager
```

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it in PowerShell:

```powershell
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

If PowerShell blocks virtual-environment activation, you can use the environment's Python executable directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m smart_file_manager
```

### Download a Release

For packaged builds and release-specific instructions, visit [GitHub Releases](https://github.com/kush85252-dotcom/smart-file-manager/releases).

## Project Status

**Current documented version: v2.2.0**

Smart File Manager is an actively developed desktop project. Features and workflows may change between versions.

- [View Releases](https://github.com/kush85252-dotcom/smart-file-manager/releases)
- [Report a Bug](https://github.com/kush85252-dotcom/smart-file-manager/issues)
- [View Open Issues](https://github.com/kush85252-dotcom/smart-file-manager/issues)

When reporting a problem, include reproducible steps and relevant error messages. Avoid sharing private file paths or other sensitive information.

## Contributing

Bug reports, practical suggestions, and contributions are welcome.

1. Check existing issues before opening a new one.
2. Describe the problem or proposed improvement clearly.
3. Include reproducible steps and relevant error messages for bug reports.
4. Avoid including private file paths or sensitive information in reports.

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidance.

## Security and Data Safety

File-management operations can affect important data. Before applying changes:

- Review proposed operations and confirmation prompts.
- Keep backups of important files.
- Check the destination and affected files before confirming an operation.
- Remember that undo may not be available for every operation.

For security concerns, use the project's configured reporting process if one is available.

## License

Smart File Manager is distributed under the [MIT License](LICENSE).

## Links

- [GitHub Repository](# Smart File Manager

[![Latest Release](https://img.shields.io/github/v/release/kush85252-dotcom/smart-file-manager?display_name=tag&label=latest%20release)](https://github.com/kush85252-dotcom/smart-file-manager/releases)
[![License](https://img.shields.io/github/license/kush85252-dotcom/smart-file-manager)](https://github.com/kush85252-dotcom/smart-file-manager/blob/main/LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/kush85252-dotcom/smart-file-manager?style=flat)](https://github.com/kush85252-dotcom/smart-file-manager/stargazers)
[![GitHub Issues](https://img.shields.io/github/issues/kush85252-dotcom/smart-file-manager)](https://github.com/kush85252-dotcom/smart-file-manager/issues)
[![Last Commit](https://img.shields.io/github/last-commit/kush85252-dotcom/smart-file-manager)](https://github.com/kush85252-dotcom/smart-file-manager/commits/main)
[![Platform](https://img.shields.io/badge/platform-Windows-0078D4)](https://github.com/kush85252-dotcom/smart-file-manager)
[![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)](https://www.python.org/)

A local-first file manager and organizer for Windows, built with Python and PyQt6.

Smart File Manager (SFM) brings file browsing, scanning, categorization, filesystem monitoring, and organization tools together in one desktop application. It uses deterministic, rule-based logic rather than AI and keeps supported file operations under the user's control.

## Features

### Smart Sense

Smart Sense provides rule-based file-organization suggestions to help users decide how to handle files. Suggestions are designed to be reviewed before the corresponding supported operations are applied.

### Custom Rule Builder

Create custom rules to tailor supported file-organization workflows to your needs. Rules are stored locally and can be adjusted as your workflow changes.

The example below is illustrative. Adapt it to the exact schema supported by your installed version of SFM.

```json
{
  "rule_name": "Move PDF Invoices",
  "trigger_extension": ".pdf",
  "contain_keyword": "invoice",
  "destination_folder": "C:/Users/User/Documents/Invoices"
}
```

### File Explorer and Preview

- Browse files and folders.
- Navigate directories and access supported file operations.
- Preview supported files before taking relevant actions.
- Use available context-menu actions where supported.

### File Categorization

SFM categorizes supported files using local rules based on file types and extensions.

| Category | Example extensions |
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

Actual categorization depends on the extensions and rules supported by the application.

### Scanning and Monitoring

- Scan selected folders to discover and categorize files.
- Optionally include subfolders in scans.
- Configure whether hidden files are displayed.
- Monitor filesystem changes while monitoring is enabled.
- Review available activity information.
- Use the available fast-scan and full-scan modes.

### Settings and Organization

- Light and dark themes.
- Adjustable interface scaling.
- Persistent JSON-based settings.
- Favorites and recent folders.
- Review and confirmation steps for supported operations.
- Undo support for eligible operations.

**Important:** Undo depends on the operation. Not every filesystem change can be reversed. Keep backups of important files.

## What's New in v2.2.0

- **Smart Sense:** Adds rule-based file-organization suggestions for users to review.
- **Custom Rule Builder:** Adds configurable rules for supported file-organization workflows.

For earlier changes, see the [changelog](changelog.md).

## Local-First Design

SFM is designed to keep its core file-management workflows on your computer.

- File categorization uses deterministic, rule-based logic.
- Core workflows do not require a cloud backend.
- Settings and custom rules are stored locally.
- Proposed operations can be reviewed before supported changes are applied.
- File categorization does not use AI.

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
- Python installed and available from your terminal.
- Dependencies listed in `requirements.txt`.

### Run from Source

Clone the repository:

```powershell
git clone https://github.com/kush85252-dotcom/smart-file-manager.git
cd smart-file-manager
```

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it in PowerShell:

```powershell
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

If PowerShell blocks virtual-environment activation, you can use the environment's Python executable directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m smart_file_manager
```

### Download a Release

For packaged builds and release-specific instructions, visit [GitHub Releases](https://github.com/kush85252-dotcom/smart-file-manager/releases).

## Project Status

**Current documented version: v2.2.0**

Smart File Manager is an actively developed desktop project. Features and workflows may change between versions.

- [View Releases](https://github.com/kush85252-dotcom/smart-file-manager/releases)
- [Report a Bug](https://github.com/kush85252-dotcom/smart-file-manager/issues)
- [View Open Issues](https://github.com/kush85252-dotcom/smart-file-manager/issues)

When reporting a problem, include reproducible steps and relevant error messages. Avoid sharing private file paths or other sensitive information.

## Contributing

Bug reports, practical suggestions, and contributions are welcome.

1. Check existing issues before opening a new one.
2. Describe the problem or proposed improvement clearly.
3. Include reproducible steps and relevant error messages for bug reports.
4. Avoid including private file paths or sensitive information in reports.

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidance.

## Security and Data Safety

File-management operations can affect important data. Before applying changes:

- Review proposed operations and confirmation prompts.
- Keep backups of important files.
- Check the destination and affected files before confirming an operation.
- Remember that undo may not be available for every operation.

For security concerns, use the project's configured reporting process if one is available.

## License

Smart File Manager is distributed under the [MIT License](LICENSE).

## Links

- [GitHub Repository](https://github.com/kush85252-dotcom/smart-file-manager)
- [Latest Releases](https://github.com/kush85252-dotcom/smart-file-manager/releases)
- [Report a Bug](https://github.com/kush85252-dotcom/smart-file-manager/issues/new)
- [Open Issues](https://github.com/kush85252-dotcom/smart-file-manager/issues)
- [Changelog](changelog.md)
- [License](LICENSE)

- [Latest Releases](https://github.com/kush85252-dotcom/smart-file-manager/releases)
- [Report a Bug](https://github.com/kush85252-dotcom/smart-file-manager/issues/new)
- [Open Issues](https://github.com/kush85252-dotcom/smart-file-manager/issues)
- [Changelog](changelog.md)
- [License](LICENSE)
