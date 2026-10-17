# Smart File Manager

**A modern, local-first file organizer and manager for Windows.**

Browse, preview, scan, organize, monitor, and manage files with transparent workflows and reviewable operations.

Built with **Python and PyQt6**.

[![Release](https://img.shields.io/github/v/release/kush85252-dotcom/smart-file-manager?display_name=tag&sort=semver)](https://github.com/kush85252-dotcom/smart-file-manager/releases)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/PyQt6-Desktop-41CD52)](https://pypi.org/project/PyQt6/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

<img src="https://github.com/user-attachments/assets/9536da34-bbfa-43b7-96e0-cb250c932c2e" alt="Smart File Manager application preview">

## Overview

Smart File Manager is a Windows desktop application designed to simplify file browsing, organization, monitoring, and management.

It uses **deterministic, rule-based file categorization** to keep file detection predictable and local. Its review-oriented workflow helps users inspect planned operations before applying changes, with confirmation and undo support for eligible operations.

Version 2.1 expands the existing file-management experience with live filesystem monitoring, folder-based lists, and additional scanning capabilities.

## Features

- **File Explorer:** Browse files and access supported file-management operations.
- **Folder Scanning:** Scan selected directories to identify and categorize files.
- **Live Monitoring:** Monitor filesystem changes in supported locations.
- **Folder-Based Lists:** Work with files associated with relevant folders.
- **Organizing Mode:** Organize files according to their detected categories.
- **File Preview:** Preview supported files before taking action.
- **Operation Preview:** Review planned changes before applying them.
- **Confirmation Controls:** Retain control over supported file operations.
- **Undo Support:** Reverse eligible operations where supported.
- **Collision-Aware Operations:** Account for existing filenames during file operations.
- **Activity Information:** Review information about application activity.
- **Persistent Settings:** Preserve configuration between launches.
- **Theme Options:** Switch between light and dark themes.
- **Adjustable Interface:** Customize UI scaling.
- **Hidden-File Visibility:** Choose whether hidden files are displayed.
- **Optional Subfolder Scanning:** Configure scanning to include subdirectories.

## What's New in Version 2.1

### Live Filesystem Monitoring

Monitor changes in supported locations without relying exclusively on one-time scans.

### Folder-Based Lists

Work with files grouped or presented according to their associated folders.

### Additional Scanning Tools

Use expanded scanning capabilities to support file discovery and scanning workflows.

These additions build on the existing file explorer, organization tools, configuration options, and operation-review workflow.

## File Categorization

Smart File Manager categorizes files using deterministic rules based on file types and extensions.

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
| Others | Unrecognized file types |

Categorization is handled through local rules rather than AI-based classification, keeping the process predictable and straightforward.

## Scanning and Organization

### One-Time Scanning

Select a folder to scan its contents and identify files that can be categorized by the application.

### Live Monitoring

Monitor supported filesystem locations for changes while working. Monitoring behavior depends on the configured paths and the capabilities of the selected release.

### Folder-Based Lists

Navigate and manage files in the context of their associated folders.

### Organizing Mode

Organize detected files into their corresponding categories. Review planned operations and confirm applicable changes before they are performed.

### Operation Workflow

```text
Select Folder
     |
     v
Scan or Monitor
     |
     v
Detect and Categorize
     |
     v
Review Planned Operations
     |
     v
Confirm Changes
     |
     v
Organize Files
```

Collision-aware handling helps account for existing filenames during supported file operations.

## File Management

### File Explorer

Browse files within Smart File Manager and access supported operations from the application interface.

### File Preview

Inspect supported files before performing relevant operations.

### Operation Preview

Review planned file changes before committing to them.

### Confirmation Controls

Confirm supported operations before changes are applied.

### Undo Support

Reverse supported file operations through the built-in undo functionality where available.

### Activity Information

Access information about file operations and application activity.

## Settings and Interface

Smart File Manager includes a persistent settings system backed by JSON configuration.

Available settings include:

- Light and dark themes
- Adjustable UI scaling
- Hidden-file visibility
- Optional subfolder scanning

Settings are preserved between application launches.

The interface brings file browsing, scanning, organization, previews, settings, and activity information together in a single desktop application.

<img width="1920" height="1034" alt="Smart File Manager screenshot 1" src="https://github.com/user-attachments/assets/0d77d5c0-95d9-4b5c-9648-3bafe8bd2ed4">

<img width="1919" height="1034" alt="Smart File Manager screenshot 2" src="https://github.com/user-attachments/assets/aa986ea2-5087-4d07-a1ff-0b2c04ac1858">

## Local-First Design

Smart File Manager is designed to keep file management local, transparent, and user-controlled.

- **Local processing:** File categorization uses deterministic, rule-based logic.
- **Local operations:** Core file-management operations are performed on the Windows PC.
- **No cloud dependency:** Core file-management workflows do not require a cloud backend.
- **Review before changes:** Planned operations can be inspected before being applied.
- **Undo where supported:** Eligible operations can be reversed through the application's undo functionality.

The guiding principle is simple: **make file management easier without taking control away from the user.**

## Installation

### Requirements

- Windows 10 or newer
- Python
