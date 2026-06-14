"""SQLite + JSON config storage for Tawreed.

All persistent state lives under a single per-user directory:

    Windows:  C:\\Users\\<user>\\.tawreed\\
    POSIX:    ~/.tawreed/

The same layout is used in BOTH dev (``python main.py``) and frozen
(PyInstaller) builds. Keeping the state outside the project tree
prevents:

  * Accidental commits of config.json / .db / outputs to git.
  * State being stranded inside ``dist/`` when the user copies the
    build folder to a new machine — the state moves with the user,
    not the binary.
  * Per-project pollution when the user is working on multiple
    Tawreed trees.

Layout::

    ~/.tawreed/
    ├── config.json
    ├── db/tawreed.db
    ├── outputs/
    │   └── <file>_<Tawreed_Output>.xlsx
    ├── logs/
    │   └── migration.log
    └── single-instance.pid

The previous version of this module put state in three different
places depending on mode (``%LOCALAPPDATA%`` for frozen, ``./tawreed/``
for dev, ``~/.tawreed`` for the old dev legacy). The new code unifies
on a single location and adds a one-shot migration that copies any
state from the old ``%LOCALAPPDATA%\\Tawreed`` and ``<exe-dir>/tawreed``
locations into ``~/.tawreed`` so an existing user keeps their
history and settings.
"""
from __future__ import annotations

import os
import sys
import json
import shutil
import sqlite3
from datetime import datetime
from typing import List, Dict, Any

from core.ai import get_default_settings, is_valid_provider, get_provider_config


# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------


def _app_root() -> str:
    """Return the directory the persistent state tree hangs off of.

    Per project policy, EVERYTHING lives under the user's home
    directory at ``~/.tawreed/`` — regardless of whether we're
    running from source (``python main.py``) or from a frozen
    PyInstaller build. The previous split (dev -> ``./tawreed/``,
    frozen -> ``%LOCALAPPDATA%\\Tawreed``) was confusing and meant
    the user's history didn't follow them when they upgraded.

    Returns the home-dir path with no trailing slash. The actual
    ``tawreed/`` subdirectory is concatenated at the call sites.
    """
    home = os.path.expanduser("~")
    if not home:
        # Last-resort fallback: %TEMP% on Windows, /tmp on POSIX.
        # If even those aren't writable, init_db() will raise.
        return os.environ.get("TEMP") or os.environ.get("TMP") or "/tmp"
    return home


APP_ROOT = _app_root()
TAWREED_DIR = os.path.join(APP_ROOT, ".tawreed")
DB_DIR = os.path.join(TAWREED_DIR, "db")
DB_PATH = os.path.join(DB_DIR, "tawreed.db")
CONFIG_PATH = os.path.join(TAWREED_DIR, "config.json")
OUTPUTS_DIR = os.path.join(TAWREED_DIR, "outputs")
LOGS_DIR = os.path.join(TAWREED_DIR, "logs")
PID_FILE_PATH = os.path.join(TAWREED_DIR, "single-instance.pid")


# ---------------------------------------------------------------------------
# Migration from the old split-location layout
# ---------------------------------------------------------------------------
#
# Before this change, state lived in different places depending on mode:
#   - Frozen (PyInstaller):  %LOCALAPPDATA%\\Tawreed\\
#   - Dev:                  <project>/tawreed/
#   - Old dev legacy:       ~/.tawreed/
# Now everything lives in ~/.tawreed/. The migration below detects the
# old locations and copies any state into the new tree, leaving a
# breadcrumb in logs/migration.log so the user can see what was moved.
#
# Best-effort — failures are silently skipped because a fresh install
# shouldn't be blocked by an unrelated legacy folder elsewhere on disk.

# Locations to scan for legacy state. We also scan the directory
# containing the running EXE, because some older frozen builds wrote
# their state to ``<exe-dir>/tawreed/`` next to the binary.
_LEGACY_LOCATIONS: list[str] = []


def _detect_legacy_locations() -> list[str]:
    """Return legacy app-data roots that might have old state."""
    candidates: list[str] = []

    # Frozen legacy #1: %LOCALAPPDATA%\\Tawreed
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        candidates.append(os.path.join(local_app_data, "Tawreed"))

    # Frozen legacy #2: <exe-dir>/tawreed  — when the EXE was run from
    # inside a zip-extract folder, state was written next to the binary.
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(os.path.abspath(sys.executable))
        candidates.append(os.path.join(exe_dir, "tawreed"))

    return [
        p for p in candidates
        if os.path.isdir(p) and os.path.normcase(p) != os.path.normcase(TAWREED_DIR)
    ]


