# Smart File Manager

**A modern, local-first file organizer and manager for Windows.**

Browse, preview, organize, monitor, scan, and manage files with clear, reviewable operations.

Built with **Python + PyQt6**.

[![Release](https://img.shields.io/github/v/release/kush85252-dotcom/smart-file-manager?display_name=tag\&sort=semver)](https://github.com/kush85252-dotcom/smart-file-manager/releases)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python\&logoColor=white)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/PyQt6-Desktop-41CD52)](https://pypi.org/project/PyQt6/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

<img src="https://github.com/user-attachments/assets/9536da34-bbfa-43b7-96e0-cb250c932c2e" alt="Smart File Manager">

## Overview

Smart File Manager is a Windows desktop application for browsing, organizing, monitoring, previewing, and managing files.

It uses **local, deterministic, rule-based file detection** and keeps file operations visible so changes can be reviewed before they are applied.

Version 2.1 builds on the existing file-management experience with live monitoring, folder-based lists, and additional scanning tools.

## Features

* File Explorer
* One-time folder scanning
* Live file monitoring
* Folder-based lists
* Additional scanning tools
* Organizing Mode
* File Preview
* Operation Preview
* Confirmation controls
* Undo for supported operations
* Collision-aware file operations
* Activity information
* Persistent Settings
* Light and Dark themes
* Adjustable UI scaling
* Hidden-file visibility
* Optional subfolder scanning

## What's New in 2.1

### Live File Monitoring

Monitor filesystem changes using the application's live-monitoring functionality, rather than relying exclusively on one-time scans.

### Folder-Based Lists

Work with folder-based lists to navigate and manage files in relevant locations.

### Additional Scanning Tools

Use the expanded scanning functionality to improve file discovery and scanning workflows.

These additions build on the existing file explorer, organization tools, settings, and operation-review workflow.

## File Organization

Smart File Manager organizes files according to their file types and extensions.

| Category     | Examples                      |
| ------------ | ----------------------------- |
| Documents    | `.pdf`, `.docx`, `.txt`       |
| Images       | `.png`, `.jpg`, `.webp`       |
| Videos       | `.mp4`, `.mkv`, `.avi`        |
| Audio        | `.mp3`, `.wav`, `.flac`       |
| Archives     | `.zip`, `.7z`, `.rar`         |
| Applications | `.exe`, `.msi`                |
| Android APKs | `.apk`                        |
| Scripts      | `.bat`, `.ps1`, `.sh`         |
| Code         | `.py`, `.cpp`, `.js`, `.html` |
| Others       | Unrecognized file types       |

File detection is deterministic and rule-based, keeping categorization predictable and local.

## Scanning & Organization

### One-Time Scan

Scan a selected folder to detect and analyze files within the selected location.

### Live Monitoring

Use live monitoring to observe filesystem changes while working with monitored locations. Monitoring behavior depends on the configured paths and application implementation.

### Folder-Based Lists

Use folder-based lists to work with files associated with particular folders.

### Organizing Mode

Organize detected files into their appropriate categories.

Before changes are made, planned operations can be reviewed and confirmed.

### Operation Workflow

```text
Select Folder
     ↓
Scan or Monitor
     ↓
Detect & Categorize
     ↓
Review Operations
     ↓
Confirm
     ↓
Organize
```

Smart File Manager also uses collision-aware operations to account for existing file names.

## File Management

### File Explorer

Browse files directly inside Smart File Manager and access supported file operations from the application.

### File Preview

Preview supported files before performing operations.

### Operation Preview

Review planned file operations before applying them.

### Confirmation

Inspect and confirm supported operations before changes are performed.

### Undo

Reverse supported file operations using the built-in undo functionality where available.

### Activity Information

View activity information about file operations while using the application.

## Settings & Interface

Smart File Manager includes a persistent Settings page backed by JSON configuration.

Available settings include:

* Light theme
* Dark theme
* UI scaling
* Hidden-file visibility
* Optional subfolder scanning

Settings are preserved between application launches.

The interface includes file browsing, scanning, organization, preview, settings, and activity features.

<img width="1920" height="1034" alt="Smart File Manager screenshot 1" src="https://github.com/user-attachments/assets/0d77d5c0-95d9-4b5c-9648-3bafe8bd2ed4" />

<img width="1919" height="1034" alt="Smart File Manager screenshot 2" src="https://github.com/user-attachments/assets/aa986ea2-5087-4d07-a1ff-0b2c04ac1858" />

## Local-First Design

Smart File Manager is designed to keep file management local and transparent.

* File categorization is deterministic and rule-based.
* File operations happen locally on your Windows PC.
* No cloud backend is required for core file-management workflows.
* Planned operations can be reviewed before changes are made.
* Supported operations can be undone.

The goal is simple: **make file management easier while keeping the user in control.**

## Installation

### Requirements

* Windows 10 or newer
* Python 3.10 or newer, subject to the dependencies of the selected release
* Git

Check your Python version:

```bash
python --version
```

### Clone the Repository

```bash
git clone https://github.com/kush85252-dotcom/smart-file-manager.git
cd smart-file-manager
```

### Create a Virtual Environment

```bash
python -m venv .venv
```

### Activate the Environment

**Command Prompt:**

```bat
.venv\Scripts\activate
```

**PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

### Install Dependencies

Install the dependencies required by the selected version. If the project provides a `requirements.txt` file, use:

```bash
python -m pip install -r requirements.txt
```

Otherwise, install the dependencies documented for that release.

### Run the Application

Use the entry point provided by the checked-out version. For versions that include the following module:

```bash
python -m smart_file_manager.main
```

The application entry point may differ between releases.

## Download

Want to use the application without setting up a Python environment?

Visit the [GitHub Releases page](https://github.com/kush85252-dotcom/smart-file-manager/releases) to find available Windows executables and release notes.

## Project Structure

The project is organized around the main application package.

```text
smart-file-manager/
├── smart_file_manager/
│   ├── ...
├── README.md
├── CHANGELOG.md
├── LICENSE
└── SECURITY.md
```

The exact project structure may vary between releases.

## Technology Stack

| Technology | Purpose                     |
| ---------- | --------------------------- |
| Python     | Application logic           |
| PyQt6      | Desktop graphical interface |
| Watchdog   | Filesystem monitoring       |
| JSON       | Persistent configuration    |
| Git        | Version control             |
| Windows    | Primary desktop platform    |

## Contributing

Contributions, bug reports, and suggestions are welcome.

To contribute:

1. Fork the repository.
2. Create a branch for your changes.
3. Implement and test your changes.
4. Open a pull request describing your contribution.

Please keep changes focused and preserve Smart File Manager's local-first approach.

## Security

If you discover a security vulnerability, please review [SECURITY.md](SECURITY.md) for reporting guidance.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and documented changes.

## License

Smart File Manager is released under the [MIT License](LICENSE).

## Author

Created and maintained by [Kush](https://github.com/kush85252-dotcom).

## Support the Project

If you find Smart File Manager useful, consider starring the repository on GitHub. Your support helps others discover the project.

[Vist my GitHub profile](https://github.com/kush85252-dotcom)

---

**Smart File Manager**

Local-first file management for Windows.
