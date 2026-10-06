# Smart File Manager

**A modern, local-first file organizer and manager for Windows.**

Browse, preview, organize, and manage files with clear, reviewable operations.

Built with **Python + PyQt6**.

[![Release](https://img.shields.io/github/v/release/kush85252-dotcom/smart-file-manager?display_name=tag&sort=semver)](https://github.com/kush85252-dotcom/smart-file-manager/releases)
[![Windows 10+](https://img.shields.io/badge/Windows-10%2B-0078D6?logo=windows\&logoColor=white)](https://www.microsoft.com/windows)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python\&logoColor=white)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/PyQt6-Desktop-41CD52)](https://www.qt.io/qt-for-python)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

<img src="https://github.com/user-attachments/assets/9536da34-bbfa-43b7-96e0-cb250c932c2e" alt="Smart File Manager">

## Overview

Smart File Manager is a Windows desktop application for browsing, organizing, previewing, and managing files.

It uses **local, deterministic, rule-based file detection** and keeps file operations visible so changes can be reviewed before they are applied.

### Features

* File Explorer
* 1-Time Scan
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

### 1-Time Scan

Scan a selected folder once to detect and analyze the files inside it.

### Organizing Mode

Organize detected files into their appropriate categories.

Before changes are made, planned operations can be reviewed and confirmed.

### Operation Workflow

```text
Select Folder
     ↓
1-Time Scan
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

Operations can be inspected and confirmed before changes are performed.

### Undo

Supported file operations can be reversed using the built-in undo functionality.

### Activity Information

Activity information keeps file operations visible while using the application.

## Settings & Interface

Smart File Manager includes a persistent Settings page backed by JSON configuration.

Available settings include:

* Light theme
* Dark theme
* UI scaling
* Hidden file visibility

Settings are preserved between application launches.

The interface includes:

* File Explorer
* 1-Time Scan
* Organizing Mode
* File Preview
* Settings
* File operations
* Activity information
* Adjustable UI scaling

<img width="1920" height="1034" alt="screenshot1" src="https://github.com/user-attachments/assets/0d77d5c0-95d9-4b5c-9648-3bafe8bd2ed4" />
<img width="1919" height="1034" alt="screenshot 2" src="https://github.com/user-attachments/assets/aa986ea2-5087-4d07-a1ff-0b2c04ac1858" />


## Local-First Design

Smart File Manager is designed to keep file management local and transparent.

* File categorization is deterministic and rule-based
* File operations happen locally on your Windows PC
* No cloud backend is required
* Planned operations can be reviewed before changes are made
* Supported operations can be undone

The goal is simple: **make file management easier while keeping the user in control.**

## Installation

### Requirements

* Windows 10 or newer
* Python 3.10+
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

**PowerShe**
