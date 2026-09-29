## v2.0.0

### Added

* Added a persistent Settings page backed by JSON configuration.
* Added live theme and UI scaling changes.
* Added Light and Dark themes.
* Added an option to show or hide hidden files.
* Added optional subfolder scanning.
* Added native Trash support for deleted files.
* Added operation preview and confirmation controls.
* Added undo controls for supported file operations.
* Added `smart_file_manager/main.py` as a convenient application launcher.

### Changed

* Improved settings handling so preferences persist between launches.
* Improved file scanning controls.
* Improved operation safety with clearer preview and confirmation steps.
* Updated project files and `.gitignore` to keep build, distribution, and virtual environment files out of the repository.

### Notes

* SFM remains local-first, deterministic, and rule-based.
* No AI is required for file detection or organization.
* Existing safety features such as preview and undo remain part of the workflow.
