use std::fs;
use std::path::PathBuf;
use directories::UserDirs;
use rusqlite::{Connection, Result};

pub fn init_tawreed_env() -> Result<PathBuf, String> {
    let user_dirs = UserDirs::new().ok_or("Could not find user home directory")?;
    let tawreed_dir = user_dirs.home_dir().join(".tawreed");
    
    let data_dir = tawreed_dir.join("data");
    let logs_dir = tawreed_dir.join("logs");
    let db_dir = tawreed_dir.join("db");
    
    fs::create_dir_all(&data_dir).map_err(|e| e.to_string())?;
    fs::create_dir_all(&logs_dir).map_err(|e| e.to_string())?;
    fs::create_dir_all(&db_dir).map_err(|e| e.to_string())?;
    
    let db_path = db_dir.join("tawreed.db");
    let conn = Connection::open(&db_path).map_err(|e| e.to_string())?;
    
    conn.execute(
        "CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY,
            api_key TEXT,
            model_id TEXT,
            language TEXT
        )",
        [],
    ).map_err(|e| e.to_string())?;

    conn.execute(
        "CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY,
            timestamp TEXT,
            project_name TEXT,
            packages_count INTEGER,
            output_path TEXT
        )",
        [],
    ).map_err(|e| e.to_string())?;

    Ok(tawreed_dir)
}
