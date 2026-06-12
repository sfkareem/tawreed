# Tawreed Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Clean up all hardcoded credentials, migrate configuration from SQLite to a JSON file, implement shared database connection state in Tauri, fix dynamic multi-sheet mappings, rename slicing terminology to "Work Package Extraction", and deploy to GitHub.

**Architecture:** Refactor `system.rs` to read/write `~/.tawreed/config.json` and host a Mutex-wrapped rusqlite connection in Tauri State. Modify `main.rs` to initialize and manage this state. Refactor `processor.rs` to resolve columns per sheet row dynamically. Clean up credential variables in scripts, and initialize/push the project to GitHub.

**Tech Stack:** Rust, Tauri v2, rusqlite, Next.js 16, TypeScript, Tailwind CSS, GitHub CLI (`gh` CLI)

---

### Task 1: Environment & Settings Refactoring

**Files:**
- Modify: `src-tauri/src/system.rs`

- [ ] **Step 1: Update settings structs, paths, and drops**
  Remove the SQLite `settings` table from database initialization and add config file helpers:
  ```rust
  pub struct DbState {
      pub conn: std::sync::Mutex<rusqlite::Connection>,
  }

  pub fn get_config_path() -> Result<PathBuf, String> {
      let user_dirs = UserDirs::new().ok_or("Could not find user home directory")?;
      Ok(user_dirs.home_dir().join(".tawreed").join("config.json"))
  }
  ```

- [ ] **Step 2: Rewrite get_settings and save_settings**
  Read and write directly to `~/.tawreed/config.json`:
  ```rust
  pub fn get_settings() -> Result<Settings, String> {
      let path = get_config_path()?;
      if path.exists() {
          let content = fs::read_to_string(&path).map_err(|e| e.to_string())?;
          serde_json::from_str(&content).map_err(|e| e.to_string())
      } else {
          let default_settings = Settings {
              api_key: "".to_string(),
              model_id: "MiniMax-M3".to_string(),
              base_url: "https://api.minimax.io/v1".to_string(),
          };
          let _ = save_settings(default_settings.clone());
          Ok(default_settings)
      }
  }

  pub fn save_settings(settings: Settings) -> Result<(), String> {
      let path = get_config_path()?;
      let content = serde_json::to_string_pretty(&settings).map_err(|e| e.to_string())?;
      fs::write(&path, content).map_err(|e| e.to_string())?;
      Ok(())
  }
  ```

- [ ] **Step 3: Refactor history database queries to use managed connection**
  Update signatures to read from locked connections:
  ```rust
  pub fn get_history(state: tauri::State<'_, DbState>) -> Result<Vec<HistoryRecord>, String> {
      let conn = state.conn.lock().map_err(|e| e.to_string())?;
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
      
      let mut history = Vec::new();
      for row in rows {
          if let Ok(record) = row {
              history.push(record);
          }
      }
      Ok(history)
  }

  pub fn add_history(conn: &rusqlite::Connection, project_name: &str, packages_count: i64, output_path: &str) -> Result<(), String> {
      let timestamp = chrono::Local::now().format("%Y-%m-%d %H:%M:%S").to_string();
      conn.execute(
          "INSERT INTO history (timestamp, project_name, packages_count, output_path) VALUES (?1, ?2, ?3, ?4)",
          [&timestamp, project_name, &packages_count.to_string(), output_path],
      ).map_err(|e| e.to_string())?;
      Ok(())
  }
  ```

---

### Task 2: Entrypoint & State Initialization

**Files:**
- Modify: `src-tauri/src/main.rs`

- [ ] **Step 1: Register DbState and rewrite commands**
  Modify `main()` to configure WAL mode and manage the state, and rewrite invoke commands:
  ```rust
  #[tauri::command]
  async fn process_boq(
      app: tauri::AppHandle,
      state: tauri::State<'_, system::DbState>,
      file_path: String,
      base_url: String,
      model: String,
      api_key: String,
  ) -> Result<String, String> {
      let (result, packages_count) = processor::extract_work_packages(app, &file_path, &base_url, &model, &api_key).await?;
      let project_name = file_path.split('\\').last().unwrap_or(&file_path).split('/').last().unwrap_or(&file_path).to_string();
      let conn = state.conn.lock().map_err(|e| e.to_string())?;
      let _ = system::add_history(&conn, &project_name, packages_count, &result);
      Ok(result)
  }

  #[tauri::command]
  fn get_settings() -> Result<system::Settings, String> {
      system::get_settings()
  }

  #[tauri::command]
  fn save_settings(api_key: String, model_id: String, base_url: String) -> Result<(), String> {
      system::save_settings(system::Settings { api_key, model_id, base_url })
  }

  #[tauri::command]
  fn get_history(state: tauri::State<'_, system::DbState>) -> Result<Vec<system::HistoryRecord>, String> {
      system::get_history(state)
  }

  fn main() {
      let tawreed_dir = match system::init_tawreed_env() {
          Ok(path) => {
              println!("Tawreed environment initialized at {:?}", path);
              path
          }
          Err(e) => {
              eprintln!("Failed to initialize Tawreed env: {}", e);
              std::process::exit(1);
          }
      };

      let db_path = tawreed_dir.join("db").join("tawreed.db");
      let conn = rusqlite::Connection::open(&db_path).expect("failed to open database");
      let _ = conn.execute("PRAGMA journal_mode=WAL", []);

      tauri::Builder::default()
          .manage(system::DbState { conn: std::sync::Mutex::new(conn) })
          .plugin(tauri_plugin_dialog::init())
          .plugin(tauri_plugin_opener::init())
          .invoke_handler(tauri::generate_handler![process_boq, get_settings, save_settings, get_history])
          .run(tauri::generate_context!())
          .expect("error while running tauri application");
  }
  ```

