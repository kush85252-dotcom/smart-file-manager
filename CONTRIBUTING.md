# Contributing to Smart File Manager

Thank you for your interest in contributing to Smart File Manager.

Smart File Manager is a desktop file organization application built with Python, PyQt6, Watchdog, pathlib, and JSON-based configuration. Contributions should focus on improving the application's reliability, usability, performance, and file-organization capabilities.

## Before Contributing

Please:

1. Read the project's `README.md`.
2. Check existing issues and pull requests before opening a new one.
3. Make sure your proposed change is relevant to Smart File Manager.
4. Test your changes locally before submitting a pull request.
5. Avoid unrelated changes in the same pull request.

## Development Setup

### Requirements

* Python 3.x
* Git
* PyQt6
* Watchdog
* Any other dependencies listed by the project

Clone the repository and install the required dependencies:

```bash
git clone <https://github.com/kush85252-dotcom/smart-file-manager>
cd <repository-folder>
pip install -r requirements.txt
```

Run the application using the project's normal startup command.

## Making Changes

When working on Smart File Manager:

* Keep changes focused and understandable.
* Follow the existing project structure.
* Avoid unnecessary rewrites of working code.
* Preserve existing functionality unless the change intentionally modifies it.
* Handle file-system operations carefully.
* Do not introduce destructive file operations without appropriate safeguards.
* Keep configuration changes compatible with the existing JSON configuration system where possible.
* Do not commit personal configuration files, temporary files, generated files, or sensitive information.

## File Operations

Smart File Manager interacts directly with files and folders, so file-system changes require extra care.

Contributors should:

* Test file operations with temporary test directories.
* Verify paths before moving or modifying files.
* Handle missing files and folders gracefully.
* Avoid permanently deleting user files unless the feature explicitly requires it and appropriate safety mechanisms exist.
* Consider permission errors and inaccessible files.
* Make sure failed operations do not leave the application in an inconsistent state.

## Pull Requests

Before opening a pull request:

* Test the application.
* Check for Python errors and warnings.
* Verify that existing features still work.
* Review your changes with Git.
* Remove debugging code and unnecessary files.
* Write a clear pull request title and description.

A good pull request should explain:

* What was changed.
* Why the change was needed.
* How it was tested.
* Any known limitations.

## Bug Fixes

For bug fixes, include enough information to reproduce and verify the issue.

If possible, provide:

* The problem.
* Steps to reproduce it.
* Expected behavior.
* Actual behavior.
* The fix that was implemented.
* Testing performed after the fix.

## New Features

New features should fit the purpose of Smart File Manager.

Before implementing a large feature, consider opening an issue or discussion to explain the idea first. This helps avoid duplicated work and allows the project's direction to be considered before significant development effort is spent.

## Code Quality

Please keep the code:

* Readable.
* Maintainable.
* Modular where appropriate.
* Consistent with the existing project.
* Properly error-handled.
* Free of unnecessary complexity.

Avoid adding dependencies unless they provide a clear benefit to the application.

## Commit Messages

Use clear commit messages that describe the change.

Examples:

```text
Fix folder loading on startup
Add organization report
Improve file watcher handling
Fix settings synchronization
```

Avoid vague messages such as:

```text
update
stuff
changes
fixed
```

## Reporting Security Issues

Do not publicly disclose serious security vulnerabilities before they can be investigated.

Follow the instructions in `SECURITY.md` for reporting security-related issues.

## Scope

Contributions should be related specifically to Smart File Manager.

This includes improvements to:

* File organization.
* Folder management.
* File monitoring.
* Application settings.
* User interface.
* Reports.
* Performance.
* Reliability.
* Error handling.
* Documentation.
* Testing.

Unrelated projects, experimental features with no connection to Smart File Manager, or changes that significantly alter the application's purpose may not be accepted.

## Contributor Expectations

By contributing, you agree to:

* Make honest and useful contributions.
* Respect other contributors.
* Keep discussions focused on the project.
* Provide accurate information about testing and changes.
* Avoid intentionally introducing harmful or destructive behavior.

Thank you for helping improve Smart File Manager.
