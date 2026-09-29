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
* Optionally scan subfolders
* Organize files using Organizing Mode
* Preview planned operations before applying them
* Confirm operations before they are performed
* Undo supported file operations
* Move deleted files to the Windows Trash
* Customize application settings
* Show or hide hidden files
* Change the interface theme and scaling

Everything happens locally on your Windows PC.

## Features

### File Organization

Smart File Manager can organize files into categories based on their file types and extensions.

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

Scan a selected folder once to detect and analyze the files currently inside it.

Subfolder scanning can optionally be enabled when a deeper scan is needed.

### Organizing Mode

Organizing Mode uses your selected organization settings to organize files into their appropriate categories.

Planned operations can be reviewed before they are applied.

Operations require confirmation before changes are performed.

### File Explorer

Browse files directly inside Smart File Manager.

The built-in explorer provides access to supported file operations without requiring a separate file manager window.

### File Preview

Preview supported files before performing operations.

### Preview and Confirmation

Review planned file operations before applying them.

Smart File Manager shows the planned changes so you can inspect what will happen before confirming an operation.

### Undo

Supported file operations can be reversed using the built-in undo functionality.

### Windows Trash Support

Deleted files can be moved to the native Windows Trash instead of being permanently removed where supported.

### Settings

Smart File Manager includes a persistent Settings page backed by JSON configuration.

Settings include options such as:

* Interface theme
* UI scaling
* Hidden file visibility
* Subfolder scanning
* Organization behavior

Settings are preserved between application launches.

### Themes and UI Scaling

Smart File Manager supports:

* Light theme
* Dark theme
* Live UI scaling changes

The interface is built with native PyQt6 components for Windows.

### Safety-Focused File Handling

Smart File Manager includes:

* Preview support
* Confirmation controls
* Undo support
* Collision-aware operations
* Operation logging
* Windows Trash support where applicable

The application is designed to keep file operations visible and under your control.

## Interface

Smart File Manager uses a native PyQt6 desktop interface designed for Windows.

The interface includes:

* File explorer
* Organization controls
* 1-Time Scan
* Organizing Mode
* File preview
* Settings
* File operations
* Activity information
* Light and Dark themes
* Adjustable UI scaling

## Screenshots

<img width="1920" height="1034" alt="Smart File Manager screenshot" src="https://github.com/user-attachments/assets/9536da34-bbfa-43b7-96e0-cb250c932c2e" />
<img width="1919" height="1034" alt="screenshot 2" src="https://github.com/user-attachments/assets/f6f5474e-98d3-4aef-ac87-badb95ddcac9" />

## Installation

### Windows Release

The easiest way to use Smart File Manager is to download a packaged Windows release.

1. Open the [Releases](../../releases) page.
2. Download the latest Windows release.
3. If the release is provided as a ZIP file, extract it.
4. Open the extracted folder.
5. Run the included Smart File Manager launcher.

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

Check your Git installation:

```bash
git --version
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
python organizer.py
```

The package launcher can also be used:

```bash
python -m smart_file_manager
```

Or, when running the application launcher directly:

```bash
python smart_file_manager/main.py
```

## Basic Workflow

A typical workflow looks like this:

```text
Select Folder
     |
Configure Settings
     |
1-Time Scan
     |
Review Results
     |
Organizing Mode
     |
Preview Planned Changes
     |
Confirm Operation
     |
Organize Files
     |
Review Results
     |
Undo if Necessary
```

You choose which folder Smart File Manager works with and when file operations are performed.

## How It Works

Smart File Manager uses deterministic, rule-based logic to categorize files.

File information such as extensions and file types is used to determine the appropriate category.

The application can first scan the selected folder using **1-Time Scan**.

If enabled, subfolder scanning allows the scan to include files inside subdirectories.

When you are ready to organize files, **Organizing Mode** uses the selected settings to create and perform organization operations.

Before changes are applied, **Preview** allows you to inspect the planned operations.

