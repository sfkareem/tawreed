# Centralized Output Directory & File Opening UX Spec

- **Date**: 2026-06-06
- **Status**: Approved
- **Topic**: Centralizing generated work packages inside the `~/.tawreed` home subdirectory and adding UI controls to open/reveal files.

---

## 1. Context & Overview
Currently, the generated Excel work packages are saved in the same directory as the source BOQ input file. The user has requested to store all generated work packages in `~/.tawreed` (specifically a dedicated subfolder `~/.tawreed/outputs`). Since this hidden home folder is not easily accessible via file explorers for non-technical users, we must implement a direct file opening UX in the Tauri frontend.

---

## 2. Component Design & Changes

### A. Centralized Output Directory (`~/.tawreed/outputs`)
- **Initialization**: Update `system::init_tawreed_env()` in `system.rs` to ensure `~/.tawreed/outputs` is created on startup along with the `db`, `logs`, and `data` folders.
- **Helper Function**: Implement `system::get_outputs_dir() -> Result<PathBuf, String>` to construct the dynamic output path safely using `UserDirs`.
- **Workbook Extraction**: Update the workbook saving logic in `processor::extract_work_packages` to save outputs in the centralized output directory instead of the input BOQ's directory.

### B. Tauri Open File Command
- **Command Implementation**: Add a Tauri command `open_file` to `main.rs` that accepts the full absolute path of the generated Excel workbook and uses `tauri_plugin_opener` to open it in the default system viewer:
  ```rust
  #[tauri::command]
  fn open_file(path: String) -> Result<(), String> {
      tauri_plugin_opener::open_path(path, None::<String>).map_err(|e| e.to_string())
  }
  ```
- **Registration**: Expose the command inside the `tauri::generate_handler![...]` in `main.rs`.

### C. Frontend UX Controls
- **Success Notification**: Once a BOQ extraction completes successfully, display a button or interactive banner with the text "Open Work Packages File" which triggers the `open_file` command.
- **History list**: In the run history screen, replace the static text showing the output path with a clickable open button or folder/external link icon next to each past extraction record. When clicked, it calls `open_file` with the record's output path.
- **Error Handling**: Gracefully handle cases where the file was deleted or cannot be opened by showing a subtle toast or error state.
