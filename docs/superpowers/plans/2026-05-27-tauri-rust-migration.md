# Tauri + Rust Migration & Codebase Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate the Tawreed backend from Python (`pywebview`) to a highly optimized Tauri v2 + Rust desktop application, followed by a complete cleanup of all legacy Python code and assets.

**Architecture:** We will scaffold the `src-tauri` directory, implement Rust-native commands for settings, window management, and native file pickers, design a oneshot-channel-based asynchronous checkpoint suspension registry, integrate the `genai` crate for LLM communication, write `calamine` and `rust_xlsxwriter` Excel engines, implement `typst` PDF compiles, add mammoth.js for DOCX parsing in the webview, and refactor `gui/app.js` to invoke Tauri commands directly.

**Tech Stack:** Tauri v2, Rust (Tokio, Calamine, rust_xlsxwriter, genai, pdfium-render, typst), JavaScript (ES6, Mammoth.js).

---

## File Structure Map
* **Create:** `src-tauri/Cargo.toml` (Cargo dependencies and workspace config)
* **Create:** `src-tauri/tauri.conf.json` (Tauri v2 configuration)
* **Create:** `src-tauri/src/main.rs` (App initialization, setup, and runner)
* **Create:** `src-tauri/src/config.rs` (Directories-next configuration loader/saver)
* **Create:** `src-tauri/src/job_manager.rs` (Job state engine with tokio channels)
* **Create:** `src-tauri/src/commands.rs` (Tauri command bridge)
* **Create:** `src-tauri/src/parsers.rs` (Calamine, PDFium, and text ingestion)
* **Create:** `src-tauri/src/exporter.rs` (rust_xlsxwriter and Typst builders)
* **Create:** `gui/mammoth.browser.min.js` (Mammoth.js DOCX-to-HTML parser)
* **Modify:** `gui/index.html` (Include Mammoth.js script)
* **Modify:** `gui/app.js` (Refactor PyWebView calls to Tauri native core invoke/event listeners)
* **Delete:** `main.py`, `tawreed_backend.py`, `requirements.txt`, `main.spec`, `generate_sample_boq.py`, `.venv/`, `build/`, `dist/`

---

## Tasks Checklist

### Task 1: Scaffolding and Configurations

**Files:**
* Create: `src-tauri/tauri.conf.json`
* Create: `src-tauri/Cargo.toml`
* Create: `src-tauri/capabilities/default.json`

- [ ] **Step 1: Scaffold Tauri v2 metadata and configurations**
    Create the configuration file `src-tauri/tauri.conf.json` to define the frameless window layout and plugins:
    ```json
    {
      "productName": "tawreed",
      "version": "0.1.0",
      "identifier": "com.tawreed.app",
      "build": {
        "beforeDevCommand": "",
        "beforeBuildCommand": "",
        "devUrl": "../gui",
        "frontendDist": "../gui"
      },
      "app": {
        "windows": [
          {
            "title": "Tawreed - Construction Materials Extractor",
            "width": 1100,
            "height": 750,
            "minWidth": 900,
            "minHeight": 600,
            "decorations": false,
            "resizable": true,
            "visible": true
          }
        ],
        "security": {
          "csp": null
        }
      },
      "bundle": {
        "active": true,
        "targets": "all",
        "icon": [
          "icons/32x32.png",
          "icons/128x128.png",
          "icons/icon.ico"
        ]
      }
    }
    ```

- [ ] **Step 2: Declare Cargo dependencies**
    Create `src-tauri/Cargo.toml` containing all dependencies required for the rewrite:
    ```toml
    [package]
    name = "tawreed"
    version = "0.1.0"
    edition = "2021"

    [dependencies]
    tauri = { version = "2.0.0", features = [] }
    tauri-plugin-dialog = "2.0.0"
    tauri-plugin-shell = "2.0.0"
    tokio = { version = "1.0", features = ["full"] }
    serde = { version = "1.0", features = ["derive"] }
    serde_json = "1.0"
    genai = "0.1.0"
    calamine = "0.24"
    rust_xlsxwriter = "0.64"
    pdfium-render = "0.8"
    typst = "0.11"
    directories-next = "2.0"
    uuid = { version = "1.0", features = ["v4", "serde"] }
    tempfile = "3.8"
    base64 = "0.21"
    ```

