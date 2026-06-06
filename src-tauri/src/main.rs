// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod processor;
mod system;

use tauri::State;
use tracing_subscriber::fmt::writer::MakeWriterExt;
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

fn validate_path_in_outputs(path_str: &str) -> Result<(), String> {
    let path = std::path::Path::new(path_str);
    if !path.exists() {
        return Err("File does not exist".to_string());
    }

    let canonical_path = path.canonicalize().map_err(|e| e.to_string())?;
    let outputs_dir = system::get_outputs_dir()?;
    let canonical_outputs = outputs_dir.canonicalize().map_err(|e| e.to_string())?;

    if !canonical_path.starts_with(&canonical_outputs) {
        return Err("Path traversal detected".to_string());
    }

    Ok(())
}

#[tauri::command]
async fn process_boq(
    app: tauri::AppHandle,
    state: State<'_, system::DbState>,
    file_path: String,
    base_url: String,
    model: String,
    api_key: String,
) -> Result<String, String> {
    tracing::info!("Processing BOQ for file: {}", file_path);
    if !file_path.ends_with(".xlsx") && !file_path.ends_with(".xls") {
        tracing::error!("Invalid file format for: {}", file_path);
        return Err("File must be an Excel file (.xlsx or .xls)".to_string());
    }
    
    if let Err(e) = validate_path_in_outputs(&file_path) {
        tracing::error!("Path validation failed for {}: {}", file_path, e);
        return Err(e);
    }

    match processor::extract_work_packages(app, &file_path, &base_url, &model, &api_key).await {
        Ok((result_path, count)) => {
            tracing::info!("Extracted {} packages to {}", count, result_path);
            let project_name = file_path.split('\\').last().unwrap_or(&file_path).split('/').last().unwrap_or(&file_path).to_string();
            if let Ok(conn) = state.conn.lock() {
                let _ = system::add_history(&conn, &project_name, count, &result_path);
            } else {
                tracing::error!("Failed to lock database connection");
            }
            Ok(result_path)
        }
        Err(e) => {
            tracing::error!("Failed to extract work packages: {}", e);
            Err(e)
        }
    }
}

#[tauri::command]
fn get_settings(_state: State<'_, system::DbState>) -> Result<system::Settings, String> {
    system::get_settings()
}

#[tauri::command]
fn save_settings(_state: State<'_, system::DbState>, api_key: String, model_id: String, base_url: String) -> Result<(), String> {
    system::save_settings(system::Settings { api_key, model_id, base_url })
}

#[tauri::command]
fn get_history(state: State<'_, system::DbState>) -> Result<Vec<system::HistoryRecord>, String> {
    let conn = state.conn.lock().map_err(|e| e.to_string())?;
    system::get_history(&conn)
}

#[tauri::command]
fn open_file(path: String) -> Result<(), String> {
    tracing::info!("Opening file: {}", path);
    if let Err(e) = validate_path_in_outputs(&path) {
        tracing::error!("Path validation failed for {}: {}", path, e);
        return Err(e);
    }
    tauri_plugin_opener::open_path(path.clone(), None::<String>).map_err(|e| {
        tracing::error!("Failed to open file {}: {}", path, e);
        e.to_string()
    })
}

fn main() {
    // Ensure the Tawreed environment is initialized first so the logs directory exists
    let log_dir = match system::init_tawreed_env() {
        Ok(path) => {
            let p = path.join("logs");
            std::fs::create_dir_all(&p).ok();
            p
        },
        Err(e) => {
            // tracing init happens later, so we just fallback
            std::path::PathBuf::from(".")
        }
    };

    let file_appender = tracing_appender::rolling::never(&log_dir, "app.log");
    let (non_blocking, _guard) = tracing_appender::non_blocking(file_appender);

    let file_layer = tracing_subscriber::fmt::layer()
        .with_writer(non_blocking)
        .with_ansi(false);

    let stdout_layer = tracing_subscriber::fmt::layer()
        .with_writer(std::io::stdout);

    tracing_subscriber::registry()
        .with(file_layer)
        .with(stdout_layer)
        .init();

    tracing::info!("Tawreed environment initialized at {:?}", log_dir.parent().unwrap_or(&log_dir));

    let db_path = system::get_db_path().expect("Failed to get DB path");
    let conn = rusqlite::Connection::open(&db_path).expect("Failed to open db");
    conn.pragma_update(None, "journal_mode", "WAL").expect("Failed to enable WAL mode");

    tauri::Builder::default()
        .plugin(tauri_plugin_updater::Builder::new().build())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_opener::init())
        .manage(system::DbState { conn: std::sync::Mutex::new(conn) })
        .invoke_handler(tauri::generate_handler![process_boq, get_settings, save_settings, get_history, open_file])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
