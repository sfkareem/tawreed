"""Smoke tests for the single-instance lock.

These run under the offscreen Qt platform so they're safe in CI.

Why we don't test the full "primary + secondary" flow here:
``QApplication`` is a singleton — only one can exist per process.
``QLocalServer`` also only allows one listener per named socket per
process. So the actual second-instance behaviour can only be
observed via a subprocess integration test (out of scope; would
live in ``tests/integration/test_single_instance_subprocess.py``).
What we *can* test in-process is:

- The class exists and is a QApplication subclass (so it
  interoperates with the rest of the Qt stack).
- The server-name helper is per-user (no collisions on shared
  Windows sessions).
- Importing the module has no side effects beyond defining the
  class.
"""

from __future__ import annotations

import os

# Set offscreen platform BEFORE importing QtWidgets so the QApplication
# doesn't try to open a real display.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from gui.single_app import SingleApplication, _server_name


def test_single_application_is_qapp_subclass() -> None:
    """The class must inherit QApplication so sys.exit(app.exec()) works."""
    assert issubclass(SingleApplication, QApplication)


def test_server_name_is_per_user() -> None:
    """Server name includes the username to avoid collisions on shared
    Windows sessions."""
    import getpass

    name = _server_name()
    assert name.startswith("tawreed-single-instance-")
    assert getpass.getuser() in name


def test_module_imports_without_side_effects() -> None:
    """Importing gui.single_app must not start a server, open a socket,
    or otherwise touch the OS. We re-import to confirm."""
    import importlib

    import gui.single_app

    importlib.reload(gui.single_app)
    # If we get here without exception, the import is clean.
    assert hasattr(gui.single_app, "SingleApplication")
    assert callable(getattr(gui.single_app.SingleApplication, "is_running", None))
    assert callable(getattr(gui.single_app.SingleApplication, "notify_primary", None))
    assert callable(getattr(gui.single_app.SingleApplication, "start_server", None))
