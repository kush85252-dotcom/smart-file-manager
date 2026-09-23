# Smart File Manager

A modern, local-first file organizer and manager for Windows.

Smart File Manager helps you organize, browse, preview, and manage files through a clean desktop interface — while keeping file operations visible and under your control.

## Features

* Modern PyQt6 desktop interface
* Built-in file explorer
* Manual and automatic organization modes
* Automatic folder monitoring
* Preview files before opening or organizing them
* Dry-run / preview mode for planned operations
* Right-click context menu
* Undo support for file operations
* Live activity logs
* Operation reports
* Dark theme
* Safety-focused file handling
* Local-first design

### File Categories

Smart File Manager can organize files into categories including:

* Documents
* Images
* Videos
* Audio
* Archives
* Applications
* Android APKs
* Scripts
* Code
* Others

## Screenshots

Screenshots will be added soon.

## Requirements

* Windows 10 or later
* Python 3.10+ when running from source
* PyQt6

## Installation

### Release

Download the latest version from the [GitHub Releases](../../releases) page and run the application.

### From Source

Clone the repository:

```bash
git clone https://github.com/kush85252-dotcom/smart-file-manager.git
cd smart-file-manager
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Run Smart File Manager:

```bash
python app.py
```

## How It Works

Smart File Manager uses local, deterministic rules to identify files based on information such as file extensions and file types.

You choose which folders Smart File Manager can work with, and you remain in control of where files are moved.

For larger operations, use **Preview** or **Dry Run** mode to review the planned changes before anything is moved.

## Safety

File management operations can affect important data, so Smart File Manager is designed with safety in mind.

Safety features include:

* Preview mode
* Dry-run support
* Undo history
* Operation logging
* Collision-aware file handling
* Trash-based deletion where supported

Always review organization settings before enabling automatic organization on important folders.

## Privacy & Local-First Design

Smart File Manager is designed to work locally.

The core application does not require:

* An online account
* A cloud service
* Uploaded files
* Remote processing

Your files stay on your computer while Smart File Manager performs its core organization and management tasks locally.

## AI

Smart File Manager does **not** require AI.

File categorization and organization use deterministic, rule-based logic that runs locally on your computer.

## Project Status

Smart File Manager is actively being developed.

Features, UI components, and internal architecture may change between releases.

See the [CHANGELOG](CHANGELOG.md) for release history and changes.

## Contributing

Contributions, bug reports, feature requests, and suggestions are welcome.

See [CONTRIBUTING](CONTRIBUTING.md) for contribution guidelines.

## Security

If you discover a security vulnerability, please report it privately.

See [SECURITY](SECURITY.md) for the security policy.

## License

Smart File Manager is released under the MIT License.

See [LICENSE](LICENSE) for the full license text.

## Links

* [GitHub Repository](https://github.com/kush85252-dotcom/smart-file-manager)
* [Releases](https://github.com/kush85252-dotcom/smart-file-manager/releases)
* [Issues](https://github.com/kush85252-dotcom/smart-file-manager/issues)

---

Built with Python and PyQt6.
