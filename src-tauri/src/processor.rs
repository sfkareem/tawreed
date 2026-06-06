use calamine::{open_workbook, Data, Reader, Xlsx, DataType};
use rust_xlsxwriter::{Workbook, Format, FormatBorder, Color, FormatAlign};
use serde_json::{json, Value};
use std::collections::HashMap;
use tauri::{AppHandle, Emitter};

pub async fn slice_boq(
    app: AppHandle,
    file_path: &str,
    base_url: &str,
    model: &str,
    api_key: &str,
) -> Result<String, String> {
    let _ = app.emit("boq-progress", "Initializing Slab Agent core engine...");

    let mut excel: Xlsx<_> = open_workbook(file_path).map_err(|e| format!("Could not open file: {}", e))?;
    let sheet_names = excel.sheet_names().to_owned();
    if sheet_names.is_empty() {
        return Err("Excel file is empty".into());
    }

    let _ = app.emit("boq-progress", format!("Slab Agent mapping structural relationships across {} sheets...", sheet_names.len()));

    let mut all_data: Vec<(String, String, Vec<Data>)> = Vec::new(); // (row_id, sheet_name, original_row_data)
    let mut headers_map: HashMap<String, Vec<String>> = HashMap::new();
    let mut markdown_content = String::new();
    
    let mut global_row_id = 1;

    // 1. Extract and convert all sheets to Markdown with Unique IDs
    for sheet_name in &sheet_names {
        if let Ok(range) = excel.worksheet_range(sheet_name) {
            markdown_content.push_str(&format!("## Sheet: {}\n", sheet_name));
            
            for (i, row) in range.rows().enumerate() {
                let row_strs: Vec<String> = row.iter().map(|c| match c {
                    Data::String(s) => s.replace("\n", " ").replace("|", " "),
                    Data::Float(f) => f.to_string(),
                    Data::Int(i) => i.to_string(),
                    Data::Bool(b) => b.to_string(),
                    _ => "".to_string(),
                }).collect();

                // Skip completely empty rows
                if row_strs.iter().all(|s| s.trim().is_empty()) {
                    continue;
                }

                if i == 0 {
                    headers_map.insert(sheet_name.clone(), row_strs.clone());
                    markdown_content.push_str(&format!("| ID | {} |\n", row_strs.join(" | ")));
                    let mut sep = vec!["---"];
                    sep.extend(vec!["---"; row_strs.len()]);
                    markdown_content.push_str(&format!("| {} |\n", sep.join(" | ")));
                    continue;
                }

                let row_id = format!("R{}", global_row_id);
                global_row_id += 1;

                all_data.push((row_id.clone(), sheet_name.clone(), row.to_vec()));
                markdown_content.push_str(&format!("| {} | {} |\n", row_id, row_strs.join(" | ")));
            }
            markdown_content.push_str("\n");
        }
    }

    let _ = app.emit("boq-progress", format!("Slab Agent compressed {} unique items into token-efficient payload...", global_row_id - 1));
    let _ = app.emit("boq-progress", "Dispatching payload to remote LLM for structural categorization...");

    // 2. Call LLM One-Shot
    let prompt = format!(
        "You are an expert construction estimator. I am providing a complete Bill of Quantities (BOQ) spanning multiple sheets, formatted as Markdown tables.\n\
        The first column in every table is a unique 'ID' (e.g., R1, R2).\n\
        Analyze the document and extract:\n\
        1. 'project_name': The overall name of the project. If you cannot find one, return null.\n\
        2. 'date': The date of the document. If you cannot find one, return null.\n\
        3. 'items': A dictionary where the keys are the exact IDs (e.g., \"R1\") and the values are the short category names (e.g., Masonry, Concrete).\n\n\
        Return ONLY a raw JSON object matching this structure: {{\"project_name\": \"...\", \"date\": \"...\", \"items\": {{\"R1\": \"...\"}}}}.\n\
        DO NOT wrap the JSON in ```json blocks. Return ONLY the raw JSON.\n\n\
        BOQ Markdown:\n{}",
        markdown_content
    );

    let client = reqwest::Client::new();
    let req_body = json!({
        "model": model,
        "messages": [
            {"role": "system", "content": "You output ONLY a raw JSON dictionary mapping IDs to categories. Absolutely no markdown blocks, no intro text."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.0
    });

    let resp = client
        .post(format!("{}/chat/completions", base_url.trim_end_matches('/')))
        .header("Authorization", format!("Bearer {}", api_key))
        .json(&req_body)
        .send()
        .await
        .map_err(|e| format!("Request failed: {}", e))?;

    if !resp.status().is_success() {
        let error_text = resp.text().await.unwrap_or_default();
        return Err(format!("LLM Error: {}", error_text));
    }

    let _ = app.emit("boq-progress", "Slab Agent received response. Verifying semantic mapping...");

    let result: Value = resp.json().await.map_err(|e| format!("Parse error: {}", e))?;
    let mut category_map: HashMap<String, String> = HashMap::new();
    let mut project_name: Option<String> = None;
    let mut project_date: Option<String> = None;

    if let Some(choices) = result["choices"].as_array() {
        if let Some(msg) = choices.get(0).and_then(|c| c["message"]["content"].as_str()) {
            
            // Robust JSON Extraction to ignore hallucinated markdown or conversational text
            let clean_msg = msg.trim();
            
            // Bypass <think> blocks entirely (Reasoning models often place `{` inside their thoughts)
            let mut actual_content = clean_msg;
            if let Some(idx) = clean_msg.rfind("</think>") {
                actual_content = &clean_msg[idx + 8..];
            }

            let start_idx = actual_content.find('{');
            let end_idx = actual_content.rfind('}');
            
            if let (Some(start), Some(end)) = (start_idx, end_idx) {
                if start <= end {
                    let json_str = &actual_content[start..=end];
                    if let Ok(parsed) = serde_json::from_str::<Value>(json_str) {
                        if let Some(name) = parsed.get("project_name").and_then(|v| v.as_str()) {
                            project_name = Some(name.to_string());
                        }
                        if let Some(date) = parsed.get("date").and_then(|v| v.as_str()) {
                            project_date = Some(date.to_string());
                        }
                        if let Some(items) = parsed.get("items").and_then(|v| v.as_object()) {
                            for (k, v) in items {
                                if let Some(v_str) = v.as_str() {
                                    category_map.insert(k.clone(), v_str.to_string());
                                }
                            }
                        }
                    } else {
                        return Err(format!("Slab Agent failed to parse extracted dictionary: {}", json_str));
                    }
                } else {
                    return Err("Slab Agent detected structural anomaly: Malformed JSON boundaries.".into());
                }
            } else {
                return Err("Slab Agent could not find JSON dictionary in the response.".into());
            }
        }
    }

    let _ = app.emit("boq-progress", "Slab Agent reconstructing workbooks and writing final slices...");

    // 3. Reconstruct into categorized Excel
    let mut categorized_data: HashMap<String, Vec<(String, Vec<Data>)>> = HashMap::new();

    for (row_id, sheet_name, row_data) in all_data {
        let category = category_map.get(&row_id).cloned().unwrap_or_else(|| "Uncategorized".to_string());
        categorized_data.entry(category).or_insert_with(Vec::new).push((sheet_name, row_data));
    }

    let mut workbook = Workbook::new();

    // 4. Create Master Summary Sheet placeholder (so it becomes the first tab)
    let _ = workbook.add_worksheet().set_name("Master Summary").map_err(|e| e.to_string())?;

    // Define Formatting Standards
    let header_format = Format::new()
        .set_bold()
        .set_font_name("Calibri")
        .set_font_size(11)
        .set_border(FormatBorder::Thin)
        .set_background_color(Color::RGB(0xE7E6E6)) // Light Grey
        .set_align(FormatAlign::Center)
        .set_align(FormatAlign::VerticalCenter)
        .set_text_wrap();

    let string_format = Format::new()
        .set_font_name("Calibri")
        .set_font_color(Color::RGB(0x000000))
        .set_border(FormatBorder::Thin)
        .set_align(FormatAlign::Top)
        .set_text_wrap();

    let center_string_format = Format::new()
        .set_font_name("Calibri")
        .set_font_color(Color::RGB(0x000000))
        .set_border(FormatBorder::Thin)
        .set_align(FormatAlign::Top)
        .set_align(FormatAlign::Center)
        .set_text_wrap();

    let num_format = Format::new()
        .set_font_name("Calibri")
        .set_font_color(Color::RGB(0x000000))
        .set_border(FormatBorder::Thin)
        .set_align(FormatAlign::Top)
        .set_num_format("#,##0.00;(#,##0.00);-"); // Zeroes as dashes

    let warning_format = Format::new()
        .set_font_name("Calibri")
        .set_bold()
        .set_border(FormatBorder::Thin)
        .set_font_color(Color::RGB(0xFF0000)) // Red text for visibility
        .set_background_color(Color::RGB(0xF2F2F2)) // Soft Grey background
        .set_align(FormatAlign::Top)
        .set_num_format("#,##0.00;(#,##0.00);-");

    let mut category_totals_info: Vec<(String, String)> = Vec::new(); // (CategoryName, AbsoluteCellReference)

    for (category, rows) in &categorized_data {
        let mut safe_name = category.replace(&['/', '\\', '?', '*', ':', '[', ']'][..], "").chars().take(31).collect::<String>();
        if safe_name.is_empty() { safe_name = "Category".to_string(); }

        let sheet = workbook.add_worksheet().set_name(&safe_name).map_err(|e| e.to_string())?;
        
        // CRITICAL: Arabic Right-To-Left direction
        sheet.set_right_to_left(true);

        // Professional column widths
        let _ = sheet.set_column_width(0, 20); // Source sheet name
        let _ = sheet.set_column_width(1, 15); // Item ID
        let _ = sheet.set_column_width(2, 60); // Description
        let _ = sheet.set_column_width(3, 15); // Unit
        let _ = sheet.set_column_width(4, 15); // Qty
        let _ = sheet.set_column_width(5, 15); // Rate
        let _ = sheet.set_column_width(6, 15); // Total

        let first_source = &rows[0].0;
        let mut qty_col: Option<u16> = None;
        let mut rate_col: Option<u16> = None;
        let mut total_col: Option<u16> = None;

        // Write Header
        sheet.write_with_format(0, 0, "Source Sheet", &header_format).map_err(|e| e.to_string())?;
        
        if let Some(headers) = headers_map.get(first_source) {
            for (col, val) in headers.iter().enumerate() {
                let c = (col + 1) as u16;
                sheet.write_with_format(0, c, val, &header_format).map_err(|e| e.to_string())?;
                
                let lower = val.to_lowercase();
                if lower.contains("كمية") || lower.contains("qty") || lower.contains("quantity") { qty_col = Some(c); }
                if lower.contains("سعر") || lower.contains("فئة") || lower.contains("rate") || lower.contains("price") { rate_col = Some(c); }
                if lower.contains("اجمالي") || lower.contains("جملة") || lower.contains("total") || lower.contains("amount") { total_col = Some(c); }
            }
        }

        let mut current_row: u32 = 1;

        // Write Rows
        for (source_sheet, row) in rows.iter() {
            sheet.write_with_format(current_row, 0, source_sheet, &center_string_format).map_err(|e| e.to_string())?;
            
            for (c_idx, val) in row.iter().enumerate() {
                let c = (c_idx + 1) as u16;
                
                let mut is_missing = false;
                if Some(c) == qty_col || Some(c) == rate_col {
                    if let Data::Empty = val { is_missing = true; }
                    else if let Data::String(s) = val { if s.trim().is_empty() { is_missing = true; } }
                    else if let Data::Float(f) = val { if *f == 0.0 { is_missing = true; } }
                    else if let Data::Int(i) = val { if *i == 0 { is_missing = true; } }

                    if is_missing {
                        let _ = app.emit("boq-warning", format!("⚠️ Missing {} in sheet '{}', row '{}'", 
                            if Some(c) == qty_col { "Quantity" } else { "Rate" }, source_sheet, current_row));
                    }
                }

                let active_format = if is_missing { 
                    &warning_format 
                } else if val.is_float() || val.is_int() { 
                    &num_format 
                } else if c == 1 || c == 3 { 
                    &center_string_format 
                } else { 
                    &string_format 
                };

                if Some(c) == total_col && qty_col.is_some() && rate_col.is_some() {
                    let qty_cell = rust_xlsxwriter::utility::row_col_to_cell(current_row, qty_col.unwrap());
                    let rate_cell = rust_xlsxwriter::utility::row_col_to_cell(current_row, rate_col.unwrap());
                    let formula = format!("={}*{}", qty_cell, rate_cell);
                    sheet.write_formula_with_format(current_row, c, formula.as_str(), &num_format).map_err(|e| e.to_string())?;
                } else {
                    match val {
                        Data::Float(f) => { sheet.write_number_with_format(current_row, c, *f, active_format).map_err(|e| e.to_string())?; },
                        Data::Int(i) => { sheet.write_number_with_format(current_row, c, *i as f64, active_format).map_err(|e| e.to_string())?; },
                        Data::String(s) => { sheet.write_string_with_format(current_row, c, s, active_format).map_err(|e| e.to_string())?; },
                        Data::Bool(b) => { sheet.write_boolean_with_format(current_row, c, *b, active_format).map_err(|e| e.to_string())?; },
                        _ => { sheet.write_string_with_format(current_row, c, "-", active_format).map_err(|e| e.to_string())?; },
                    }
                }
            }
            current_row += 1;
        }

        // Write Category Summary Row
        if let Some(t_col) = total_col {
            if current_row > 1 {
                let start_cell = rust_xlsxwriter::utility::row_col_to_cell(1, t_col);
                let end_cell = rust_xlsxwriter::utility::row_col_to_cell(current_row - 1, t_col);
                let sum_formula = format!("=SUM({}:{})", start_cell, end_cell);
                
                sheet.write_with_format(current_row, t_col - 1, "الاجمالي (Total)", &header_format).map_err(|e| e.to_string())?;
                sheet.write_formula_with_format(current_row, t_col, sum_formula.as_str(), &header_format).map_err(|e| e.to_string())?;
                
                let total_ref_cell = rust_xlsxwriter::utility::row_col_to_cell_absolute(current_row, t_col);
                category_totals_info.push((safe_name.clone(), total_ref_cell));
            }
        }
    }

    // 5. Populate Master Summary Sheet
    if !category_totals_info.is_empty() {
        let mut summary_sheet = workbook.worksheet_from_name("Master Summary").map_err(|e| e.to_string())?;
        summary_sheet.set_right_to_left(true);

        let _ = summary_sheet.set_column_width(0, 40);
        let _ = summary_sheet.set_column_width(1, 25);

        summary_sheet.write_with_format(0, 0, "القسم (Category)", &header_format).map_err(|e| e.to_string())?;
        summary_sheet.write_with_format(0, 1, "القيمة (Amount)", &header_format).map_err(|e| e.to_string())?;

        let mut sum_row = 1;
        for (cat_name, cell_ref) in &category_totals_info {
            summary_sheet.write_with_format(sum_row, 0, cat_name, &string_format).map_err(|e| e.to_string())?;
            let link_formula = format!("='{}'!{}", cat_name, cell_ref);
            summary_sheet.write_formula_with_format(sum_row, 1, link_formula.as_str(), &num_format).map_err(|e| e.to_string())?;
            sum_row += 1;
        }

        if sum_row > 1 {
            let start_sum = rust_xlsxwriter::utility::row_col_to_cell(1, 1);
            let end_sum = rust_xlsxwriter::utility::row_col_to_cell(sum_row - 1, 1);
            summary_sheet.write_with_format(sum_row, 0, "الاجمالي الكلي (Grand Total)", &header_format).map_err(|e| e.to_string())?;
            let final_formula = format!("=SUM({}:{})", start_sum, end_sum);
            summary_sheet.write_formula_with_format(sum_row, 1, final_formula.as_str(), &header_format).map_err(|e| e.to_string())?;
        }
    }

    let output_path = format!("{}_sliced.xlsx", file_path);
    workbook.save(&output_path).map_err(|e| format!("Failed to save excel: {}", e))?;

    let _ = app.emit("boq-progress", "Slab Agent execution complete. Payload secured.");

    Ok(output_path)
}