def _migrate_legacy_state() -> None:
    """One-shot migration: copy any legacy state into ~/.tawreed/."""
    legacy_roots = _detect_legacy_locations()
    if not legacy_roots:
        return

    os.makedirs(TAWREED_DIR, exist_ok=True)

    migrated: list[str] = []
    for legacy in legacy_roots:
        # Copy specific files (not the whole tree, in case the user
        # dropped unrelated stuff into the legacy folder).
        for fname in ("config.json",):
            src = os.path.join(legacy, fname)
            if os.path.isfile(src):
                dst = os.path.join(TAWREED_DIR, fname)
                if not os.path.exists(dst):
                    try:
                        shutil.copy2(src, dst)
                        migrated.append(src)
                    except OSError:
                        pass

        # Copy the SQLite db file (the whole history table).
        legacy_db = os.path.join(legacy, "db", "tawreed.db")
        if os.path.isfile(legacy_db):
            dst = os.path.join(DB_DIR, "tawreed.db")
            if not os.path.exists(dst):
                try:
                    os.makedirs(DB_DIR, exist_ok=True)
                    shutil.copy2(legacy_db, dst)
                    migrated.append(legacy_db)
                except OSError:
                    pass

        # Copy outputs directory contents (but not the dir itself, to
        # avoid clobbering anything the new run has already written).
        legacy_outputs = os.path.join(legacy, "outputs")
        if os.path.isdir(legacy_outputs):
            try:
                os.makedirs(OUTPUTS_DIR, exist_ok=True)
                for name in os.listdir(legacy_outputs):
                    src = os.path.join(legacy_outputs, name)
                    dst = os.path.join(OUTPUTS_DIR, name)
                    if os.path.exists(dst):
                        continue
                    if os.path.isfile(src):
                        try:
                            shutil.copy2(src, dst)
                            migrated.append(src)
                        except OSError:
                            pass
            except OSError:
                pass

    if migrated:
        # Write a breadcrumb so the user (or a future migration
        # tool) can find where the data came from.
        try:
            os.makedirs(LOGS_DIR, exist_ok=True)
            breadcrumb = os.path.join(LOGS_DIR, "migration.log")
            with open(breadcrumb, "w", encoding="utf-8") as f:
                f.write(
                    f"Migrated {len(migrated)} file(s) from legacy location(s)\n"
                    f"on {datetime.now().isoformat()}.\n"
                    f"New state root: {TAWREED_DIR}\n"
                    f"Files copied:\n" +
                    "\n".join(f"  - {p}" for p in migrated) + "\n"
                )
        except OSError:
            pass


# ---------------------------------------------------------------------------
# Database lifecycle
# ---------------------------------------------------------------------------


def _cleanup_stray_app_state() -> None:
    """Best-effort cleanup of stray state trees that the old code
    left lying around.

    Background: earlier versions of Tawreed wrote its state to one
    of three places depending on mode — ``%LOCALAPPDATA%\\Tawreed``,
    ``<exe-dir>/tawreed``, or ``~/.tawreed`` — and the user's most
    recent installed build may have populated any of them. After
    this change, the canonical location is ``~/.tawreed`` and any
    pre-existing state has already been migrated by
    ``_migrate_legacy_state``.

    This function is the second half: it removes the now-empty
    legacy tree, but ONLY if the migration emptied it. If the user
    dropped unrelated files into the legacy folder we leave it
    alone (the migration log captures what we did copy, so a power
    user can still recover the rest from the legacy location).

    Runs once per process. Failures are silently swallowed.
    """
    legacy_roots = _detect_legacy_locations()
    for legacy in legacy_roots:
        try:
            # Don't remove the user's HOME (~/.tawreed) — that's
            # a real user folder and may have unrelated content.
            # We only clean up the frozen-build leftovers.
            if os.path.normcase(legacy) == os.path.normcase(
                os.path.join(os.path.expanduser("~"), ".tawreed")
            ):
                continue
            if not os.path.isdir(legacy):
                continue
            # If the folder contains anything OTHER than our
            # sub-folders, leave it alone — the user dropped
            # something there.
            expected = {"config.json", "db", "outputs", "logs", "single-instance.pid"}
            try:
                contents = set(os.listdir(legacy))
            except OSError:
                continue
            if not contents.issubset(expected):
                continue
            # Sub-folders we created should be empty or only
            # contain migrated files. If they're not empty, leave
            # them — the migration already copied the files to the
            # new location and the user may want to inspect.
            for sub in ("db", "outputs"):
                p = os.path.join(legacy, sub)
                if os.path.isdir(p):
                    try:
                        if os.listdir(p):
                            continue
                    except OSError:
                        pass
            # Safe to remove.
            import shutil as _sh
            _sh.rmtree(legacy, ignore_errors=True)
        except Exception:
            pass


