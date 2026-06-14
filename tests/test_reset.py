"""Tests for the wipe-everything reset path.

We never touch the real TAWREED_DIR — every test points core.db at
a tmp_path so the user's actual config / history / outputs are
untouched.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

import core.db as db
import core.reset as reset_mod


@pytest.fixture
def isolated_tawreed_dir(tmp_path, monkeypatch):
    """Point core.db at a tmp dir and create the standard subfolders.

    Also neutralises the legacy-location detection in ``core.db`` so
    the migration code doesn't accidentally pick up the developer's
    real machine state (e.g. the real ``dist/Tawreed/tawreed/`` from
    their last smoke test) and copy it into the test sandbox.
    """
    monkeypatch.setattr(db, "TAWREED_DIR", str(tmp_path))
    monkeypatch.setattr(db, "DB_DIR", str(tmp_path / "db"))
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "db" / "tawreed.db"))
    monkeypatch.setattr(db, "CONFIG_PATH", str(tmp_path / "config.json"))
    monkeypatch.setattr(db, "OUTPUTS_DIR", str(tmp_path / "outputs"))
    monkeypatch.setattr(db, "_detect_legacy_locations", lambda: [])
    for sub in ("db", "outputs"):
        (tmp_path / sub).mkdir(exist_ok=True)
    return tmp_path


def _write_config(p: Path) -> None:
    p.write_text(
        '{"provider": "OpenAI", "api_key": "sk-test-abc123", "model": "MiniMax-M3"}',
        encoding="utf-8",
    )


def _seed_history(n: int) -> None:
    db.init_db()
    conn = sqlite3.connect(db.DB_PATH)
    cur = conn.cursor()
    for i in range(n):
        cur.execute(
            "INSERT INTO history (timestamp, project_name, packages_count, output_path) "
            "VALUES (?, ?, ?, ?)",
            (f"2026-06-13 1{i:02d}:00", f"Project {i}", i + 1, f"/tmp/p{i}.xlsx"),
        )
    conn.commit()
    conn.close()


def _seed_outputs(n: int) -> list[Path]:
    out = []
    for i in range(n):
        p = Path(db.OUTPUTS_DIR) / f"run_{i}.xlsx"
        p.write_bytes(b"fake xlsx content")
        out.append(p)
    return out


def test_reset_deletes_config(isolated_tawreed_dir):
    cfg = Path(db.CONFIG_PATH)
    _write_config(cfg)
    assert cfg.exists()

    report = reset_mod.reset_all()
    assert report.config_deleted is True
    assert not cfg.exists()


def test_reset_truncates_history(isolated_tawreed_dir):
    _seed_history(5)
    report = reset_mod.reset_all()
    assert report.history_rows_deleted == 5
    # Table still exists, just empty.
    conn = sqlite3.connect(db.DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM history")
    assert cur.fetchone()[0] == 0
    conn.close()


def test_reset_clears_outputs(isolated_tawreed_dir):
    files = _seed_outputs(3)
    assert all(f.exists() for f in files)

    report = reset_mod.reset_all()
    assert report.outputs_deleted == 3
    assert not any(f.exists() for f in files)
    # The outputs/ directory itself is preserved.
    assert Path(db.OUTPUTS_DIR).is_dir()


def test_reset_handles_missing_files_gracefully(isolated_tawreed_dir):
    """Fresh install — nothing to delete. Should not raise."""
    report = reset_mod.reset_all()
    assert report.config_deleted is False
    assert report.history_rows_deleted == 0
    assert report.outputs_deleted == 0


def test_reset_clears_qsettings(monkeypatch):
    """Mock QSettings so we don't pollute the user's real registry."""
    from PySide6.QtCore import QSettings

    calls = {"cleared": False}

    class FakeSettings:
        def clear(self):
            calls["cleared"] = True

        def sync(self):
            pass

    monkeypatch.setattr(QSettings, "__init__", lambda self, *a, **kw: None)
    monkeypatch.setattr(QSettings, "clear", lambda self: calls.__setitem__("cleared", True))
    monkeypatch.setattr(QSettings, "sync", lambda self: None)

    assert reset_mod._clear_qsettings() is True
    assert calls["cleared"] is True


def test_reset_returns_human_summary(isolated_tawreed_dir):
    # Make sure no other test left outputs in the shared tmp dir.
    for stale in Path(db.OUTPUTS_DIR).iterdir():
        if stale.is_file():
            stale.unlink()
    _write_config(Path(db.CONFIG_PATH))
    _seed_history(2)
    _seed_outputs(4)
    import sys

    sys.stderr.write("DEBUG OUTPUTS_DIR: " + str(db.OUTPUTS_DIR) + "\n")
    sys.stderr.write("DEBUG contents: " + str(list(Path(db.OUTPUTS_DIR).iterdir())) + "\n")
    sys.stderr.flush()
    report = reset_mod.reset_all()
    sys.stderr.write("DEBUG outputs_deleted: " + str(report.outputs_deleted) + "\n")
    sys.stderr.flush()
    s = report.human_summary()
    assert "API key" in s
    assert "2 history row" in s
    assert "4 output file" in s
    assert "Window" in s
    assert "Tawreed will restart" in s