- [ ] **Step 3: Define Tauri capabilities**
    Create `src-tauri/capabilities/default.json` to configure security permissions for dialogs and shells:
    ```json
    {
      "$schema": "../node_modules/@tauri-apps/cli/schema-capability.json",
      "identifier": "default",
      "description": "Default capability permissions",
      "windows": ["main"],
      "permissions": [
        "core:default",
        "dialog:allow-open",
        "dialog:allow-save",
        "shell:allow-open"
      ]
    }
    ```

- [ ] **Step 4: Commit Scaffolding**
    ```bash
    git add src-tauri/tauri.conf.json src-tauri/Cargo.toml src-tauri/capabilities/default.json
    git commit -m "chore: scaffold tauri v2 configuration files"
    ```

---

### Task 2: Rust App Configuration & Directories

**Files:**
* Create: `src-tauri/src/config.rs`

- [ ] **Step 1: Create Config Structs and Loader**
    Write the implementation in `src-tauri/src/config.rs` to handle system path resolution using `directories-next` and atomic saves:
    ```rust
    use serde::{Serialize, Deserialize};
    use directories_next::ProjectDirs;
    use std::fs::{self, File};
    use std::io::{self, Write};
    use std::path::PathBuf;

    #[derive(Serialize, Deserialize, Debug, Clone)]
    pub struct AppSettings {
        pub api_provider: String,
        pub base_url: String,
        pub api_key: String,
        pub model_name: String,
        pub preferred_language: String,
        pub max_file_size_mb: u64,
        pub max_content_length_chars: usize,
        pub api_timeout_seconds: u64,
        pub theme: String,
        pub qa_max_iterations: usize,
        #[serde(default = "default_first_run")]
        pub first_run: bool,
    }

    fn default_first_run() -> bool { true }

    impl Default for AppSettings {
        fn default() -> Self {
            Self {
                api_provider: "gemini".to_string(),
                base_url: "https://generativelanguage.googleapis.com".to_string(),
                api_key: "".to_string(),
                model_name: "gemini-2.0-flash".to_string(),
                preferred_language: "bilingual".to_string(),
                max_file_size_mb: 15,
                max_content_length_chars: 80000,
                api_timeout_seconds: 900,
                theme: "system".to_string(),
                qa_max_iterations: 3,
                first_run: true,
            }
        }
    }

    pub struct ConfigManager {
        proj_dirs: ProjectDirs,
    }

    impl ConfigManager {
        pub fn new() -> Result<Self, String> {
            let dirs = ProjectDirs::from("com", "tawreed", "tawreed")
                .ok_or("Could not locate system directories".to_string())?;
            Ok(Self { proj_dirs: dirs })
        }

        pub fn config_dir(&self) -> PathBuf {
            self.proj_dirs.config_dir().to_path_buf()
        }

        pub fn logs_dir(&self) -> PathBuf {
            self.config_dir().join("logs")
        }

        pub fn config_file(&self) -> PathBuf {
            self.config_dir().join("config.json")
        }

        pub fn load_settings(&self) -> io::Result<AppSettings> {
            let config_path = self.config_file();
            if !config_path.exists() {
                let default_settings = AppSettings::default();
                self.save_settings(&default_settings)?;
                return Ok(default_settings);
            }
            let file = File::open(&config_path)?;
            let reader = io::BufReader::new(file);
            let settings: AppSettings = serde_json::from_reader(reader)
                .map_err(|e| io::Error::new(io::ErrorKind::InvalidData, e))?;
            Ok(settings)
        }

        pub fn save_settings(&self, settings: &AppSettings) -> io::Result<()> {
            let config_dir = self.config_dir();
            fs::create_dir_all(&config_dir)?;
            let mut temp = tempfile::NamedTempFile::new_in(&config_dir)?;
            let bytes = serde_json::to_vec_pretty(settings)
                .map_err(|e| io::Error::new(io::ErrorKind::InvalidData, e))?;
            temp.write_all(&bytes)?;
            temp.flush()?;
            temp.persist(&self.config_file())
                .map_err(|e| io::Error::new(io::ErrorKind::Other, e.to_string()))?;
            Ok(())
        }
    }
    ```