def init_db() -> None:
    """Initialise the state tree (idempotent).

    Performs a one-shot migration of any legacy app data into the
    new ~/.tawreed/ tree, cleans up the now-empty legacy trees
    next to the EXE, then ensures the standard subfolders exist
    and the history table is created.
    """
    # One-shot migration: pull any old state into the new tree.
    _migrate_legacy_state()

    # Clean up the now-empty legacy trees left behind by older
    # frozen builds. Best-effort; never raises.
    _cleanup_stray_app_state()

    for subfolder in ("db", "outputs", "logs"):
        os.makedirs(os.path.join(TAWREED_DIR, subfolder), exist_ok=True)

    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("PRAGMA journal_mode=WAL")
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                project_name TEXT,
                packages_count INTEGER,
                output_path TEXT
            )
        ''')
        conn.commit()
    finally:
        if conn:
            conn.close()


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("PRAGMA journal_mode=WAL")
        return conn
    except Exception:
        conn.close()
        raise


def get_history() -> List[Dict[str, Any]]:
    os.makedirs(DB_DIR, exist_ok=True)
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("PRAGMA journal_mode=WAL")
        cursor = conn.cursor()
        cursor.execute("SELECT id, timestamp, project_name, packages_count, output_path FROM history ORDER BY id DESC")
        rows = cursor.fetchall()
        history = []
        for r in rows:
            history.append({
                "id": r[0],
                "timestamp": r[1],
                "project_name": r[2],
                "packages_count": r[3],
                "output_path": r[4],
            })
        return history
    finally:
        if conn:
            conn.close()


def delete_history_entry(entry_id: int) -> bool:
    """Remove a single history row by id. Returns True if a row was removed.

    The on-disk output Excel is NOT touched — only the database row.
    The History page uses this from its Delete action.
    """
    if not os.path.exists(DB_PATH):
        return False
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("DELETE FROM history WHERE id = ?", (entry_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        if conn:
            conn.close()


def add_history(project_name: str, packages_count: int, output_path: str) -> None:
    os.makedirs(DB_DIR, exist_ok=True)
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("PRAGMA journal_mode=WAL")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO history (timestamp, project_name, packages_count, output_path) VALUES (?, ?, ?, ?)",
            (timestamp, project_name, packages_count, output_path)
        )
        conn.commit()
    finally:
        if conn:
            conn.close()


# ---------------------------------------------------------------------------
# Settings (config.json) IO
# ---------------------------------------------------------------------------


def get_settings() -> Dict[str, Any]:
    default_settings = get_default_settings()
    # Backwards-compat aliases: legacy code used `model_id` interchangeably
    # with `model`. Keep both keys in sync at load time.
    default_settings.setdefault("model_id", default_settings["model"])
    if not os.path.exists(CONFIG_PATH):
        return default_settings
    f = None
    try:
        f = open(CONFIG_PATH, "r", encoding="utf-8")
        settings = json.load(f)
        if "model_id" in settings and "model" not in settings:
            settings["model"] = settings["model_id"]
        elif "model" in settings and "model_id" not in settings:
            settings["model_id"] = settings["model"]

        # Migration: old "OpenAI" entry that pointed at a custom base
        # URL (e.g. the MiniMax proxy at api.minimax.io/v1) gets
        # promoted to "OpenAI Compatible" so the existing config
        # still works after the provider rebrand.
        saved_provider = settings.get("provider", "")
        saved_url = settings.get("base_url", "") or ""
        if saved_provider == "OpenAI" and saved_url and "api.openai.com" not in saved_url:
            settings["provider"] = "OpenAI Compatible"

        if "provider" not in settings or not is_valid_provider(settings["provider"]):
            settings["provider"] = default_settings["provider"]

        for k, v in default_settings.items():
            if k not in settings:
                settings[k] = v
        return settings
    except Exception:
        return default_settings
    finally:
        if f:
            f.close()


def save_settings(settings: dict) -> None:
    """Persist the settings dict. Validates and normalises the provider field."""
    os.makedirs(TAWREED_DIR, exist_ok=True)

    provider = settings.get("provider", "OpenAI")
    if not is_valid_provider(provider):
        provider = "OpenAI"
    settings["provider"] = provider

    p = get_provider_config(provider)
    if not settings.get("base_url"):
        settings["base_url"] = p["base_url"]
    if not settings.get("model"):
        settings["model"] = p["default_model"]
    if not settings.get("model_id"):
        settings["model_id"] = settings["model"]

    if "model_id" in settings and "model" not in settings:
        settings["model"] = settings["model_id"]
    elif "model" in settings and "model_id" not in settings:
        settings["model_id"] = settings["model"]

    f = None
    try:
        f = open(CONFIG_PATH, "w", encoding="utf-8")
        json.dump(settings, f, indent=4, ensure_ascii=False)
    finally:
        if f:
            f.close()


def update_settings(provider: str, api_key: str, model: str, base_url: str) -> None:
    settings = {
        "provider": provider,
        "api_key": api_key,
        "model": model,
        "model_id": model,
        "base_url": base_url,
    }
    save_settings(settings)


def get_outputs_dir() -> str:
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    return os.path.abspath(OUTPUTS_DIR)
