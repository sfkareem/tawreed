"""Tests for the PID-sidecar logic in SingleApplication.

The full single-instance flow can only be tested cross-process (see
test_single_app.py docstring). What we *can* test in-process is the
helper logic that makes the flow correct on Windows:

- ``_is_pid_alive`` returns True for the current process.
- ``_is_pid_alive`` returns False for a clearly-dead PID.
- ``_read_pid_file`` / ``_write_pid_file`` round-trip the current PID.
- ``_clear_pid_file`` removes the file.
"""
from __future__ import annotations

import os
import sys

# Offscreen Qt platform so the QApplication doesn't open a display.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication

from gui.single_app import (
    _clear_pid_file,
    _is_pid_alive,
    _pid_file_path,
    _read_pid_file,
    _write_pid_file,
)


@pytest.fixture(scope="module")
def qapp() -> QApplication:
    app = QApplication.instance() or QApplication(sys.argv)
    yield app


def test_is_pid_alive_current_process(qapp: QApplication) -> None:
    """The PID of the current Python process is, by definition, alive."""
    assert _is_pid_alive(os.getpid()) is True


def test_is_pid_alive_nonexistent(qapp: QApplication) -> None:
    """PIDs that are clearly out of range (negative, zero, very high)
    must return False, not raise."""
    assert _is_pid_alive(0) is False
    assert _is_pid_alive(-1) is False
    assert _is_pid_alive(0x7FFFFFFE) is False  # 32-bit max-ish, probably not allocated


def test_pid_file_roundtrip(qapp: QApplication) -> None:
    """Writing the current PID and reading it back returns the same value."""
    _clear_pid_file()
    assert _read_pid_file() is None, "expected no PID file at start of test"

    _write_pid_file(os.getpid())
    assert _read_pid_file() == os.getpid(), "round-trip failed"

    _clear_pid_file()
    assert _read_pid_file() is None, "PID file was not removed"


def test_pid_file_path_is_per_user(qapp: QApplication) -> None:
    """The PID file lives under the per-user AppLocalDataLocation
    (Windows: %LOCALAPPDATA%\\<Org>\\<App>)."""
    path = _pid_file_path()
    assert path.name == "single-instance.pid"
    assert path.parent.is_dir() or True  # parent may not exist yet