Operations are then performed only after confirmation.

## Settings and Configuration

Smart File Manager stores application settings locally using JSON configuration.

Settings persist between launches and control application behavior such as:

* Theme
* UI scaling
* Hidden file visibility
* Subfolder scanning
* Organization settings

Configuration is stored locally on the Windows PC.

## Privacy

Smart File Manager is designed as a local-first application.

The core application does not require:

* An online account
* Cloud storage
* File uploads
* Remote file processing

Your files remain on your computer while Smart File Manager performs its core operations locally.

## AI

Smart File Manager does not depend on AI.

File categorization and organization use deterministic, rule-based logic that runs locally on your computer.

No AI service is required for the core organization system.

## Safety

Smart File Manager works with real files, so care should be taken when organizing important data.

Before performing large operations:

1. Select the correct folder.
2. Configure the required settings.
3. Run a 1-Time Scan.
4. Review the results.
5. Review the organization settings.
6. Use Preview.
7. Review the planned changes.
8. Confirm the operation when ready.

Keeping independent backups of important files is recommended.

## Project Structure

```text
smart-file-manager/
|
+-- organizer.py
|
+-- smart_file_manager/
|   +-- __main__.py
|   +-- main.py
|   +-- app.py
|   +-- config.py
|   +-- categorization.py
|   +-- utils.py
|   +-- logging_config.py
|
+-- services/
|   +-- file_operations.py
|   +-- organizer.py
|
+-- ui/
|   +-- main_window.py
|   +-- styles.py
|
+-- requirements.txt
+-- CHANGELOG.md
+-- CONTRIBUTING.md
+-- SECURITY.md
+-- LICENSE
```

## Updating

### Release Version

Download the latest version from the [Releases](../../releases) page.

Follow the installation instructions included with the specific release.

### Source Version

Navigate to the project directory:

```bash
cd smart-file-manager
```

Pull the latest changes:

```bash
git pull
```

Update dependencies if required:

```bash
pip install -r requirements.txt
```

Then run Smart File Manager:

```bash
python organizer.py
```

## Troubleshooting

### Python Is Not Recognized

If Windows reports that Python is not recognized, verify that Python is installed and available from the command line.

Run:

```bash
python --version
```

### Dependencies Fail to Install

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

Then install the project dependencies again:

```bash
pip install -r requirements.txt
```

### Smart File Manager Does Not Start

Make sure you are inside the project directory:

```bash
cd smart-file-manager
```

Then run:

```bash
python organizer.py
```

If the application reports an error, check the terminal output for the relevant error message.

### Permission Problems

Some Windows folders have restricted permissions.

If Smart File Manager cannot access a folder, test it with a folder that your Windows account can normally read and modify.

Avoid testing file organization on protected Windows system folders.

## Project Status

Smart File Manager is actively being developed.

Features, UI components, and internal architecture may change between releases.

See the [CHANGELOG](CHANGELOG.md) for release history and changes.

## Bug Reports and Feature Requests

Found a bug or have a feature request?

Open an issue on GitHub:

[Report an Issue](../../issues)

When reporting a bug, include:

* Windows version
* Smart File Manager version
* Steps to reproduce the issue
* Expected behavior
* Actual behavior
* Relevant error messages or logs

Do not include private or sensitive file information.

## Contributing

Contributions are welcome.

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## Security

If you discover a security vulnerability, please report it privately rather than publicly posting sensitive details.

See [SECURITY.md](SECURITY.md) for the security policy.

## License

Smart File Manager is released under the MIT License.

See [LICENSE](LICENSE) for the full license text.

## Links

* [GitHub Repository](https://github.com/kush85252-dotcom/smart-file-manager)
* [Releases](https://github.com/kush85252-dotcom/smart-file-manager/releases)
* [Issues](https://github.com/kush85252-dotcom/smart-file-manager/issues)

---

Built with Python and PyQt6.
