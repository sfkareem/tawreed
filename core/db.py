import os
import sys
import json
import sqlite3
from datetime import datetime
from typing import List, Dict, Any

from core.ai import get_default_settings, is_valid_provider, get_provider_config

# Root directory for Tawreed configurations and database
if getattr(sys, 'frozen', False):
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        TAWREED_DIR = os.path.join(local_app_data, "Tawreed")
    else:
        TAWREED_DIR = os.path.expanduser("~/AppData/Local/Tawreed")
else:
    TAWREED_DIR = os.path.expanduser("~/.tawreed")

DB_DIR = os.path.join(TAWREED_DIR, "db")
DB_PATH = os.path.join(DB_DIR, "tawreed.db")
CONFIG_PATH = os.path.join(TAWREED_DIR, "config.json")
OUTPUTS_DIR = os.path.join(TAWREED_DIR, "outputs")

def init_db() -> None:
    # Ensure directory structure exists
    for subfolder in ["data", "logs", "db", "outputs"]:
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
    # Ensure db path folder exists
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
                "output_path": r[4]
            })
        return history
    finally:
        if conn:
            conn.close()

def add_history(project_name: str, packages_count: int, output_path: str) -> None:
    # Ensure db path folder exists
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
        # Ensure model maps to model_id and vice versa
        if "model_id" in settings and "model" not in settings:
            settings["model"] = settings["model_id"]
        elif "model" in settings and "model_id" not in settings:
            settings["model_id"] = settings["model"]

        # Migrate: if the stored provider is not one we recognise
        # (e.g. user upgraded from an older build), fall back to the default.
        if "provider" not in settings or not is_valid_provider(settings["provider"]):
            settings["provider"] = default_settings["provider"]

        # Ensure all default keys exist, merging in any missing values.
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
    # Ensure directory structure exists
    os.makedirs(TAWREED_DIR, exist_ok=True)

    # Validate the provider; if invalid, leave the previous value alone
    # (the Settings UI is expected to send a valid name).
    provider = settings.get("provider", "OpenAI")
    if not is_valid_provider(provider):
        provider = "OpenAI"
    settings["provider"] = provider

    # Auto-fill base_url and model from the provider config if the user
    # left them blank or the values are clearly stale.
    p = get_provider_config(provider)
    if not settings.get("base_url"):
        settings["base_url"] = p["base_url"]
    if not settings.get("model"):
        settings["model"] = p["default_model"]
    if not settings.get("model_id"):
        settings["model_id"] = settings["model"]

    # Ensure model and model_id are in sync
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
        "base_url": base_url
    }
    save_settings(settings)

def get_outputs_dir() -> str:
    # Ensure outputs directory exists
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    return os.path.abspath(OUTPUTS_DIR)
