# BOQ Output Restructure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Completely restructure the exported Excel workbook to feature a Cover Sheet with LLM-extracted metadata, a comprehensive Master Sheet, and individual Package sheets with precise columns and pre-injected formulas.

**Architecture:** We will modify `src-tauri/src/processor.rs` to update the LLM JSON prompt to extract project metadata alongside item categories. Then, we will rewrite the `rust_xlsxwriter` sequence to generate the new Cover Sheet, Master Sheet, and updated Package sheets while applying new Page Setup print behaviors.

**Tech Stack:** Rust, Tauri, `rust_xlsxwriter`, `calamine`, `serde_json`

---

### Task 1: Update LLM Extraction Logic

**Files:**
- Modify: `C:\Users\karee\Desktop\QS Mind\slab-api\src-tauri\src\processor.rs`

- [ ] **Step 1: Update the LLM Prompt**
Modify the prompt in `slice_boq` to request a structured JSON with metadata:
```rust
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
```

- [ ] **Step 2: Update the JSON Parsing Logic**
Create variables for `project_name` and `date` and update the JSON parsing logic to extract them:
```rust
    let mut category_map: HashMap<String, String> = HashMap::new();
    let mut project_name: Option<String> = None;
    let mut project_date: Option<String> = None;

    if let Some(choices) = result["choices"].as_array() {
        if let Some(msg) = choices.get(0).and_then(|c| c["message"]["content"].as_str()) {
            let clean_msg = msg.trim();
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
```

- [ ] **Step 3: Run cargo check to verify types**
Run: `cd "C:\Users\karee\Desktop\QS Mind\slab-api\src-tauri" && cargo check`
Expected: Passes without LLM parsing errors.

- [ ] **Step 4: Commit**
```bash
git add src-tauri/src/processor.rs
git commit -m "feat: upgrade LLM parsing to extract project metadata"
```

---

### Task 2: Excel Formatting & Cover Sheet

**Files:**
- Modify: `C:\Users\karee\Desktop\QS Mind\slab-api\src-tauri\src\processor.rs`

- [ ] **Step 1: Add new Formats**
Add `unfilled_format` below `warning_format`:
```rust
    let unfilled_format = Format::new()
        .set_font_name("Calibri")
        .set_border(FormatBorder::Thin)
        .set_background_color(Color::RGB(0xFFFF00)) // Bright Yellow
        .set_align(FormatAlign::Top)
        .set_text_wrap();
```

- [ ] **Step 2: Generate Cover Sheet**
Right after `let mut workbook = Workbook::new();`, build the Cover Sheet:
```rust
    let mut cover_sheet = workbook.add_worksheet().set_name("Cover").map_err(|e| e.to_string())?;
    cover_sheet.set_right_to_left(true);
    let _ = cover_sheet.set_column_width(0, 30);
    let _ = cover_sheet.set_column_width(1, 50);

    cover_sheet.write_with_format(1, 0, "Application", &header_format).map_err(|e| e.to_string())?;
    cover_sheet.write_with_format(1, 1, "Slab BOQ Slicer - Developed by kareemsafwat.com", &string_format).map_err(|e| e.to_string())?;
    
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
```

- [ ] **Step 3: Commit**
```bash
git add src-tauri/src/processor.rs
git commit -m "feat: implement cover sheet with metadata injection"
```

---

### Task 3: Package Sheets Update

**Files:**
- Modify: `C:\Users\karee\Desktop\QS Mind\slab-api\src-tauri\src\processor.rs`

- [ ] **Step 1: Overhaul Package Logic**
In the `for (category, rows) in &categorized_data` loop, update sheet setup and column headers:
```rust
        let sheet = workbook.add_worksheet().set_name(&format!("Pkg - {}", safe_name)).map_err(|e| e.to_string())?;
        sheet.set_right_to_left(true);
        sheet.fit_to_pages(1, 0);
        let _ = sheet.repeat_rows(0, 0);

        let _ = sheet.set_column_width(0, 15); // Number
        let _ = sheet.set_column_width(1, 60); // Description
        let _ = sheet.set_column_width(2, 15); // Unit
        let _ = sheet.set_column_width(3, 15); // Qty
        let _ = sheet.set_column_width(4, 15); // Rate
        let _ = sheet.set_column_width(5, 15); // Amount

        // Write Header
        let headers = ["Number", "Item Description", "Unit", "Quantity", "Rate", "Amount"];
        for (c, val) in headers.iter().enumerate() {
            sheet.write_with_format(0, c as u16, val, &header_format).map_err(|e| e.to_string())?;
        }
```

- [ ] **Step 2: Update Row Writing in Package Sheets**
Remove the old data matching and strictly write the specific columns. (Assume original description, unit, qty, rate indexes are found via `headers_map` mapping. Wait! The prompt categorizes ID -> Category. The original data might not be cleanly split into exactly Description/Unit/Qty/Rate unless we explicitly find them).

*Wait, `row.iter()` dumps all original columns. If the original columns were random, how do we map them cleanly to "Item Description, Unit, Quantity, Rate, Amount"?*
*We previously found `qty_col`, `rate_col` dynamically. We must find `desc_col` and `unit_col` dynamically too, or assume standard columns.*

