# Smart File Manager - Requirements & Installation Guide

Welcome! This guide explains everything you need to run **Smart File Manager** on your computer.

---

# System Requirements

## Operating System

* Windows 10 (64-bit)
* Windows 11 (64-bit)

> Linux and macOS are not officially tested yet.

---

# Python Version

Smart File Manager requires:

* Python **3.11** or newer

You can download Python from:

https://www.python.org/downloads/

After installation, verify it by running:

```bash
python --version
```

or

```bash
py --version
```

---

# Required Python Packages

Install all required dependencies using:

```bash
pip install PyQt6 watchdog send2trash
```

Or install them individually:

```bash
pip install PyQt6
pip install watchdog
pip install send2trash
```

---

# What Each Dependency Does

## PyQt6

Provides the graphical user interface (GUI) for Smart File Manager.

Used for:

* Windows
* Buttons
* Lists
* Dialogs
* Progress bars
* Menus
* Themes

---

## Watchdog

Monitors folders in real time.

Used for:

* Auto Mode
* Detecting new files
* Live file monitoring

---

## Send2Trash

Safely moves files to the Windows Recycle Bin instead of permanently deleting them.

---

# Standard Python Modules

The following modules are included with Python and **do not need to be installed**:

* os
* sys
* json
* pathlib
* shutil
* threading
* datetime
* logging
* traceback
* time

---

# Running the Application

Navigate to the project folder:

```bash
cd smart-file-manager
```

Run the application:

```bash
python smart_file_manager.py
```

or

```bash
py smart_file_manager.py
```

---

# Troubleshooting

## "ModuleNotFoundError"

Install the missing dependency:

```bash
pip install <module-name>
```

Example:

```bash
pip install PyQt6
```

---

## Python Is Not Recognized

Reinstall Python and enable:

**Add Python to PATH**

during installation.

---

## Permission Errors

Run the application using a normal user account with permission to access the selected folders.

---

## Auto Mode Does Not Work

Check that:

* Watchdog is installed
* Auto Mode is enabled in the application settings
* The selected folder still exists

---

# Recommended Environment

Using a virtual environment is recommended:

```bash
python -m venv venv
```

Activate it:

### Windows

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install PyQt6 watchdog send2trash
```

---

# Need Help?

If you encounter any issues while installing or running Smart File Manager:

* Open a GitHub Issue
* Start a GitHub Discussion
* Check the project documentation

---

Thank you for trying Smart File Manager!

I hope you enjoy using the project as much as I enjoyed building it.
