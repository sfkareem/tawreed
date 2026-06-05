// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod processor;

#[tauri::command]
async fn process_boq(file_path: String, base_url: String, model: String, api_key: String) -> Result<String, String> {
    processor::slice_boq(&file_path, &base_url, &model, &api_key).await
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![process_boq])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