---

### Task 3: Package Processing Engine Dynamic Mapping

**Files:**
- Modify: `src-tauri/src/processor.rs`

- [ ] **Step 1: Rename slice_boq and update progress logs**
  Rename to `extract_work_packages`, clean up "BOQ Slicer" references to "Tawreed Work Package Extractor" in cover sheet and log strings, and return `Result<(String, i64), String>`.

- [ ] **Step 2: Move columns resolution inside row loop**
  Extract columns dynamically per sheet:
  ```rust
          let mut current_row: u32 = 1;
          for (sheet_name, row) in rows.iter() {
              let mut num_col: Option<u16> = None;
              let mut desc_col: Option<u16> = None;
              let mut unit_col: Option<u16> = None;
              let mut qty_col: Option<u16> = None;
              let mut rate_col: Option<u16> = None;

              if let Some(source_headers) = headers_map.get(sheet_name) {
                  for (col, val) in source_headers.iter().enumerate() {
                      let c = col as u16;
                      let lower = val.to_lowercase();
                      let is_num = lower.contains("رقم") || lower.contains("no") || lower.contains("item") || lower.contains("مسلسل");
                      let is_desc = lower.contains("بيان") || lower.contains("وصف") || lower.contains("desc") || (lower.contains("بند") && !lower.contains("رقم"));
                      let is_unit = lower.contains("وحدة") || lower.contains("وحده") || lower.contains("unit");
                      let is_qty = lower.contains("كمية") || lower.contains("كميه") || lower.contains("qty") || lower.contains("quantity");
                      let is_rate = lower.contains("سعر") || lower.contains("فئة") || lower.contains("فئه") || lower.contains("rate") || lower.contains("price");

                      if is_num { if num_col.is_none() { num_col = Some(c); } }
                      else if is_desc { if desc_col.is_none() { desc_col = Some(c); } }
                      else if is_unit { if unit_col.is_none() { unit_col = Some(c); } }
                      else if is_qty { if qty_col.is_none() { qty_col = Some(c); } }
                      else if is_rate { if rate_col.is_none() { rate_col = Some(c); } }
                  }
              }
              // ... proceed to call write_data! macro using current offsets ...
  ```

---

### Task 4: UI Terminology Audit

**Files:**
- Modify: `src/app/page.tsx`

- [ ] **Step 1: Replace Slicer terminology**
  Replace "BOQ Slicing" with "Work Package Extractor" or "breaking BOQs into work packages".
  Update the History screen component to render `record.packages_count` dynamically:
  ```tsx
  <p className="font-medium text-emerald-400 text-xs sm:text-sm">{record.packages_count} Packages</p>
  ```

---

### Task 5: Credentials Cleanup and Git ignore Config

**Files:**
- Modify: `src-tauri/build_test.cjs`
- Modify: `.gitignore`
- Delete: `src-tauri/src/bin/test_boq.rs`

- [ ] **Step 1: Delete hardcoded credentials from build_test.cjs**
  Replace key with:
  ```javascript
  let key = process.env.TAWREED_API_KEY || "";
  ```

- [ ] **Step 2: Exclude autogenerated test runner and targets**
  Add rules to root `.gitignore` to prevent secret/leak leaks:
  ```
  .next
  dist
  node_modules
  .venv
  src-tauri/src/bin/test_boq.rs
  src-tauri/target/
  .env
  *.local
  ```

- [ ] **Step 3: Remove test_boq.rs from git tracking**
  Command: `git rm --cached src-tauri/src/bin/test_boq.rs`

---

### Task 6: GitHub Deployment

**Files:**
- Command Line

- [ ] **Step 1: Build check**
  Run: `cd src-tauri && cargo check`

- [ ] **Step 2: Commit local changes**
  Run: `git commit -a -m "refactor: drop database settings, configure WAL state, fix dynamic column extraction, clean credentials"`

- [ ] **Step 3: Create repository and push**
  Run: `gh repo create tawreed --public --source=. --remote=origin --push`
