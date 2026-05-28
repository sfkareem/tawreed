#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_shell::init())
        .invoke_handler(tauri::generate_handler![
            tawreed::commands::load_settings,
            tawreed::commands::save_settings,
            tawreed::commands::select_file,
            tawreed::commands::extract_takeoff,
            tawreed::commands::save_takeoff_excel,
            tawreed::commands::open_file
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