- [ ] **Step 2: Commit Config Module**
    ```bash
    git add src-tauri/src/config.rs
    git commit -m "feat: implement config loading and saving using directories-next"
    ```

---

### Task 3: Shared Job Registry & Checkpoints

**Files:**
* Create: `src-tauri/src/job_manager.rs`

- [ ] **Step 1: Write Job Sessions Registry**
    Create `src-tauri/src/job_manager.rs` using `tokio::sync::oneshot` and shared arc mutex map to enable non-blocking checkpoints:
    ```rust
    use std::collections::HashMap;
    use std::sync::Arc;
    use tokio::sync::{oneshot, Mutex};
    use uuid::Uuid;
    use serde::{Serialize, Deserialize};
    use std::sync::atomic::AtomicBool;

    #[derive(Serialize, Deserialize, Clone, Debug)]
    pub enum CheckpointResolution {
        ApprovedPackages(Vec<String>),
        ResolvedWarnings(HashMap<String, String>),
        Aborted,
    }

    pub struct JobSession {
        pub resume_tx: Option<oneshot::Sender<CheckpointResolution>>,
        pub aborted: Arc<AtomicBool>,
    }

    #[derive(Default)]
    pub struct JobManager {
        pub active_jobs: Arc<Mutex<HashMap<Uuid, JobSession>>>,
    }

    impl JobManager {
        pub async fn register_job(&self, job_id: Uuid, aborted: Arc<AtomicBool>) {
            let mut jobs = self.active_jobs.lock().await;
            jobs.insert(job_id, JobSession {
                resume_tx: None,
                aborted,
            });
        }

        pub async fn register_checkpoint(&self, job_id: Uuid, tx: oneshot::Sender<CheckpointResolution>) -> Result<(), &'static str> {
            let mut jobs = self.active_jobs.lock().await;
            if let Some(session) = jobs.get_mut(&job_id) {
                session.resume_tx = Some(tx);
                Ok(())
            } else {
                Err("Job session not found")
            }
        }

        pub async fn resume_checkpoint(&self, job_id: Uuid, resolution: CheckpointResolution) -> Result<(), &'static str> {
            let mut jobs = self.active_jobs.lock().await;
            if let Some(session) = jobs.get_mut(&job_id) {
                if let Some(tx) = session.resume_tx.take() {
                    let _ = tx.send(resolution);
                    Ok(())
                } else {
                    Err("No active checkpoint for this job")
                }
            } else {
                Err("Job session not found")
            }
        }

        pub async fn remove_job(&self, job_id: Uuid) {
            let mut jobs = self.active_jobs.lock().await;
            jobs.remove(&job_id);
        }
    }
    ```

- [ ] **Step 2: Commit Job Manager**
    ```bash
    git add src-tauri/src/job_manager.rs
    git commit -m "feat: implement tokio oneshot checkpoint suspension registry"
    ```

---

### Task 4: Unified AI Service (LLM Client)

**Files:**
* Create: `src-tauri/src/ai_service.rs`

- [ ] **Step 1: Write unified client using genai crate**
    Create `src-tauri/src/ai_service.rs`. This implements a client using `genai::Client` to handle chat and structured requests:
    ```rust
    use genai::chat::{ChatRequest, ChatResponse, Message};
    use genai::Client;
    use crate::config::AppSettings;

    pub struct AIService;

    impl AIService {
        pub async fn call_ai(settings: &AppSettings, prompt: &str) -> Result<String, String> {
            // Map settings model names to genai model names
            let client = Client::new();
            
            // Build chat query
            let chat_req = ChatRequest::new(vec![
                Message::user(prompt)
            ]);

            // Execute using the unified SDK provider selection
            let model = &settings.model_name;
            let response = client.exec(model, chat_req, None).await
                .map_err(|e| format!("AI API call failed: {}", e))?;

            Ok(response.content.unwrap_or_default())
        }
    }
    ```

