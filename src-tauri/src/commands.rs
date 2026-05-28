use tauri::AppHandle;
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
        Some(tauri_plugin_dialog::FilePath::Url(url)) => Ok(url.to_string()),
        _ => Ok("".to_string()),
    }
}

#[tauri::command]
pub async fn extract_takeoff(file_path: String, _lang: String) -> Result<Value, String> {
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

#[tauri::command]
pub fn open_file(path: String) -> Result<bool, String> {
    #[cfg(target_os = "windows")]
    {
        std::process::Command::new("explorer")
            .arg(&path)
            .spawn()
            .map_err(|e| e.to_string())?;
    }
    #[cfg(target_os = "macos")]
    {
        std::process::Command::new("open")
            .arg(&path)
            .spawn()
            .map_err(|e| e.to_string())?;
    }
    #[cfg(target_os = "linux")]
    {
        std::process::Command::new("xdg-open")
            .arg(&path)
            .spawn()
            .map_err(|e| e.to_string())?;
    }
    Ok(true)
}
