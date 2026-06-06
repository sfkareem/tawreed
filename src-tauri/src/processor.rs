use calamine::{open_workbook, Data, Reader, Xlsx};
use rust_xlsxwriter::{Workbook, Format, FormatBorder, Color, FormatAlign, Table};
use serde_json::{json, Value};
use std::collections::HashMap;
use tauri::{AppHandle, Emitter};

#[derive(serde::Serialize, Clone)]
struct StreamPayload {
    token: String,
    is_thought: bool,
}

pub async fn extract_work_packages(
    app: AppHandle,
    file_path: &str,
    base_url: &str,
    model: &str,
    api_key: &str,
) -> Result<(String, i64), String> {
    let _ = app.emit("boq-progress", "Initializing Tawreed Extractor core engine...");

    let mut excel: Xlsx<_> = open_workbook(file_path).map_err(|e| format!("Could not open file: {}", e))?;
    let sheet_names = excel.sheet_names().to_owned();
    if sheet_names.is_empty() {
        return Err("Excel file is empty".into());
    }

    let _ = app.emit("boq-progress", format!("Tawreed Extractor mapping structural relationships across {} sheets...", sheet_names.len()));

    let mut all_data: Vec<(String, String, Vec<Data>)> = Vec::new(); // (row_id, sheet_name, original_row_data)
    let mut headers_map: HashMap<String, Vec<String>> = HashMap::new();
    let mut markdown_content = String::new();
    
    let mut global_row_id = 1;

    // 1. Extract and convert all sheets to Markdown with Unique IDs
    for sheet_name in &sheet_names {
        if let Ok(range) = excel.worksheet_range(sheet_name) {
            markdown_content.push_str(&format!("## Sheet: {}\n", sheet_name));
            let mut header_found = false;
            
            for (i, row) in range.rows().enumerate() {
                let row_strs: Vec<String> = row.iter().map(|c| match c {
                    Data::String(s) => s.replace("\n", " ").replace("|", " "),
                    Data::Float(f) => f.to_string(),
                    Data::Int(i) => i.to_string(),
                    Data::Bool(b) => b.to_string(),
                    _ => "".to_string(),
                }).collect();

                if row_strs.iter().all(|s| s.trim().is_empty()) { continue; }

                if !header_found {
                    let row_joined = row_strs.join(" ").to_lowercase();
                    let non_empty_count = row_strs.iter().filter(|s| !s.trim().is_empty()).count();
                    let has_keyword = row_joined.contains("كمية") || row_joined.contains("كميه") || row_joined.contains("qty") || 
                                      row_joined.contains("سعر") || row_joined.contains("rate") ||
                                      row_joined.contains("وحدة") || row_joined.contains("وحده") || row_joined.contains("unit") ||
                                      row_joined.contains("اجمالي") || row_joined.contains("total");

                    if non_empty_count >= 3 && has_keyword {
                        header_found = true;
                        headers_map.insert(sheet_name.clone(), row_strs.clone());
                        markdown_content.push_str(&format!("| ID | {} |\n", row_strs.join(" | ")));
                        let mut sep = vec!["---"];
                        sep.extend(vec!["---"; row_strs.len()]);
                        markdown_content.push_str(&format!("| {} |\n", sep.join(" | ")));
                    } else {
                        // Include metadata in markdown for LLM to extract project name / date
                        markdown_content.push_str(&format!("{}\n", row_strs.into_iter().filter(|s| !s.trim().is_empty()).collect::<Vec<_>>().join(": ")));
                    }
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

    let _ = app.emit("boq-progress", format!("Tawreed Extractor compressed {} unique items into token-efficient payload...", global_row_id - 1));
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
        "temperature": 0.0,
        "stream": true
    });

    let _ = app.emit("boq-progress", "Contacting LLM for category mapping...");

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

    let _ = app.emit("boq-progress", "Extracting categories from stream...");

    let mut full_response = String::new();
    let mut reasoning_response = String::new();
    let mut stream_buf = String::new();
    let mut reader = resp;

    while let Some(chunk) = reader.chunk().await.map_err(|e| e.to_string())? {
        let chunk_str = String::from_utf8_lossy(&chunk);
        stream_buf.push_str(&chunk_str);

        while let Some(pos) = stream_buf.find('\n') {
            let line = stream_buf[..pos].to_string();
            stream_buf = stream_buf[pos + 1..].to_string();

            let trimmed = line.trim();
            if trimmed.is_empty() {
                continue;
            }
            if trimmed.starts_with("data: ") {
                let data = &trimmed[6..];
                if data == "[DONE]" {
                    break;
                }
                if let Ok(val) = serde_json::from_str::<Value>(data) {
                    if let Some(choices) = val["choices"].as_array() {
                        if let Some(choice) = choices.get(0) {
                            let content_tok = choice["delta"]["content"].as_str().unwrap_or("");
                            let reasoning_tok = choice["delta"]["reasoning_content"].as_str().unwrap_or("");

                            if !content_tok.is_empty() {
                                full_response.push_str(content_tok);
                                
                                // Determine if token is a thought based on tags
                                let has_start = full_response.contains("<think>");
                                let has_end = full_response.contains("</think>");
                                let is_thought = has_start && !has_end;

                                let _ = app.emit("boq-token", StreamPayload {
                                    token: content_tok.to_string(),
                                    is_thought,
                                });
                            }

                            if !reasoning_tok.is_empty() {
                                reasoning_response.push_str(reasoning_tok);
                                let _ = app.emit("boq-token", StreamPayload {
                                    token: reasoning_tok.to_string(),
                                    is_thought: true,
                                });
                            }
                        }
                    }
                }
            }
        }
    }

    let _ = app.emit("boq-progress", "Tawreed Extractor received response. Verifying semantic mapping...");

    let mut category_map: HashMap<String, String> = HashMap::new();
    let mut project_name: Option<String> = None;
    let mut project_date: Option<String> = None;

    // Robust JSON Extraction to ignore hallucinated markdown or conversational text
    let clean_msg = full_response.trim();
            
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
                        return Err(format!("Tawreed Extractor failed to parse extracted dictionary: {}", json_str));
                    }
                } else {
                    return Err("Tawreed Extractor detected structural anomaly: Malformed JSON boundaries.".into());
                }
            } else {
                return Err("Tawreed Extractor could not find JSON dictionary in the response.".into());
            }

    let _ = app.emit("boq-progress", "Tawreed Extractor reconstructing workbooks and writing final packages...");

    // 3. Reconstruct into categorized Excel
    let mut categorized_data: HashMap<String, Vec<(String, Vec<Data>)>> = HashMap::new();

    for (row_id, sheet_name, row_data) in all_data {
        let category = category_map.get(&row_id).cloned().unwrap_or_else(|| "Uncategorized".to_string());
        categorized_data.entry(category).or_insert_with(Vec::new).push((sheet_name, row_data));
    }

    macro_rules! write_data {
        ($s:expr, $r:expr, $c:expr, $val:expr, $align:expr, $num:expr) => {
            match $val {
                Data::Float(f) => { $s.write_number_with_format($r, $c, *f, $num).map_err(|e| e.to_string())?; },
                Data::Int(i) => { $s.write_number_with_format($r, $c, *i as f64, $num).map_err(|e| e.to_string())?; },
                Data::String(st) => { 
                    if let Ok(num) = st.replace(",", "").parse::<f64>() {
                        $s.write_number_with_format($r, $c, num, $num).map_err(|e| e.to_string())?;
                    } else {
                        $s.write_string_with_format($r, $c, st, $align).map_err(|e| e.to_string())?;
                    }
                },
                Data::Bool(b) => { $s.write_boolean_with_format($r, $c, *b, $align).map_err(|e| e.to_string())?; },
                Data::Empty => { $s.write_string_with_format($r, $c, "", $align).map_err(|e| e.to_string())?; },
                _ => { $s.write_string_with_format($r, $c, "-", $align).map_err(|e| e.to_string())?; },
            }
        }
    }

    let mut workbook = Workbook::new();

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

    let unfilled_format = Format::new()
        .set_font_name("Calibri")
        .set_border(FormatBorder::Thin)
        .set_background_color(Color::RGB(0xFFFF00)) // Bright Yellow
        .set_align(FormatAlign::Top)
        .set_text_wrap();

    // 4.5. Generate Cover Sheet
    let mut cover_sheet = workbook.add_worksheet().set_name("Cover").map_err(|e| e.to_string())?;

    let _ = cover_sheet.set_column_width(0, 30);
    let _ = cover_sheet.set_column_width(1, 50);

    cover_sheet.write_with_format(1, 0, "Application", &header_format).map_err(|e| e.to_string())?;
    cover_sheet.write_with_format(1, 1, "Tawreed Work Package Extractor - Developed by kareemsafwat.com", &string_format).map_err(|e| e.to_string())?;
    
    cover_sheet.write_with_format(3, 0, "Project Name", &header_format).map_err(|e| e.to_string())?;
    if let Some(ref name) = project_name {
        cover_sheet.write_with_format(3, 1, name, &string_format).map_err(|e| e.to_string())?;
    } else {
        cover_sheet.write_with_format(3, 1, "", &unfilled_format).map_err(|e| e.to_string())?;
    }

    cover_sheet.write_with_format(4, 0, "Date", &header_format).map_err(|e| e.to_string())?;
    if let Some(ref date) = project_date {
        cover_sheet.write_with_format(4, 1, date, &string_format).map_err(|e| e.to_string())?;
    } else {
        cover_sheet.write_with_format(4, 1, "", &unfilled_format).map_err(|e| e.to_string())?;
    }

    let mut master_rows_data: Vec<(String, Data, Data, Data, Data, Data)> = Vec::new();

    for (category, rows) in &categorized_data {
        let mut safe_name = category.replace(&['/', '\\', '?', '*', ':', '[', ']'][..], "").chars().take(31).collect::<String>();
        if safe_name.is_empty() { safe_name = "Category".to_string(); }

        let sheet = workbook.add_worksheet().set_name(&format!("Pkg - {}", safe_name).chars().take(31).collect::<String>()).map_err(|e| e.to_string())?;
        
        sheet.set_print_fit_to_pages(1, 0);
        sheet.set_repeat_rows(0, 0).map_err(|e| e.to_string())?;

        let _ = sheet.set_column_width(0, 15); // Number
        let _ = sheet.set_column_width(1, 60); // Description
        let _ = sheet.set_column_width(2, 15); // Unit
        let _ = sheet.set_column_width(3, 15); // Qty
        let _ = sheet.set_column_width(4, 15); // Rate
        let _ = sheet.set_column_width(5, 15); // Amount

        let pkg_headers = ["Number", "Item Description", "Unit", "Quantity", "Rate", "Amount"];
        for (c, val) in pkg_headers.iter().enumerate() {
            sheet.write_with_format(0, c as u16, *val, &header_format).map_err(|e| e.to_string())?;
        }

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
                    
                    let is_desc = lower.contains("بيان") || lower.contains("وصف") || lower.contains("desc") || (lower.contains("بند") && !lower.contains("رقم"));
                    let is_num = (lower.contains("رقم") || lower.contains("no") || lower.contains("item") || lower.contains("مسلسل")) && !is_desc;
                    let is_unit = lower.contains("وحدة") || lower.contains("وحده") || lower.contains("unit");
                    let is_qty = lower.contains("كمية") || lower.contains("كميه") || lower.contains("qty") || lower.contains("quantity");
                    let is_rate = lower.contains("سعر") || lower.contains("فئة") || lower.contains("فئه") || lower.contains("rate") || lower.contains("price");

                    if is_desc { if desc_col.is_none() { desc_col = Some(c); } }
                    else if is_num { if num_col.is_none() { num_col = Some(c); } }
                    else if is_unit { if unit_col.is_none() { unit_col = Some(c); } }
                    else if is_qty { if qty_col.is_none() { qty_col = Some(c); } }
                    else if is_rate { if rate_col.is_none() { rate_col = Some(c); } }
                }
            }

            let mut num_val = Data::Empty;
            if let Some(c) = num_col { if let Some(v) = row.get(c as usize) { num_val = v.clone(); } }
            write_data!(sheet, current_row, 0, &num_val, &center_string_format, &num_format);

            let mut desc_val = Data::Empty;
            if let Some(c) = desc_col { if let Some(v) = row.get(c as usize) { desc_val = v.clone(); } }
            write_data!(sheet, current_row, 1, &desc_val, &string_format, &num_format);

            let mut unit_val = Data::Empty;
            if let Some(c) = unit_col { if let Some(v) = row.get(c as usize) { unit_val = v.clone(); } }
            write_data!(sheet, current_row, 2, &unit_val, &center_string_format, &num_format);

            let mut qty_val = Data::Empty;
            if let Some(c) = qty_col { if let Some(v) = row.get(c as usize) { qty_val = v.clone(); } }
            write_data!(sheet, current_row, 3, &qty_val, &num_format, &num_format);
            let pkg_qty_cell = rust_xlsxwriter::utility::row_col_to_cell(current_row, 3);

            let mut rate_val = Data::Empty;
            if let Some(c) = rate_col { if let Some(v) = row.get(c as usize) { rate_val = v.clone(); } }
            write_data!(sheet, current_row, 4, &rate_val, &num_format, &num_format);
            let pkg_rate_cell = rust_xlsxwriter::utility::row_col_to_cell(current_row, 4);

            sheet.write_formula_with_format(current_row, 5, format!("=IFERROR({}*{}, 0)", pkg_qty_cell, pkg_rate_cell).as_str(), &num_format).map_err(|e| e.to_string())?;

            master_rows_data.push((safe_name.clone(), num_val, desc_val, unit_val, qty_val, rate_val));

            current_row += 1;
        }
        
        if current_row > 1 {
            let table = Table::new();
            sheet.add_table(0, 0, current_row - 1, 5, &table).map_err(|e| e.to_string())?;
        }
    }

    // 5. Master Sheet Setup
    let mut master_sheet = workbook.add_worksheet().set_name("Master").map_err(|e| e.to_string())?;
    master_sheet.set_print_fit_to_pages(1, 0);
    master_sheet.set_repeat_rows(0, 0).map_err(|e| e.to_string())?;

    let _ = master_sheet.set_column_width(0, 15); // Number
    let _ = master_sheet.set_column_width(1, 20); // Package
    let _ = master_sheet.set_column_width(2, 60); // Description
    let _ = master_sheet.set_column_width(3, 15); // Unit
    let _ = master_sheet.set_column_width(4, 15); // Qty
    let _ = master_sheet.set_column_width(5, 15); // Rate
    let _ = master_sheet.set_column_width(6, 15); // Amount

    let master_headers = ["Number", "Package", "Item Description", "Unit", "Quantity", "Rate", "Amount"];
    for (c, val) in master_headers.iter().enumerate() {
        master_sheet.write_with_format(0, c as u16, *val, &header_format).map_err(|e| e.to_string())?;
    }
    
    let mut master_row: u32 = 1;
    for (pkg, num_val, desc_val, unit_val, qty_val, rate_val) in master_rows_data {
        write_data!(master_sheet, master_row, 0, &num_val, &center_string_format, &num_format);
        master_sheet.write_string_with_format(master_row, 1, &pkg, &center_string_format).map_err(|e| e.to_string())?;
        write_data!(master_sheet, master_row, 2, &desc_val, &string_format, &num_format);
        write_data!(master_sheet, master_row, 3, &unit_val, &center_string_format, &num_format);
        write_data!(master_sheet, master_row, 4, &qty_val, &num_format, &num_format);
        write_data!(master_sheet, master_row, 5, &rate_val, &num_format, &num_format);

        let mst_qty_cell = rust_xlsxwriter::utility::row_col_to_cell(master_row, 4);
        let mst_rate_cell = rust_xlsxwriter::utility::row_col_to_cell(master_row, 5);
        master_sheet.write_formula_with_format(master_row, 6, format!("=IFERROR({}*{}, 0)", mst_qty_cell, mst_rate_cell).as_str(), &num_format).map_err(|e| e.to_string())?;

        master_row += 1;
    }
    
    if master_row > 1 {
        let table = Table::new();
        master_sheet.add_table(0, 0, master_row - 1, 6, &table).map_err(|e| e.to_string())?;
    }

    let date_str = chrono::Local::now().format("%Y-%m-%d").to_string();
    let safe_project_name = project_name.as_deref().unwrap_or("Unknown_Project").replace(" ", "_").replace("/", "_");
    let file_name = format!("{}_{}_Work_Packages_Tawreed.xlsx", date_str, safe_project_name);
    let output_dir = crate::system::get_outputs_dir()?;
    let output_path = output_dir.join(&file_name).to_string_lossy().into_owned();

    workbook.save(&output_path).map_err(|e| format!("Failed to save excel: {}", e))?;

    let _ = app.emit("boq-progress", "Tawreed Extractor execution complete. Payload secured.");

    let total_packages = categorized_data.len() as i64;
    Ok((output_path, total_packages))
}