- [ ] **Step 2: Commit AI Service**
    ```bash
    git add src-tauri/src/ai_service.rs
    git commit -m "feat: integrate genai unified LLM communication engine"
    ```

---

### Task 5: Document Parsers (Calamine, PDFium)

**Files:**
* Create: `src-tauri/src/parsers.rs`

- [ ] **Step 1: Implement Calamine Excel Forward-Fill and PDFium Render**
    Create `src-tauri/src/parsers.rs` to extract spreadsheet values and convert PDF pages into vision-ready JPEGs:
    ```rust
    use calamine::{Reader, Xlsx, open_workbook, DataType};
    use pdfium_render::prelude::*;
    use std::path::Path;

    pub struct DocumentParser;

    impl DocumentParser {
        pub fn parse_excel(path: &str) -> Result<Vec<Vec<String>>, String> {
            let mut workbook: Xlsx<_> = open_workbook(path)
                .map_err(|e| format!("Failed to open Excel: {}", e))?;
            
            let sheet_name = workbook.sheet_names().get(0)
                .ok_or("No sheets found in workbook")?.clone();
            
            let mut rows = Vec::new();
            if let Some(Ok(range)) = workbook.worksheet_range(&sheet_name) {
                let mut last_category = String::new();
                for r in range.rows() {
                    let mut row_values = Vec::new();
                    for (i, cell) in r.iter().enumerate() {
                        let mut val = match cell {
                            DataType::String(s) => s.clone(),
                            DataType::Float(f) => f.to_string(),
                            DataType::Int(i) => i.to_string(),
                            _ => "".to_string(),
                        };
                        
                        // Excel Forward-Fill category resolving
                        if i == 0 {
                            if val.is_empty() {
                                val = last_category.clone();
                            } else {
                                last_category = val.clone();
                            }
                        }
                        row_values.push(val);
                    }
                    rows.push(row_values);
                }
            }
            Ok(rows)
        }

        pub fn render_pdf_page_to_jpeg(pdf_path: &str, page_idx: u32, output_jpeg_path: &str) -> Result<(), String> {
            let pdfium = Pdfium::default();
            let document = pdfium.load_pdf_from_file(pdf_path, None)
                .map_err(|e| format!("Failed to load PDF: {:?}", e))?;
            
            let page = document.pages().get(page_idx)
                .map_err(|e| format!("Failed to get page: {:?}", e))?;
            
            let bitmap = page.render(300, 300, None)
                .map_err(|e| format!("Failed to render page: {:?}", e))?;
            
            bitmap.as_image().write_to_file(Path::new(output_jpeg_path))
                .map_err(|e| format!("Failed to save JPEG: {}", e))?;
            
            Ok(())
        }
    }
    ```

- [ ] **Step 2: Commit Parsers**
    ```bash
    git add src-tauri/src/parsers.rs
    git commit -m "feat: implement calamine excel reader and pdfium page rendering"
    ```

---

### Task 6: Exporters (rust_xlsxwriter, Typst)

**Files:**
* Create: `src-tauri/src/exporter.rs`

