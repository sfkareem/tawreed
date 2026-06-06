use std::fs;
use std::path::PathBuf;
use directories::UserDirs;
use rusqlite::{Connection, Result};

pub struct DbState {
    pub conn: std::sync::Mutex<rusqlite::Connection>,
}

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

#[derive(serde::Serialize, serde::Deserialize)]
pub struct Settings {
    pub api_key: String,
    pub model_id: String,
    pub base_url: String,
}

pub fn get_db_path() -> Result<PathBuf, String> {
    let user_dirs = UserDirs::new().ok_or("Could not find user home directory")?;
    Ok(user_dirs.home_dir().join(".tawreed").join("db").join("tawreed.db"))
}

pub fn get_config_path() -> Result<PathBuf, String> {
    let user_dirs = UserDirs::new().ok_or("Could not find user home directory")?;
    Ok(user_dirs.home_dir().join(".tawreed").join("config.json"))
}

pub fn get_settings() -> Result<Settings, String> {
    let config_path = get_config_path()?;
    if config_path.exists() {
        let content = fs::read_to_string(&config_path).map_err(|e| e.to_string())?;
        let settings: Settings = serde_json::from_str(&content).map_err(|e| e.to_string())?;
        Ok(settings)
    } else {
        Ok(Settings {
            api_key: "".to_string(),
            model_id: "MiniMax-M3".to_string(),
            base_url: "https://api.minimax.io/v1".to_string(),
        })
    }
}

pub fn save_settings(settings: Settings) -> Result<(), String> {
    let config_path = get_config_path()?;
    if let Some(parent) = config_path.parent() {
        let _ = fs::create_dir_all(parent);
    }
    let content = serde_json::to_string_pretty(&settings).map_err(|e| e.to_string())?;
    fs::write(&config_path, content).map_err(|e| e.to_string())?;
    Ok(())
}

#[derive(serde::Serialize)]
pub struct HistoryRecord {
    pub id: i64,
    pub timestamp: String,
    pub project_name: String,
    pub packages_count: i64,
    pub output_path: String,
}

pub fn get_history(conn: &Connection) -> Result<Vec<HistoryRecord>, String> {
    let mut stmt = conn.prepare("SELECT id, timestamp, project_name, packages_count, output_path FROM history ORDER BY id DESC").map_err(|e| e.to_string())?;
    let rows = stmt.query_map([], |row| {
        Ok(HistoryRecord {
            id: row.get(0)?,
            timestamp: row.get(1)?,
            project_name: row.get(2)?,
            packages_count: row.get(3)?,
            output_path: row.get(4)?,
        })
    }).map_err(|e| e.to_string())?;
    
    let history: rusqlite::Result<Vec<HistoryRecord>> = rows.collect();
    history.map_err(|e| e.to_string())
}

pub fn add_history(conn: &Connection, project_name: &str, packages_count: i64, output_path: &str) -> Result<(), String> {
    let timestamp = chrono::Local::now().format("%Y-%m-%d %H:%M:%S").to_string();
    conn.execute(
        "INSERT INTO history (timestamp, project_name, packages_count, output_path) VALUES (?1, ?2, ?3, ?4)",
        rusqlite::params![timestamp, project_name, packages_count, output_path],
    ).map_err(|e| e.to_string())?;
    Ok(())
}
