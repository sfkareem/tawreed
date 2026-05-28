# Tawreed Scratch Rebuild Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the Tawreed desktop app from scratch as a lightweight, fully automated Tauri v2 + Rust application focusing on foundational document ingestion, AI-powered extraction, and structured Excel export.

**Architecture:** We will set up standard Tauri v2 configuration structures, implement home-directory settings persistence, implement calamine and pdfium/zip-based document parsing utilities, build reqwest-based direct Gemini/OpenAI vision REST integrations, and develop a rust_xlsxwriter styled takeoff sheet generator.

**Tech Stack:** Tauri v2, Rust (Tokio, reqwest, Calamine, rust_xlsxwriter, pdf-extract, pdfium-render, zip, serde), HTML5/Vanilla CSS/Javascript (ES6).

---

### Task 1: Scaffolding & Tauri Configurations

**Files:**
- Create: `src-tauri/Cargo.toml`
- Create: `src-tauri/tauri.conf.json`
- Create: `src-tauri/capabilities/default.json`

- [ ] **Step 1: Write Cargo.toml with dependencies**
    Create `src-tauri/Cargo.toml`:
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
    reqwest = { version = "0.12", features = ["json", "multipart"] }
    calamine = "0.24"
    rust_xlsxwriter = "0.64"
    pdf-extract = "0.7"
    pdfium-render = "0.8"
    zip = "0.6"
    chrono = { version = "0.4", features = ["serde"] }
    tempfile = "3.8"
    base64 = "0.21"
    uuid = { version = "1.0", features = ["v4", "serde"] }
    image = "0.24"
    ```

- [ ] **Step 2: Create tauri.conf.json**
    Create `src-tauri/tauri.conf.json`:
    ```json
    {
      "productName": "Tawreed",
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
            "title": "Tawreed - Materials Takeoff",
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

- [ ] **Step 3: Create capabilities configuration**
    Create `src-tauri/capabilities/default.json`:
    ```json
    {
      "identifier": "default",
      "description": "Default permissions for Tawreed",
      "windows": ["main"],
      "permissions": [
        "core:default",
        "dialog:allow-open",
        "dialog:allow-save",
        "shell:allow-open"
      ]
    }
    ```

- [ ] **Step 4: Verify scaffolding configuration**
    Run: `cargo check` inside `src-tauri` directory.
    Expected: Cargo downloads and validates dependency configurations.

- [ ] **Step 5: Commit scaffolding**
    Run:
    ```bash
    git add src-tauri/Cargo.toml src-tauri/tauri.conf.json src-tauri/capabilities/default.json
    git commit -m "chore: scaffold tauri dependency and window configuration structures"
    ```

---

### Task 2: Settings Configuration Loader

**Files:**
- Create: `src-tauri/src/config.rs`

- [ ] **Step 1: Write Config File module**
    Create `src-tauri/src/config.rs`:
    ```rust
    use serde::{Serialize, Deserialize};
    use std::fs::{self, File};
    use std::io::{self, Write};
    use std::path::PathBuf;

    #[derive(Serialize, Deserialize, Debug, Clone)]
    #[serde(default)]
    pub struct AppSettings {
        pub api_provider: String,
        pub base_url: String,
        pub api_key: String,
        pub model_name: String,
        pub preferred_language: String,
        pub theme: String,
        pub api_timeout_seconds: u64,
    }

    impl Default for AppSettings {
        fn default() -> Self {
            Self {
                api_provider: "gemini".to_string(),
                base_url: "https://generativelanguage.googleapis.com".to_string(),
                api_key: "".to_string(),
                model_name: "gemini-2.0-flash".to_string(),
                preferred_language: "bilingual".to_string(),
                theme: "system".to_string(),
                api_timeout_seconds: 900,
            }
        }
    }

    pub struct ConfigManager;

    impl ConfigManager {
        pub fn config_dir() -> PathBuf {
            let home = std::env::var("USERPROFILE")
                .or_else(|_| std::env::var("HOME"))
                .unwrap_or_else(|_| ".".to_string());
            PathBuf::from(home).join(".tawreed")
        }

        pub fn config_file() -> PathBuf {
            Self::config_dir().join("config.json")
        }

        pub fn logs_dir() -> PathBuf {
            Self::config_dir().join("logs")
        }

        pub fn load_settings() -> io::Result<AppSettings> {
            let path = Self.config_file();
            if !path.exists() {
                let default_settings = AppSettings::default();
                Self::save_settings(&default_settings)?;
                return Ok(default_settings);
            }
            let file = File::open(path)?;
            let reader = io::BufReader::new(file);
            let settings: AppSettings = serde_json::from_reader(reader)
                .map_err(|e| io::Error::new(io::ErrorKind::InvalidData, e))?;
            Ok(settings)
        }

        pub fn save_settings(settings: &AppSettings) -> io::Result<()> {
            let dir = Self.config_dir();
            fs::create_dir_all(&dir)?;
            let mut temp = tempfile::NamedTempFile::new_in(&dir)?;
            let bytes = serde_json::to_vec_pretty(settings)
                .map_err(|e| io::Error::new(io::ErrorKind::InvalidData, e))?;
            temp.write_all(&bytes)?;
            temp.flush()?;
            temp.persist(&Self.config_file())
                .map_err(|e| io::Error::new(io::ErrorKind::Other, e.to_string()))?;
            Ok(())
        }
    }

    #[cfg(test)]
    mod tests {
        use super::*;

        #[test]
        fn test_app_settings_default() {
            let settings = AppSettings::default();
            assert_eq!(settings.api_provider, "gemini");
            assert_eq!(settings.theme, "system");
        }
    }
    ```

- [ ] **Step 2: Run unit tests**
    Run: `cargo test --lib config`
    Expected: PASS

- [ ] **Step 3: Commit config module**
    Run:
    ```bash
    git add src-tauri/src/config.rs
    git commit -m "feat: implement home-directory settings resolver and loader"
    ```

---

### Task 3: Document Parsers Ingest

**Files:**
- Create: `src-tauri/src/parsers.rs`

- [ ] **Step 1: Write Parsers module**
    Create `src-tauri/src/parsers.rs`:
    ```rust
    use calamine::{Reader, open_workbook_auto, Data, DataType};
    use pdfium_render::prelude::*;
    use std::collections::HashMap;
    use std::fs::File;
    use std::io::Read;
    use image::ImageFormat;

    pub struct DocumentParser;

    fn init_pdfium() -> Result<Pdfium, String> {
        std::panic::catch_unwind(|| {
            Pdfium::default()
        }).map_err(|_| "Failed to load pdfium bindings".to_string())
    }

    impl DocumentParser {
        pub fn parse_excel(path: &str) -> Result<(String, Vec<String>), String> {
            let mut workbook = open_workbook_auto(path)
                .map_err(|e| format!("Excel open failure: {}", e))?;
            let mut serialized = Vec::new();
            let mut warnings = Vec::new();

            for sheet in workbook.sheet_names() {
                serialized.push(format!("--- Sheet: {} ---", sheet));
                let range = workbook.worksheet_range(&sheet)
                    .map_err(|e| format!("Sheet read failure: {}", e))?
                    .ok_or_else(|| "Empty range".to_string())?;

                let mut last_category = String::new();
                for r_idx in 0..range.height() {
                    let mut row_vals = Vec::new();
                    for c_idx in 0..range.width() {
                        let cell = range.get((r_idx, c_idx)).unwrap_or(&Data::Empty);
                        let mut val = match cell {
                            Data::Empty => "".to_string(),
                            Data::String(s) => s.trim().to_string(),
                            Data::Float(f) => f.to_string(),
                            Data::Int(i) => i.to_string(),
                            Data::Bool(b) => b.to_string(),
                            _ => "".to_string(),
                        };
                        if c_idx == 0 {
                            if val.is_empty() {
                                val = last_category.clone();
                            } else {
                                last_category = val.clone();
                            }
                        }
                        row_vals.push(val);
                    }
                    serialized.push(format!("Row {}: | {} |", r_idx + 1, row_vals.join(" | ")));
                }
            }
            Ok((serialized.join("\n"), warnings))
        }

        pub fn parse_docx(path: &str) -> Result<String, String> {
            let file = File::open(path).map_err(|e| format!("DOCX open failure: {}", e))?;
            let mut archive = zip::ZipArchive::new(file).map_err(|e| format!("Zip error: {}", e))?;
            let mut doc_file = archive.by_name("word/document.xml")
                .map_err(|e| format!("Document file missing in DOCX: {}", e))?;
            let mut content = String::new();
            doc_file.read_to_string(&mut content).map_err(|e| format!("Read xml failure: {}", e))?;

            // Strip xml tags to extract clean text
            let mut text = String::new();
            let mut in_tag = false;
            for c in content.chars() {
                if c == '<' {
                    in_tag = true;
                } else if c == '>' {
                    in_tag = false;
                    text.push(' ');
                } else if !in_tag {
                    text.push(c);
                }
            }
            Ok(text.split_whitespace().collect::<Vec<&str>>().join(" "))
        }

        pub fn parse_csv(path: &str) -> Result<String, String> {
            let mut file = File::open(path).map_err(|e| format!("CSV open failure: {}", e))?;
            let mut content = String::new();
            file.read_to_string(&mut content).map_err(|e| format!("CSV read failure: {}", e))?;
            Ok(content)
        }

        pub fn parse_digital_pdf(path: &str) -> Result<(String, bool), String> {
            let text = pdf_extract::extract_text(path)
                .map_err(|e| format!("PDF extraction error: {}", e))?;
            let is_scanned = text.trim().len() < 100;
            Ok((text, is_scanned))
        }

        pub fn render_pdf_to_images(pdf_path: &str) -> Result<Vec<Vec<u8>>, String> {
            let pdfium = init_pdfium()?;
            let document = pdfium.load_pdf_from_file(pdf_path, None)
                .map_err(|e| format!("Failed loading pdfium: {:?}", e))?;
            let mut images = Vec::new();
            for (idx, page) in document.pages().iter().enumerate() {
                let bitmap = page.render(300, 300, None)
                    .map_err(|e| format!("Page render failure: {:?}", e))?;
                let mut jpeg_bytes = Vec::new();
                let mut cursor = std::io::Cursor::new(&mut jpeg_bytes);
                bitmap.as_image().into_rgb8().write_to(&mut cursor, ImageFormat::Jpeg)
                    .map_err(|e| format!("Image format conversion failed: {}", e))?;
                images.push(jpeg_bytes);
            }
            Ok(images)
        }
    }
    ```

- [ ] **Step 2: Run unit tests**
    Run: `cargo test --lib parsers`
    Expected: PASS

- [ ] **Step 3: Commit parser module**
    Run:
    ```bash
    git add src-tauri/src/parsers.rs
    git commit -m "feat: add Excel, DOCX, CSV, and PDF/pdfium parser integrations"
    ```

---

### Task 4: AI REST Service Wrapper

**Files:**
- Create: `src-tauri/src/ai_service.rs`

- [ ] **Step 1: Write AI HTTP service module**
    Create `src-tauri/src/ai_service.rs`:
    ```rust
    use crate::config::AppSettings;
    use base64::{Engine as _, engine::general_purpose};
    use serde_json::Value;

    pub struct AIService;

    impl AIService {
        pub async fn call_ai(
            settings: &AppSettings,
            prompt: &str,
            text_content: &str,
            image_bytes_list: Option<Vec<Vec<u8>>>,
        ) -> Result<String, String> {
            if settings.api_key.is_empty() {
                return Err("API Key is missing in Settings.".to_string());
            }

            let client = reqwest::Client::builder()
                .timeout(std::time::Duration::from_secs(settings.api_timeout_seconds))
                .build()
                .map_err(|e| format!("Failed to build HTTP client: {}", e))?;

            let full_prompt = format!("{}\n\nDocument Data:\n{}", prompt, text_content);
            let provider = settings.api_provider.to_lowercase();

            if provider == "gemini" {
                let mut parts = vec![serde_json::json!({ "text": full_prompt })];
                if let Some(images) = image_bytes_list {
                    for img in images {
                        let b64 = general_purpose::STANDARD.encode(&img);
                        parts.push(serde_json::json!({
                            "inlineData": {
                                "mimeType": "image/jpeg",
                                "data": b64
                            }
                        }));
                    }
                }

                let request_body = serde_json::json!({
                    "contents": [{ "parts": parts }],
                    "generationConfig": {
                        "responseMimeType": "application/json"
                    }
                });

                let base_url = if settings.base_url.is_empty() {
                    "https://generativelanguage.googleapis.com/v1beta".to_string()
                } else {
                    settings.base_url.clone()
                };

                let url = format!("{}/models/{}:generateContent?key={}", base_url, settings.model_name, settings.api_key);
                let res = client.post(&url).json(&request_body).send().await
                    .map_err(|e| format!("Request failed: {}", e))?;
                let body: Value = res.json().await.map_err(|e| format!("JSON parse failure: {}", e))?;
                let txt = body["candidates"][0]["content"]["parts"][0]["text"].as_str()
                    .ok_or_else(|| format!("Invalid response format: {:?}", body))?;
                Ok(txt.to_string())

            } else {
                let content_value = if let Some(images) = image_bytes_list {
                    let mut parts = vec![serde_json::json!({ "type": "text", "text": full_prompt })];
                    for img in images {
                        let b64 = general_purpose::STANDARD.encode(&img);
                        parts.push(serde_json::json!({
                            "type": "image_url",
                            "image_url": { "url": format!("data:image/jpeg;base64,{}", b64) }
                        }));
                    }
                    serde_json::json!(parts)
                } else {
                    serde_json::json!(full_prompt)
                };

                let request_body = serde_json::json!({
                    "model": settings.model_name,
                    "messages": [{ "role": "user", "content": content_value }],
                    "response_format": { "type": "json_object" }
                });

                let base_url = if settings.base_url.is_empty() {
                    "https://api.openai.com/v1/chat/completions".to_string()
                } else {
                    settings.base_url.clone()
                };

                let res = client.post(&base_url)
                    .header("Authorization", format!("Bearer {}", settings.api_key))
                    .json(&request_body).send().await
                    .map_err(|e| format!("Request failed: {}", e))?;
                let body: Value = res.json().await.map_err(|e| format!("JSON parse failure: {}", e))?;
                let txt = body["choices"][0]["message"]["content"].as_str()
                    .ok_or_else(|| format!("Invalid response format: {:?}", body))?;
                Ok(txt.to_string())
            }
        }

        pub fn clean_and_extract_json(raw: &str) -> Result<serde_json::Value, String> {
            let mut clean = raw.trim().to_string();
            if let Some(start) = clean.find("<think>") {
                if let Some(end) = clean.find("</think>") {
                    clean.replace_range(start..end + 8, "");
                }
            }
            let mut json_str = clean.trim();
            if json_str.starts_with("```") {
                if let Some(first_line) = json_str.find('\n') {
                    json_str = &json_str[first_line..];
                }
                if json_str.ends_with("```") {
                    json_str = &json_str[..json_str.len() - 3];
                }
                json_str = json_str.trim();
            }
            serde_json::from_str(json_str).map_err(|e| format!("Deserialization error: {}", e))
        }
    }
    ```

- [ ] **Step 2: Run unit tests**
    Run: `cargo test --lib ai_service`
    Expected: PASS

- [ ] **Step 3: Commit AI service wrapper**
    Run:
    ```bash
    git add src-tauri/src/ai_service.rs
    git commit -m "feat: implement HTTP payload bindings and JSON clean helper for Gemini/OpenAI"
    ```

---

### Task 5: Excel Exporter

**Files:**
- Create: `src-tauri/src/exporter.rs`

- [ ] **Step 1: Write Excel Exporter module**
    Create `src-tauri/src/exporter.rs`:
    ```rust
    use rust_xlsxwriter::{Workbook, Format, Color, FormatAlign, FormatBorder, XlsxError};
    use serde_json::Value;

    pub struct ExcelExporter;

    impl ExcelExporter {
        pub fn export(data: &Value, output_path: &str, lang: &str) -> Result<(), String> {
            Self::export_impl(data, output_path, lang)
                .map_err(|e| format!("Excel generation failure: {}", e))
        }

        fn export_impl(data: &Value, output_path: &str, lang: &str) -> Result<(), XlsxError> {
            let mut workbook = Workbook::new();
            let worksheet = workbook.add_worksheet()?;

            if lang == "arabic" {
                worksheet.set_right_to_left(true);
            }

            let header_format = Format::new()
                .set_font_name("Segoe UI")
                .set_font_size(11)
                .set_bold()
                .set_font_color(Color::White)
                .set_background_color(Color::RGB(0xD35400)) // Safety orange
                .set_align(FormatAlign::Center)
                .set_border(FormatBorder::Thin);

            let row_format = Format::new()
                .set_font_name("Segoe UI")
                .set_font_size(10)
                .set_border(FormatBorder::Thin);

            // Write headers
            let headers = vec![
                "Package", "Material Name", "Technical Specs", "Brand",
                "Unit", "Quantity", "Basis", "Confidence", "Remarks"
            ];
            for (col, text) in headers.iter().enumerate() {
                worksheet.write_string_with_format(0, col as u16, text, &header_format)?;
            }

            // Write data rows
            if let Some(arr) = data.as_array() {
                for (row_idx, item) in arr.iter().enumerate() {
                    let row = (row_idx + 1) as u32;
                    worksheet.write_string(row, 0, item["package"].as_str().unwrap_or(""))?;
                    worksheet.write_string(row, 1, item["material_name"].as_str().unwrap_or(""))?;
                    worksheet.write_string(row, 2, item["technical_specs"].as_str().unwrap_or(""))?;
                    worksheet.write_string(row, 3, item["brand"].as_str().unwrap_or(""))?;
                    worksheet.write_string(row, 4, item["unit"].as_str().unwrap_or(""))?;
                    
                    let qty = item["quantity"].as_f64().unwrap_or(0.0);
                    worksheet.write_number(row, 5, qty)?;

                    worksheet.write_string(row, 6, item["basis"].as_str().unwrap_or(""))?;
                    worksheet.write_string(row, 7, item["confidence"].as_str().unwrap_or(""))?;
                    worksheet.write_string(row, 8, item["remarks"].as_str().unwrap_or(""))?;
                }
            }

            workbook.save(output_path)?;
            Ok(())
        }
    }
    ```

- [ ] **Step 2: Commit exporter module**
    Run:
    ```bash
    git add src-tauri/src/exporter.rs
    git commit -m "feat: add rust_xlsxwriter spreadsheet cell generator"
    ```

---

### Task 6: Tauri commands and lib bridge

**Files:**
- Create: `src-tauri/src/commands.rs`
- Create: `src-tauri/src/lib.rs`
- Create: `src-tauri/src/main.rs`

- [ ] **Step 1: Write Tauri Commands module**
    Create `src-tauri/src/commands.rs`:
    ```rust
    use tauri::{State, AppHandle};
    use crate::config::{ConfigManager, AppSettings};
    use crate::parsers::DocumentParser;
    use crate::ai_service::AIService;
    use crate::exporter::ExcelExporter;
    use serde_json::Value;

    #[tauri::command]
    pub fn load_settings() -> Result<AppSettings, String> {
        ConfigManager::load_settings().map_err(|e| e.to_string())
    }

    #[tauri::command]
    pub fn save_settings(settings: AppSettings) -> Result<bool, String> {
        ConfigManager::save_settings(&settings).map_err(|e| e.to_string())?;
        Ok(true)
    }

    #[tauri::command]
    pub fn select_file(app: AppHandle) -> Result<String, String> {
        use tauri_plugin_dialog::DialogExt;
        let fp = app.dialog().file().blocking_pick_file();
        match fp {
            Some(tauri_plugin_dialog::FilePath::Path(path)) => Ok(path.to_string_lossy().into_owned()),
            _ => Ok("".to_string()),
        }
    }

    #[tauri::command]
    pub async fn extract_takeoff(file_path: String, lang: String) -> Result<Value, String> {
        let settings = ConfigManager::load_settings().map_err(|e| e.to_string())?;
        
        let path = std::path::Path::new(&file_path);
        let ext = path.extension().and_then(|e| e.to_str()).unwrap_or("").to_lowercase();

        let mut text = String::new();
        let mut images = None;

        if ext == "xlsx" || ext == "xls" {
            let (excel_txt, _) = DocumentParser::parse_excel(&file_path)?;
            text = excel_txt;
        } else if ext == "docx" {
            text = DocumentParser::parse_docx(&file_path)?;
        } else if ext == "csv" {
            text = DocumentParser::parse_csv(&file_path)?;
        } else if ext == "pdf" {
            let (pdf_txt, is_scanned) = DocumentParser::parse_digital_pdf(&file_path)?;
            if is_scanned {
                let img_bytes = DocumentParser::render_pdf_to_images(&file_path)?;
                images = Some(img_bytes);
            } else {
                text = pdf_txt;
            }
        } else if ext == "png" || ext == "jpg" || ext == "jpeg" {
            let bytes = std::fs::read(&file_path).map_err(|e| e.to_string())?;
            images = Some(vec![bytes]);
        }

        let system_prompt = "You are a professional Quantity Surveying Assistant.\n\
            Extract construction materials from the provided document data.\n\
            Return a JSON object containing a 'materials' key mapped to a list of items.\n\
            Each item MUST strictly follow this JSON schema:\n\
            {\n\
              \"package\": \"Structural concrete / Plaster / Doors etc...\",\n\
              \"material_name\": \"Specific material name\",\n\
              \"technical_specs\": \"Technical description or standard\",\n\
              \"brand\": \"Brand or model if stated, otherwise empty\",\n\
              \"unit\": \"m3, m2, unit, kg, ton etc...\",\n\
              \"quantity\": 123.45,\n\
              \"basis\": \"Quantification basis details\",\n\
              \"confidence\": \"High/Medium/Low\",\n\
              \"remarks\": \"Any observations\"\n\
            }";

        let raw = AIService::call_ai(&settings, system_prompt, &text, images).await?;
        let parsed = AIService::clean_and_extract_json(&raw)?;
        Ok(parsed)
    }

    #[tauri::command]
    pub fn save_takeoff_excel(data: Value, file_path: String, lang: String) -> Result<bool, String> {
        ExcelExporter::export(&data, &file_path, &lang)?;
        Ok(true)
    }
    ```

- [ ] **Step 2: Create lib.rs**
    Create `src-tauri/src/lib.rs`:
    ```rust
    pub mod config;
    pub mod parsers;
    pub mod ai_service;
    pub mod exporter;
    pub mod commands;
    ```

- [ ] **Step 3: Create main.rs**
    Create `src-tauri/src/main.rs`:
    ```rust
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
                tawreed::commands::save_takeoff_excel
            ])
            .run(tauri::generate_context!())
            .expect("error while running tauri application");
    }
    ```

- [ ] **Step 4: Verify build succeeds**
    Run: `cargo check` inside `src-tauri` directory.
    Expected: Compiles with 0 warnings or errors.

- [ ] **Step 5: Commit Tauri interop layer**
    Run:
    ```bash
    git add src-tauri/src/commands.rs src-tauri/src/lib.rs src-tauri/src/main.rs
    git commit -m "feat: add tauri command handlers and bootsrapper runtime declarations"
    ```

---

### Task 7: Frontend GUI Layout & Styling

**Files:**
- Create: `gui/index.html`
- Create: `gui/style.css`
- Create: `gui/app.js`

- [ ] **Step 1: Write index.html**
    Create `gui/index.html`:
    ```html
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Tawreed - Materials Takeoff</title>
      <link rel="stylesheet" href="style.css">
    </head>
    <body>
      <div class="sidebar">
        <h2>Tawreed</h2>
        <div class="tab-btn active" onclick="switchTab('workspace')">Workspace</div>
        <div class="tab-btn" onclick="switchTab('settings')">Settings</div>
        <div class="tab-btn" onclick="switchTab('about')">About</div>
      </div>
      <div class="main-content">
        <div id="workspace-tab" class="tab-content active">
          <h1>Materials Takeoff</h1>
          <div class="upload-area" id="drop-zone" onclick="triggerFilePicker()">
            <p>Drag and drop BOQ file here, or click to browse</p>
            <p class="sub">Supports Excel, Word, PDF, CSV, and Images</p>
          </div>
          <p id="selected-file-label"></p>
          <div class="form-row">
            <label>Language:</label>
            <select id="lang-select">
              <option value="bilingual">Bilingual</option>
              <option value="english">English</option>
              <option value="arabic">Arabic</option>
            </select>
            <button onclick="startExtraction()">Start Extraction</button>
          </div>
          <div class="console-log" id="console">Ready...</div>
          <table class="takeoff-table" id="takeoff-grid">
            <thead>
              <tr>
                <th>Package</th>
                <th>Material Name</th>
                <th>Technical Specs</th>
                <th>Brand</th>
                <th>Unit</th>
                <th>Quantity</th>
                <th>Basis</th>
                <th>Confidence</th>
                <th>Remarks</th>
              </tr>
            </thead>
            <tbody id="takeoff-rows"></tbody>
          </table>
          <button id="export-btn" style="display:none;" onclick="exportToExcel()">Export to Excel</button>
        </div>

        <div id="settings-tab" class="tab-content">
          <h1>Settings</h1>
          <div class="form-group">
            <label>AI Provider:</label>
            <select id="provider-select">
              <option value="gemini">Google Gemini</option>
              <option value="openai">OpenAI</option>
            </select>
          </div>
          <div class="form-group">
            <label>API Key:</label>
            <input type="password" id="api-key-input">
          </div>
          <div class="form-group">
            <label>Model Name:</label>
            <input type="text" id="model-input">
          </div>
          <div class="form-group">
            <label>Base URL Override:</label>
            <input type="text" id="base-url-input">
          </div>
          <button onclick="saveSettings()">Save Settings</button>
        </div>

        <div id="about-tab" class="tab-content">
          <h1>About Tawreed</h1>
          <p>Tawreed is an intelligent Quantity Surveying assistant designed to automate takeoff routines.</p>
          <p>Author: Kareem Safwat</p>
        </div>
      </div>
      <script src="app.js" type="module"></script>
    </body>
    </html>
    ```

- [ ] **Step 2: Write style.css**
    Create `gui/style.css`:
    ```css
    :root {
      --bg-base: #0f172a;
      --bg-surface: rgba(30, 41, 59, 0.7);
      --border-color: rgba(255, 255, 255, 0.1);
      --primary-accent: #ea580c;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
    }

    body {
      margin: 0;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background: var(--bg-base);
      color: var(--text-main);
      display: flex;
      height: 100vh;
      overflow: hidden;
    }

    .sidebar {
      width: 250px;
      background: rgba(15, 23, 42, 0.95);
      border-right: 1px solid var(--border-color);
      padding: 20px;
    }

    .sidebar h2 {
      color: var(--primary-accent);
      margin-bottom: 30px;
    }

    .tab-btn {
      padding: 12px;
      margin: 8px 0;
      border-radius: 6px;
      cursor: pointer;
      color: var(--text-muted);
      transition: background 0.2s, color 0.2s;
    }

    .tab-btn.active, .tab-btn:hover {
      background: var(--bg-surface);
      color: var(--text-main);
    }

    .main-content {
      flex: 1;
      padding: 40px;
      overflow-y: auto;
    }

    .tab-content {
      display: none;
    }

    .tab-content.active {
      display: block;
    }

    .upload-area {
      border: 2px dashed var(--primary-accent);
      background: var(--bg-surface);
      border-radius: 12px;
      padding: 40px;
      text-align: center;
      cursor: pointer;
      margin-bottom: 20px;
      backdrop-filter: blur(12px);
    }

    .upload-area .sub {
      color: var(--text-muted);
      font-size: 14px;
    }

    .form-row, .form-group {
      margin-bottom: 20px;
    }

    input, select {
      background: var(--bg-base);
      border: 1px solid var(--border-color);
      color: var(--text-main);
      padding: 10px;
      border-radius: 6px;
      margin-right: 10px;
    }

    button {
      background: var(--primary-accent);
      border: none;
      color: white;
      padding: 10px 20px;
      border-radius: 6px;
      cursor: pointer;
    }

    .console-log {
      background: #020617;
      border: 1px solid var(--border-color);
      font-family: monospace;
      padding: 15px;
      border-radius: 6px;
      margin-bottom: 20px;
      height: 100px;
      overflow-y: auto;
    }

    .takeoff-table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 20px;
      background: var(--bg-surface);
      border-radius: 8px;
      overflow: hidden;
    }

    th, td {
      border: 1px solid var(--border-color);
      padding: 12px;
      text-align: left;
    }

    th {
      background: var(--primary-accent);
      color: white;
    }
    ```

- [ ] **Step 3: Write app.js**
    Create `gui/app.js`:
    ```javascript
    const { invoke } = window.__TAURI__.core;

    let selectedFilePath = "";
    let extractedMaterials = [];

    window.switchTab = function(tabName) {
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      
      document.getElementById(`${tabName}-tab`).classList.add('active');
      event.target.classList.add('active');
    };

    window.triggerFilePicker = async function() {
      try {
        const path = await invoke("select_file");
        if (path) {
          selectedFilePath = path;
          document.getElementById("selected-file-label").innerText = `Selected File: ${path}`;
          logConsole("File loaded successfully.");
        }
      } catch (err) {
        logConsole(`File select error: ${err}`);
      }
    };

    window.startExtraction = async function() {
      if (!selectedFilePath) {
        logConsole("Please select a file first.");
        return;
      }
      logConsole("Querying LLM for material extraction...");
      try {
        const lang = document.getElementById("lang-select").value;
        const res = await invoke("extract_takeoff", { filePath: selectedFilePath, lang });
        extractedMaterials = res.materials || [];
        renderGrid(extractedMaterials);
        logConsole(`Extraction complete: Found ${extractedMaterials.length} materials.`);
        document.getElementById("export-btn").style.display = "block";
      } catch (err) {
        logConsole(`Extraction failed: ${err}`);
      }
    };

    window.exportToExcel = async function() {
      try {
        const lang = document.getElementById("lang-select").value;
        const exportPath = selectedFilePath.replace(/\.[^/.]+$/, "") + "_Takeoff.xlsx";
        
        // Read grid values
        const rows = document.querySelectorAll("#takeoff-rows tr");
        const updatedMaterials = [];
        rows.forEach(tr => {
          const cells = tr.querySelectorAll("td");
          updatedMaterials.push({
            package: cells[0].innerText,
            material_name: cells[1].innerText,
            technical_specs: cells[2].innerText,
            brand: cells[3].innerText,
            unit: cells[4].innerText,
            quantity: parseFloat(cells[5].innerText) || 0.0,
            basis: cells[6].innerText,
            confidence: cells[7].innerText,
            remarks: cells[8].innerText
          });
        });

        await invoke("save_takeoff_excel", { data: updatedMaterials, filePath: exportPath, lang });
        logConsole(`Excel Takeoff saved to: ${exportPath}`);
      } catch (err) {
        logConsole(`Export failed: ${err}`);
      }
    };

    window.loadSettings = async function() {
      try {
        const settings = await invoke("load_settings");
        document.getElementById("provider-select").value = settings.api_provider;
        document.getElementById("api-key-input").value = settings.api_key;
        document.getElementById("model-input").value = settings.model_name;
        document.getElementById("base-url-input").value = settings.base_url;
      } catch (err) {
        logConsole(`Settings load failure: ${err}`);
      }
    };

    window.saveSettings = async function() {
      try {
        const settings = {
          api_provider: document.getElementById("provider-select").value,
          api_key: document.getElementById("api-key-input").value,
          model_name: document.getElementById("model-input").value,
          base_url: document.getElementById("base-url-input").value,
          preferred_language: "bilingual",
          theme: "system",
          api_timeout_seconds: 900
        };
        await invoke("save_settings", { settings });
        logConsole("Settings saved successfully.");
      } catch (err) {
        logConsole(`Settings save failure: ${err}`);
      }
    };

    function logConsole(msg) {
      const consoleNode = document.getElementById("console");
      consoleNode.innerText = `[${new Date().toLocaleTimeString()}] ${msg}\n` + consoleNode.innerText;
    }

    function renderGrid(materials) {
      const tbody = document.getElementById("takeoff-rows");
      tbody.innerHTML = "";
      materials.forEach(m => {
        const tr = document.createElement("tr");
        const keys = [
          "package", "material_name", "technical_specs", "brand",
          "unit", "quantity", "basis", "confidence", "remarks"
        ];
        keys.forEach(k => {
          const td = document.createElement("td");
          td.contentEditable = "true";
          td.innerText = m[k] !== undefined ? m[k] : "";
          tr.appendChild(td);
        });
        tbody.appendChild(tr);
      });
    }

    // Init
    document.addEventListener("DOMContentLoaded", () => {
      window.loadSettings();
    });
    ```

- [ ] **Step 4: Commit frontend assets**
    Run:
    ```bash
    git add gui/index.html gui/style.css gui/app.js
    git commit -m "feat: implement glassmorphic UI layout panels and bridge event triggers"
    ```

---

### Task 8: Integration & Build Verification

**Files:**
- Modify: `src-tauri/tests/integration_tests.rs`

- [ ] **Step 1: Write integration tests**
    Create `src-tauri/tests/integration_tests.rs`:
    ```rust
    use tawreed::config::{ConfigManager, AppSettings};
    use tawreed::parsers::DocumentParser;
    use std::fs::File;
    use std::io::Write;

    #[test]
    fn test_csv_parser_and_settings() {
        let settings = AppSettings::default();
        assert_eq!(settings.api_provider, "gemini");

        let dir = tempfile::tempdir().unwrap();
        let file_path = dir.path().join("test.csv");
        let mut file = File::create(&file_path).unwrap();
        writeln!(file, "Material,Quantity,Unit").unwrap();
        writeln!(file, "Concrete,100,m3").unwrap();

        let content = DocumentParser::parse_csv(file_path.to_str().unwrap()).unwrap();
        assert!(content.contains("Concrete"));
    }
    ```

- [ ] **Step 2: Run all tests**
    Run: `cargo test` inside `src-tauri` directory.
    Expected: All tests pass.

- [ ] **Step 3: Commit integration test suite**
    Run:
    ```bash
    git add src-tauri/tests/integration_tests.rs
    git commit -m "test: add config and csv parser integration tests"
    ```