- [ ] **Step 1: Write Excel Exporter using rust_xlsxwriter**
    Create `src-tauri/src/exporter.rs` to generate styled workbooks and compile native Typst PDF documents:
    ```rust
    use rust_xlsxwriter::{Workbook, Worksheet, Format, Color, FormatBorder, FormatAlign, FormatPatterns, XlsxError};
    use std::process::Command;

    pub struct Exporter;

    impl Exporter {
        pub fn generate_takeoff_excel(output_path: &str, lang: &str) -> Result<(), XlsxError> {
            let mut workbook = Workbook::new();
            let worksheet = workbook.add_worksheet()?;
            
            // Layout direction
            if lang == "arabic" {
                worksheet.set_right_to_left(true);
            }
            worksheet.set_screen_gridlines(true);

            // Styling Header Format
            let header_format = Format::new()
                .set_font_name("Segoe UI")
                .set_font_size(11)
                .set_bold()
                .set_font_color(Color::RGB(0xFFFFFF))
                .set_background_color(Color::RGB(0xD35400))
                .set_pattern(FormatPatterns::Solid)
                .set_border(FormatBorder::Thin)
                .set_border_color(Color::RGB(0xD5D8DC))
                .set_align(FormatAlign::Center);

            worksheet.write_string_with_format(0, 0, "Package / Material", &header_format)?;
            worksheet.write_string_with_format(0, 1, "Specification", &header_format)?;
            worksheet.write_string_with_format(0, 2, "Qty", &header_format)?;
            worksheet.write_string_with_format(0, 3, "Unit", &header_format)?;

            workbook.save(output_path)?;
            Ok(())
        }

        pub fn generate_typst_pdf(typst_code: &str, output_pdf_path: &str) -> Result<(), String> {
            // Save Typst content to temporary file
            let temp_typst = std::env::temp_dir().join("tawreed_report.typ");
            std::fs::write(&temp_typst, typst_code)
                .map_err(|e| format!("Failed to write temp typst file: {}", e))?;

            // Compile using typst CLI or crate bindings
            let output = Command::new("typst")
                .arg("compile")
                .arg(&temp_typst)
                .arg(output_pdf_path)
                .output()
                .map_err(|e| format!("Failed to execute Typst: {}", e))?;

            if !output.status.success() {
                return Err(String::from_utf8_lossy(&output.stderr).to_string());
            }

            Ok(())
        }
    }
    ```

- [ ] **Step 2: Commit Exporter Module**
    ```bash
    git add src-tauri/src/exporter.rs
    git commit -m "feat: implement rust_xlsxwriter excel output and typst pdf builder"
    ```

---

### Task 7: Command Bridge & Refactoring `app.js`

**Files:**
* Create: `src-tauri/src/commands.rs`
* Create: `src-tauri/src/main.rs`
* Create: `gui/mammoth.browser.min.js`
* Modify: `gui/index.html`
* Modify: `gui/app.js`

- [ ] **Step 1: Implement Tauri Command Bridge**
    Create `src-tauri/src/commands.rs` containing all invocable APIs:
    ```rust
    use tauri::{State, Window, AppHandle};
    use crate::config::{ConfigManager, AppSettings};
    use crate::job_manager::{JobManager, CheckpointResolution};
    use std::collections::HashMap;

    #[tauri::command]
    pub fn load_settings(config_mgr: State<'_, ConfigManager>) -> Result<AppSettings, String> {
        config_mgr.load_settings().map_err(|e| e.to_string())
    }

    #[tauri::command]
    pub fn save_settings(settings: AppSettings, config_mgr: State<'_, ConfigManager>) -> Result<bool, String> {
        config_mgr.save_settings(&settings).map_err(|e| e.to_string())?;
        Ok(true)
    }

    #[tauri::command]
    pub async fn submit_approved_packages(
        job_id: String,
        packages: Vec<String>,
        job_mgr: State<'_, JobManager>,
    ) -> Result<bool, String> {
        let uuid = uuid::Uuid::parse_str(&job_id).map_err(|e| e.to_string())?;
        job_mgr.resume_checkpoint(uuid, CheckpointResolution::ApprovedPackages(packages)).await?;
        Ok(true)
    }

    #[tauri::command]
    pub async fn submit_warning_resolutions(
        job_id: String,
        resolutions: HashMap<String, String>,
        job_mgr: State<'_, JobManager>,
    ) -> Result<bool, String> {
        let uuid = uuid::Uuid::parse_str(&job_id).map_err(|e| e.to_string())?;
        job_mgr.resume_checkpoint(uuid, CheckpointResolution::ResolvedWarnings(resolutions)).await?;
        Ok(true)
    }

    #[tauri::command]
    pub async fn abort_job(job_id: String, job_mgr: State<'_, JobManager>) -> Result<bool, String> {
        let uuid = uuid::Uuid::parse_str(&job_id).map_err(|e| e.to_string())?;
        job_mgr.resume_checkpoint(uuid, CheckpointResolution::Aborted).await?;
        Ok(true)
    }
    ```

