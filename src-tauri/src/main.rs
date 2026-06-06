// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod processor;
mod system;

use tauri::State;

#[tauri::command]
async fn process_boq(
    app: tauri::AppHandle,
    state: State<'_, system::DbState>,
    file_path: String,
    base_url: String,
    model: String,
    api_key: String,
) -> Result<String, String> {
    let (result_path, count) = processor::extract_work_packages(app, &file_path, &base_url, &model, &api_key).await?;
    // Add to history
    let project_name = file_path.split('\\').last().unwrap_or(&file_path).split('/').last().unwrap_or(&file_path).to_string();
    let conn = state.conn.lock().map_err(|e| e.to_string())?;
    let _ = system::add_history(&conn, &project_name, count, &result_path);
    Ok(result_path)
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

fn main() {
    match system::init_tawreed_env() {
        Ok(path) => println!("Tawreed environment initialized at {:?}", path),
        Err(e) => eprintln!("Failed to initialize Tawreed env: {}", e),
    }

    let db_path = system::get_db_path().expect("Failed to get DB path");
    let conn = rusqlite::Connection::open(&db_path).expect("Failed to open db");
    conn.pragma_update(None, "journal_mode", "WAL").expect("Failed to enable WAL mode");

    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_opener::init())
        .manage(system::DbState { conn: std::sync::Mutex::new(conn) })
        .invoke_handler(tauri::generate_handler![process_boq, get_settings, save_settings, get_history])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
