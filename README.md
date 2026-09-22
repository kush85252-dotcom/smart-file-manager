# Smart File Manager

A modern, local-first file organizer and manager for Windows.

Smart File Manager helps you organize files into categories, preview files, monitor folders, and safely manage file operations through a simple desktop interface.

## Features

* Modern PyQt6 desktop interface
* Built-in file explorer
* Automatic file organization
* Manual and automatic modes
* File categories for:

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
* File preview
* Folder monitoring
* Right-click context menu
* Live activity logs
* Reports
* Undo support for file operations
* Safety-focused file handling
* Dry-run / preview mode
* Dark theme
* Local-first design

## Screenshots

Screenshots will be added soon.

## Requirements

* Windows 10 or later
* Python 3.10+ when running from source
* PyQt6

## Installation

### Release

Download the latest release from the GitHub Releases page and run the application.

### From Source

Clone the repository:

```bash
git clone https://github.com/kush85252-dotcom/smart-file-manager.git
cd smart-file-manager
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run Smart File Manager:

```bash
python app.py
```

## How It Works

Smart File Manager scans the folders you choose and identifies files using rule-based categories such as file extensions and file types.

You stay in control of where files are moved.

Before performing potentially large operations, use Preview or Dry Run mode to review what will happen.

## Safety

Smart File Manager is designed with safe file handling in mind.

File operations include safeguards such as:

* Preview mode
* Dry-run support
* Undo history
* Trash-based deletion where supported
* Operation logging

Always review automatic organization settings before enabling them on important folders.

## Privacy

Smart File Manager is local-first.

The core application does not require an online account or cloud service to organize your files.

Your files remain on your computer.

## AI

The core Smart File Manager application does not depend on AI.

File organization is handled locally using deterministic, rule-based logic.

## Project Status

Smart File Manager is actively being developed.

Features, UI components, and internal architecture may change between releases.

Check the [CHANGELOG](CHANGELOG.md) for release history and changes.

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

* GitHub: https://github.com/kush85252-dotcom/smart-file-manager
* Releases: https://github.com/kush85252-dotcom/smart-file-manager/releases
* Issues: https://github.com/kush85252-dotcom/smart-file-manager/issues

---

Built with Python and PyQt6.
