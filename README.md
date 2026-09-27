# Smart File Manager

A modern, local-first file organizer and manager for Windows.

Smart File Manager provides a simple way to browse, organize, preview, and manage files while keeping file operations visible and under your control.

Built with Python and PyQt6.

## What is Smart File Manager?

Managing a Downloads folder containing different types of files can get messy quickly.

Smart File Manager helps organize files into categories using local, deterministic, rule-based file detection.

You can:

* Browse files
* Preview supported files
* Scan a folder once
* Organize files using Organizing Mode
* Preview planned operations before applying them
* Undo supported file operations
* View activity logs and operation reports

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

The scan finishes after processing the selected folder and does not continuously monitor it.

### Organizing Mode

Organizing Mode uses your selected organization settings to organize files into their appropriate categories.

Planned operations can be reviewed before they are applied.

### File Explorer

Browse files directly inside Smart File Manager.

The built-in explorer provides access to supported file operations without requiring a separate file manager window.

### File Preview

Preview supported files before performing operations.

### Preview and Dry Run

Review planned file operations before applying them.

This is especially useful when organizing folders containing large numbers of files.

### Undo

Supported file operations can be reversed using the built-in undo functionality.

### Activity Logs and Reports

Track file operations through:

* Live activity logs
* Operation history
* Reports
* Organization results

### Safety-Focused File Handling

Smart File Manager includes:

* Preview mode
* Dry Run support
* Undo support
* Collision-aware operations
* Operation logging
* Trash-based deletion where supported

## Interface

Smart File Manager uses a native PyQt6 desktop interface designed for Windows.

The interface includes:

* File explorer
* Organization controls
* 1-Time Scan
* Organizing Mode
* File preview
* File operations
* Activity information
* Dark theme

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
5. Run the Smart File Manager executable.

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

The module entry point can also be used:

```bash
python -m smart_file_manager
```

## Basic Workflow

A typical workflow looks like this:

```text
Select Folder
     |
Choose Mode
     |
1-Time Scan
     |
Review Results
     |
Organizing Mode
     |
Preview Planned Changes
     |
Organize Files
     |
Check Activity / Report
     |
Undo if Necessary
```

You choose which folder Smart File Manager works with and when file operations are performed.

## How It Works

Smart File Manager uses deterministic, rule-based logic to categorize files.

File information such as extensions and file types is used to determine the appropriate category.

The application can first scan the selected folder using **1-Time Scan**.

When you are ready to organize files, **Organizing Mode** uses the selected settings to create and perform the organization operations.

Before larger operations, **Preview** or **Dry Run** mode can be used to inspect the planned changes.

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
2. Run a 1-Time Scan.
3. Review the results.
4. Review the organization settings.
5. Use Preview or Dry Run.
6. Review the planned changes.
7. Start the operation when ready.

Keeping independent backups of important files is recommended.

## Project Structure

```text
smart-file-manager/
|
+-- organizer.py
|
+-- smart_file_manager/
|   +-- __main__.py
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

```

Main changes: **less repetition, cleaner wording, consistent terminology, better section flow, and no fake “enterprise” fluff.** The substance of your README is still yours.
```
