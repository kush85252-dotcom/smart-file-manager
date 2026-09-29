# Smart File Manager

A modern, local-first file organizer and manager for Windows.

Smart File Manager provides a simple way to browse, organize, preview, and manage files while keeping file operations visible and under your control.

Built with Python and PyQt6.

## What is Smart File Manager?

Managing a folder containing different types of files can get messy quickly.

Smart File Manager helps organize files into categories using local, deterministic, rule-based file detection.

You can:

* Browse files
* Preview supported files
* Scan a folder once
* Organize files using Organizing Mode
* Preview planned operations before applying them
* Confirm operations before changes are performed
* Undo supported file operations
* Customize application settings
* Show or hide hidden files
* Change the interface theme and scaling

Everything happens locally on your Windows PC.

## Features

### File Organization

Smart File Manager organizes files into categories based on their file types and extensions.

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

### 1-Time Scan

Scan a selected folder once to detect and analyze the files inside it.

### Organizing Mode

Organizing Mode organizes detected files into their appropriate categories.

Before changes are made, you can preview the planned operations and confirm them.

### File Explorer

Browse files directly inside Smart File Manager and access supported file operations from the application.

### File Preview

Preview supported files before performing operations.

### Preview and Confirmation

Review planned file operations before applying them.

Smart File Manager shows the planned changes so you can inspect what will happen before confirming an operation.

### Undo

Supported file operations can be reversed using the built-in undo functionality.

### Settings

Smart File Manager includes a persistent Settings page backed by JSON configuration.

Settings include:

* Interface theme
* UI scaling
* Hidden file visibility

Settings are preserved between application launches.

### Themes and UI Scaling

Smart File Manager supports:

* Light theme
* Dark theme
* Live UI scaling changes

## Safety-Focused File Handling

Smart File Manager is designed to keep file operations visible and under your control.

Safety features include:

* Operation preview
* Confirmation controls
* Undo support
* Collision-aware operations
* Operation logging

Always review important operations before confirming them.

## Interface

Smart File Manager uses a native PyQt6 desktop interface designed for Windows.

The interface includes:

* File Explorer
* 1-Time Scan
* Organizing Mode
* File Preview
* Settings
* File operations
* Activity information
* Light and Dark themes
* Adjustable UI scaling

## Screenshots

<img width="1920" height="1034" alt="Smart File Manager screenshot" src="https://github.com/user-attachments/assets/9536da34-bbfa-43b7-96e0-cb250c932c2e" />

<img width="1919" height="1034" alt="Smart File Manager screenshot 2" src="https://github.com/user-attachments/assets/f6f5474e-98d3-4aef-ac87-badb95ddcac9" />

## Installation

### Windows Release

The easiest way to use Smart File Manager is to download a packaged Windows release.

1. Open the Releases page.
2. Download the latest Windows release.
3. Extract the release if necessary.
4. Run the included Smart File Manager launcher.

Python is not required when using a packaged Windows release.

### Run From Source

Running from source is useful for development, testing, or using the latest repository code.

#### Requirements

* Windows 10 or newer
* Python 3.10+
* Git

Check your Python installation:

```bash
python --version
```

#### 1. Clone the Repository

```bash
git clone https://github.com/kush85252-dotcom/smart-file-manager.git
cd smart-file-manager
```

#### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

#### 3. Activate the Virtual Environment

**Command Prompt:**

```bat
.venv\Scripts\activate
```

**PowerShell:**

```powershell
.venv\Scripts\Activate.ps1
```

#### 4. Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

#### 5. Run Smart File Manager

```bash
python o
```
