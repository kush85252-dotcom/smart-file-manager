# Smart File Manager

[![Latest Release](https://img.shields.io/github/v/release/kush85252-dotcom/smart-file-manager?label=latest%20release)](https://github.com/kush85252-dotcom/smart-file-manager/releases)
[![License](https://img.shields.io/github/license/kush85252-dotcom/smart-file-manager)](https://github.com/kush85252-dotcom/smart-file-manager/blob/main/LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/kush85252-dotcom/smart-file-manager?style=flat)](https://github.com/kush85252-dotcom/smart-file-manager/stargazers)
[![GitHub Issues](https://img.shields.io/github/issues/kush85252-dotcom/smart-file-manager)](https://github.com/kush85252-dotcom/smart-file-manager/issues)
[![Last Commit](https://img.shields.io/github/last-commit/kush85252-dotcom/smart-file-manager)](https://github.com/kush85252-dotcom/smart-file-manager/commits/main)
[![Platform](https://img.shields.io/badge/platform-Windows-0078D4?logo=windows)](https://github.com/kush85252-dotcom/smart-file-manager)
[![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)](https://www.python.org/)

A modern, local-first file organizer and manager for Windows, built with Python and PyQt6.

Smart File Manager helps you browse, scan, monitor, categorize, and manage files through configurable rules and user-controlled workflows.

## Overview

Smart File Manager (SFM) is a Windows desktop application designed to make everyday file management easier, safer, and more organized.

Version 2.2 introduces **Smart Sense** and the **Custom Rule Builder**, extending SFM's existing file-management capabilities while maintaining a focus on transparency, local processing, and user control.

## Features

### Smart Sense

Smart Sense extends SFM's file-awareness capabilities to support its file-management workflow.

### Custom Rule Builder

Configure custom rules to tailor supported file-handling behavior to your needs.

### File Explorer

- Browse files and folders.
- Navigate directories.
- Access supported file operations through the interface.
- Work with files using the application's available controls.

### File Categorization

Organize supported file types into categories using local, rule-based detection.

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

Actual categorization depends on the application's configured rules and supported extensions.

### Scanning Tools

- **Fast Scan:** Use the available fast-scanning workflow to inspect selected folders.
- **Full Scan:** Perform a more comprehensive folder scan.
- **Subfolder Scanning:** Optionally include subdirectories.
- **Hidden Files:** Configure visibility of hidden files where supported.

### Live Monitoring

Monitor selected folders and their subfolders for supported filesystem changes while monitoring is active.

- Start and stop monitoring.
- Review detected file activity.
- Observe supported creation, modification, deletion, and movement events.
- View recent events through the monitoring interface.

Monitoring is optional and depends on the filesystem-monitoring component being available.

### Favorites and Recent Folders

- Save frequently accessed folders as favorites.
- Revisit recently opened folders.
- Access saved locations from the relevant interface.
- Configure the recent-folder list where supported.

### Settings and Interface

- Light and dark themes.
- Adjustable interface scaling.
- Persistent JSON-based settings.
- Configurable application preferences.

### File Operation Safety

SFM emphasizes clear, user-controlled workflows.

- Review supported operations before execution.
- Confirm changes where required.
- Use available undo controls for eligible operations.
- Receive error information for supported operations.
- Keep important files backed up.

Undo availability depends on the operation. Not every filesystem change can necessarily be reversed.

## What's New in v2.2

### Smart Sense

Introduces additional file-awareness capabilities to build on SFM's existing file-management workflows.

### Custom Rule Builder

Adds configurable rules to give users more control over supported file-handling behavior.

These additions extend the existing scanning, categorization, monitoring, and file-management experience.

For earlier changes, see the [Changelog](changelog.md).

## How It Works

SFM uses local file access and rule-based processing to support its core workflows.

A typical workflow:

1. Open Smart File Manager.
2. Select a folder to browse or scan.
3. Review the available file information and categorization.
4. Configure supported rules and settings.
5. Review any proposed operation and confirmation prompts.
6. Apply the operation and inspect the result.

The exact steps depend on the selected feature.

## Local-First Design

Smart File Manager is designed around local processing and user control.

- Core file-management operations run on your computer.
- Core workflows do not require a cloud backend.
- File categorization uses application rules.
- Supported changes can include review and confirmation steps.
- Settings are stored locally using JSON-based configuration.

SFM aims to keep everyday file management predictable and transparent.

## Technology Stack

| Technology | Purpose |
| --- | --- |
| Python | Application logic |
| PyQt6 | Desktop interface |
| `pathlib` | Filesystem path handling |
| Watchdog | Filesystem event monitoring |
| JSON | Application settings and configuration |

## Installation

### Requirements

- Windows 10 or newer.
- Python installed and available from your terminal.
- Dependencies listed in `requirements.txt`.

### Run from Source

Clone the repository:

```bash
git clone https://github.com/kush85252-dotcom/smart-file-manager.git
cd smart-file-manager
```

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Launch the application using the entry point provided by your checked-out version.

For example, if your entry point is `main.py` in the repository root:

```bash
python main.py
```

If your entry point is different, use the appropriate command for your project structure.

### Prebuilt Releases

Check the [GitHub Releases](https://github.com/kush85252-dotcom/smart-file-manager/releases) page for available packaged versions and their installation instructions.

## Project Structure

The application is organized around its source files, configuration, and supporting resources.

The exact structure may change between releases. Consult the repository for the current source layout and entry point.

## Project Status

**Current development version: 2.2**

Smart File Manager continues to focus on improving reliability, usability, file-awareness, and configurable workflows.

Future features and improvements are subject to development and testing.

## Contributing

Contributions, bug reports, and practical suggestions are welcome.

Before submitting changes:

1. Check existing issues to avoid duplicates.
2. Describe the problem or proposed improvement clearly.
3. Include reproducible steps for bugs.
4. Avoid including private file paths or sensitive information in reports.

See [CONTRIBUTING.md](CONTRIBUTING.md) if available in the repository.

## Security and Data Safety

Always keep backups of important files.

Review proposed operations and confirmation prompts before applying changes. Report suspected security vulnerabilities through the project's designated security-reporting process, if one is configured.

## License

Smart File Manager is distributed under the [MIT License](LICENSE).

## Links

- [GitHub Repository](https://github.com/kush85252-dotcom/smart-file-manager)
- [Latest Releases](https://github.com/kush85252-dotcom/smart-file-manager/releases)
- [Report a Bug](https://github.com/kush85252-dotcom/smart-file-manager/issues)
- [Changelog](changelog.md)
