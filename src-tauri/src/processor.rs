use calamine::{Reader, open_workbook, Xlsx, Data};
use rust_xlsxwriter::Workbook;
use serde_json::{json, Value};
use std::collections::HashMap;

pub async fn slice_boq(file_path: &str, base_url: &str, model: &str, api_key: &str) -> Result<String, String> {
    let mut excel: Xlsx<_> = open_workbook(file_path).map_err(|e| format!("Could not open file: {}", e))?;
    let sheet_names = excel.sheet_names().to_owned();
    if sheet_names.is_empty() {
        return Err("Excel file is empty".into());
    }
    
    let first_sheet = &sheet_names[0];
    let range = excel.worksheet_range(first_sheet).map_err(|e| format!("Cannot read sheet: {}", e))?;

    let client = reqwest::Client::new();
    let mut categorized_data: HashMap<String, Vec<Vec<String>>> = HashMap::new();
    let mut headers: Vec<String> = Vec::new();

    // Iterate through rows
    for (i, row) in range.rows().enumerate() {
        let row_strs: Vec<String> = row.iter().map(|c| match c {
            Data::String(s) => s.to_string(),
            Data::Float(f) => f.to_string(),
            Data::Int(i) => i.to_string(),
            Data::Bool(b) => b.to_string(),
            _ => "".to_string(),
        }).collect();

        if i == 0 {
            headers = row_strs;
            continue;
        }

        let item_desc = row_strs.join(" | ");
        if item_desc.trim().is_empty() {
            continue;
        }

        let prompt = format!("Categorize this construction BOQ item into exactly one short work package name (e.g. Masonry, Plaster, Concrete, Finishes, HVAC). Return ONLY the work package name, nothing else. Item: {}", item_desc);

        // Call LLM
        let req_body = json!({
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a construction estimator. Reply with exactly one category name."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.0
        });

        let resp = client.post(format!("{}/chat/completions", base_url.trim_end_matches('/')))
            .header("Authorization", format!("Bearer {}", api_key))
            .json(&req_body)
            .send()
            .await
            .map_err(|e| format!("Request failed: {}", e))?;

        if !resp.status().is_success() {
            let error_text = resp.text().await.unwrap_or_default();
            return Err(format!("LLM Error: {}", error_text));
        }

        let result: Value = resp.json().await.map_err(|e| format!("Parse error: {}", e))?;
        let mut category = "Uncategorized".to_string();
        
        if let Some(choices) = result["choices"].as_array() {
            if let Some(msg) = choices.get(0).and_then(|c| c["message"]["content"].as_str()) {
                category = msg.trim().to_string();
            }
        }

        categorized_data.entry(category).or_insert_with(Vec::new).push(row_strs);
    }

    // Write a new Excel workbook
    let mut workbook = Workbook::new();
    for (category, rows) in categorized_data {
        let safe_name = category.replace(&['/', '\\', '?', '*', ':', '[', ']'][..], "").chars().take(31).collect::<String>();
        let sheet = workbook.add_worksheet().set_name(&safe_name).map_err(|e| e.to_string())?;

        for (col, h) in headers.iter().enumerate() {
            sheet.write_string(0, col as u16, h).map_err(|e| e.to_string())?;
        }

        for (r_idx, row) in rows.iter().enumerate() {
            for (c_idx, val) in row.iter().enumerate() {
                sheet.write_string((r_idx + 1) as u32, c_idx as u16, val).map_err(|e| e.to_string())?;
            }
        }
    }

    let output_path = format!("{}_sliced.xlsx", file_path);
    workbook.save(&output_path).map_err(|e| format!("Failed to save excel: {}", e))?;

    Ok(output_path)
}
