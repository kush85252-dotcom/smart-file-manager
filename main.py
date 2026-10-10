"""Smart File Manager launcher."""

from smart_file_manager.app import *

if __name__ == "__main__":
    import runpy
    runpy.run_module("smart_file_manager", run_name="__main__")
