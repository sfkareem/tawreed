"""Shared pytest fixtures and configuration for the tawreed test suite.

Centralises three things that used to be duplicated across every
test file:

1. ``QT_QPA_PLATFORM=offscreen`` — required for any test that
   instantiates a ``QWidget`` (otherwise the test would try to open
   a real window). Set before any PySide6 import.

2. The ``sys.path`` mutation that lets the test files import
   ``core``, ``gui``, ``tawreed_app`` when the project is not
   installed (i.e. when running ``pytest`` from a fresh checkout
   without ``pip install -e .``).

3. A common ``isolated_tawreed_dir`` fixture that points ``core.db``
   at a tmp_path so tests never touch the real ``~/.tawreed/``.
"""
from __future__ import annotations

import os
import sys
import sqlite3
from pathlib import Path

# 1. Qt must be set up BEFORE any PySide6 import. This is a no-op
# when there's no DISPLAY (e.g. CI), and tells Qt to render to a
# hidden buffer instead of trying to open a real window.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# 2. Make the project root importable so `import core` works
# without `pip install -e .`. Belt-and-braces: the project's
# pyproject.toml also lists these as setuptools packages.
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import pytest  # noqa: E402  (must come after the sys.path mutation)


@pytest.fixture
def isolated_tawreed_dir(tmp_path, monkeypatch):
    """Point ``core.db`` at a tmp dir so tests never touch the real
    ``~/.tawreed/``.

    This is the shared base fixture every test that exercises the
    state tree should use. Resets the module-level path constants
    AND neutralises the legacy-location detection (so a test
    doesn't accidentally pick up the developer's real machine
    state and copy it into the tmp dir).
    """
    import core.db as db
    monkeypatch.setattr(db, "TAWREED_DIR", str(tmp_path))
    monkeypatch.setattr(db, "DB_DIR", str(tmp_path / "db"))
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "db" / "tawreed.db"))
    monkeypatch.setattr(db, "CONFIG_PATH", str(tmp_path / "config.json"))
    monkeypatch.setattr(db, "OUTPUTS_DIR", str(tmp_path / "outputs"))
    monkeypatch.setattr(db, "LOGS_DIR", str(tmp_path / "logs"))
    monkeypatch.setattr(db, "PID_FILE_PATH", str(tmp_path / "single-instance.pid"))
    # Neutralise the legacy-location detection so a test never
    # accidentally picks up the developer's real machine state.
    monkeypatch.setattr(db, "_detect_legacy_locations", lambda: [])
    (tmp_path / "db").mkdir(exist_ok=True)
    (tmp_path / "outputs").mkdir(exist_ok=True)
    return tmp_path
