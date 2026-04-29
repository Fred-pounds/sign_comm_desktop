import os
import sys


def app_root():
    """Return the app root in source mode or the PyInstaller extraction dir."""
    if hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def resource_path(*parts):
    """Build an absolute path to a bundled or source resource."""
    return os.path.join(app_root(), *parts)