- [ ] **Step 2: Bind setup lifecycle and command handlers in main.rs**
    Create `src-tauri/src/main.rs`:
    ```rust
    #![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

    mod config;
    mod job_manager;
    mod ai_service;
    mod parsers;
    mod exporter;
    mod commands;

    use config::ConfigManager;
    use job_manager::JobManager;

    fn main() {
        let config_mgr = ConfigManager::new().expect("Failed to initialize config manager");
        
        tauri::Builder::default()
            .manage(config_mgr)
            .manage(JobManager::default())
            .invoke_handler(tauri::generate_handler![
                commands::load_settings,
                commands::save_settings,
                commands::submit_approved_packages,
                commands::submit_warning_resolutions,
                commands::abort_job
            ])
            .run(tauri::generate_context!())
            .expect("error while running tauri application");
    }
    ```

- [ ] **Step 3: Setup Mammoth.js DOCX-to-HTML parser**
    Download the minified Mammoth.js browser bundle to `gui/mammoth.browser.min.js` and link it inside `gui/index.html`:
    ```html
    <script src="mammoth.browser.min.js"></script>
    ```

- [ ] **Step 4: Refactor app.js to Tauri Core invoke API**
    Modify `gui/app.js` to strip `pywebview.api` calls and transition entirely to Tauri invoke and event listeners:
    ```javascript
    const { invoke } = window.__TAURI__.core;
    const { listen } = window.__TAURI__.event;

    // Load Settings
    async function loadConfig() {
        try {
            appSettings = await invoke("load_settings");
            // ... bind settings UI values ...
        } catch (err) {
            console.error("Failed to load settings", err);
        }
    }

    // Save Settings
    async function saveConfig(settings) {
        await invoke("save_settings", { settings });
    }

    // Submitting Checkpoints
    async function submitApprovedPackages(jobId, packages) {
        await invoke("submit_approved_packages", { jobId, packages });
    }

    async function submitWarningResolutions(jobId, resolutions) {
        await invoke("submit_warning_resolutions", { jobId, resolutions });
    }

    async function abortJob(jobId) {
        await invoke("abort_job", { jobId });
    }

    // Event Listener setup
    listen("agent-update", (event) => {
        receiveAgentUpdate(event.payload);
    });
    ```

- [ ] **Step 5: Commit Tauri Bridge Refactoring**
    ```bash
    git add src-tauri/src/commands.rs src-tauri/src/main.rs gui/index.html gui/app.js
    git commit -m "feat: rewire frontend bridge, linking core invoke and mammoth.js"
    ```

---

### Task 8: Codebase Cleanup

**Files:**
* Delete: `main.py`
* Delete: `tawreed_backend.py`
* Delete: `requirements.txt`
* Delete: `main.spec`
* Delete: `generate_sample_boq.py`

- [ ] **Step 1: Destroy legacy Python files**
    Run:
    ```powershell
    Remove-Item main.py, tawreed_backend.py, requirements.txt, main.spec, generate_sample_boq.py -Force
    Remove-Item .venv, build, dist -Recurse -Force -ErrorAction SilentlyContinue
    ```

- [ ] **Step 2: Commit Cleanup**
    ```bash
    git add .
    git commit -m "chore: remove all legacy Python backend scripts and packaging configurations"
    ```

---

## Execution Handoff Choice

Plan complete and saved to [2026-05-27-tauri-rust-migration.md](file:///c:/Users/karee/Desktop/QS%20Mind/tawreed/docs/superpowers/plans/2026-05-27-tauri-rust-migration.md). Two execution options:

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration.

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints.

Which approach?