```rust
        let first_source = &rows[0].0;
        let mut num_col: Option<u16> = None;
        let mut desc_col: Option<u16> = None;
        let mut unit_col: Option<u16> = None;
        let mut qty_col: Option<u16> = None;
        let mut rate_col: Option<u16> = None;

        if let Some(source_headers) = headers_map.get(first_source) {
            for (col, val) in source_headers.iter().enumerate() {
                let c = col as u16;
                let lower = val.to_lowercase();
                if lower.contains("بند") || lower.contains("رقم") || lower.contains("no") || lower.contains("item") { if num_col.is_none() { num_col = Some(c); } }
                if lower.contains("بيان") || lower.contains("وصف") || lower.contains("desc") { desc_col = Some(c); }
                if lower.contains("وحدة") || lower.contains("unit") { unit_col = Some(c); }
                if lower.contains("كمية") || lower.contains("qty") || lower.contains("quantity") { qty_col = Some(c); }
                if lower.contains("سعر") || lower.contains("فئة") || lower.contains("rate") || lower.contains("price") { rate_col = Some(c); }
            }
        }

        let mut current_row: u32 = 1;
        for (_, row) in rows.iter() {
            // Number
            if let Some(c) = num_col {
                if let Some(val) = row.get(c as usize) {
                    write_val(sheet, current_row, 0, val, &center_string_format, &num_format)?;
                }
            }
            // Description
            if let Some(c) = desc_col {
                if let Some(val) = row.get(c as usize) {
                    write_val(sheet, current_row, 1, val, &string_format, &num_format)?;
                }
            }
            // Unit
            if let Some(c) = unit_col {
                if let Some(val) = row.get(c as usize) {
                    write_val(sheet, current_row, 2, val, &center_string_format, &num_format)?;
                }
            }
            // Qty
            let mut qty_cell = String::new();
            if let Some(c) = qty_col {
                if let Some(val) = row.get(c as usize) {
                    write_val(sheet, current_row, 3, val, &num_format, &num_format)?;
                    qty_cell = rust_xlsxwriter::utility::row_col_to_cell(current_row, 3);
                }
            }
            // Rate
            let mut rate_cell = String::new();
            if let Some(c) = rate_col {
                if let Some(val) = row.get(c as usize) {
                    write_val(sheet, current_row, 4, val, &num_format, &num_format)?;
                    rate_cell = rust_xlsxwriter::utility::row_col_to_cell(current_row, 4);
                }
            }
            
            // Amount Formula
            if !qty_cell.is_empty() && !rate_cell.is_empty() {
                sheet.write_formula_with_format(current_row, 5, format!("={}*{}", qty_cell, rate_cell).as_str(), &num_format).map_err(|e| e.to_string())?;
            }

            current_row += 1;
        }
```
*(Note: Implement a helper `write_val` to handle `Data` types cleanly).*

- [ ] **Step 3: Commit**
```bash
git add src-tauri/src/processor.rs
git commit -m "refactor: implement strict column definitions for package sheets"
```

---

### Task 4: Master Sheet Implementation

**Files:**
- Modify: `C:\Users\karee\Desktop\QS Mind\slab-api\src-tauri\src\processor.rs`

- [ ] **Step 1: Delete Old Master Summary**
Remove the old `category_totals_info` tracking and the old "Master Summary" sheet population logic at the bottom of the file.

- [ ] **Step 2: Build Master Sheet dynamically**
Before looping through `categorized_data`, initialize a `Master` worksheet and apply Page Setup:
```rust
    let mut master_sheet = workbook.add_worksheet().set_name("Master").map_err(|e| e.to_string())?;
    master_sheet.set_right_to_left(true);
    master_sheet.fit_to_pages(1, 0);
    let _ = master_sheet.repeat_rows(0, 0);

    let _ = master_sheet.set_column_width(0, 15); // Number
    let _ = master_sheet.set_column_width(1, 20); // Package
    let _ = master_sheet.set_column_width(2, 60); // Description
    let _ = master_sheet.set_column_width(3, 15); // Unit
    let _ = master_sheet.set_column_width(4, 15); // Qty
    let _ = master_sheet.set_column_width(5, 15); // Rate
    let _ = master_sheet.set_column_width(6, 15); // Amount

    let master_headers = ["Number", "Package", "Item Description", "Unit", "Quantity", "Rate", "Amount"];
    for (c, val) in master_headers.iter().enumerate() {
        master_sheet.write_with_format(0, c as u16, val, &header_format).map_err(|e| e.to_string())?;
    }
    let mut master_row: u32 = 1;
```

- [ ] **Step 3: Populate Master Sheet during Category Loop**
As you loop through `all_data` or `categorized_data` to populate Package Sheets, write the same extracted data directly into `master_sheet` incrementing `master_row`, inserting the `safe_name` into column 1 (Package).

- [ ] **Step 4: Build & Test Tauri**
Run: `npm run tauri build`
Expected: Output `.exe` completes successfully without compiler errors.

- [ ] **Step 5: Commit**
```bash
git add src-tauri/src/processor.rs
git commit -m "feat: replace summary with unified master sheet"
```
