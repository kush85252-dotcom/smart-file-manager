# Smart File Manager

The original single-file application is now organized as a small Python
package without changing its Qt UI or filesystem features.

## Run

```bash
python organizer.py
```

or:

```bash
python -m smart_file_manager
```

PyQt6 remains the only application dependency.

## Architecture

- `smart_file_manager/app.py` owns application startup.
- `smart_file_manager/ui/main_window.py` owns Qt widgets, signals, dialogs,
  navigation, and presentation state.
- `smart_file_manager/ui/styles.py` holds the existing stylesheet.
- `smart_file_manager/services/file_operations.py` owns primitive filesystem
  actions.
- `smart_file_manager/services/organizer.py` owns organization planning,
  collision-safe moves, and undo execution.
- `smart_file_manager/categorization.py` owns extension rules.
- `smart_file_manager/config.py` owns app constants and startup path policy.
- `smart_file_manager/utils.py` owns size/date formatting.
- `smart_file_manager/logging_config.py` is the isolated logging extension
  point.  Auto Mode, watchdog monitoring, JSON settings, and reports were not
  present in the original application, so they were not invented here.

`organizer.py` remains as a compatibility launcher and re-exports the original
public helper names and `SFM_Lite` class.