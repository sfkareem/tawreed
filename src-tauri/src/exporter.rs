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
        let worksheet = workbook.add_worksheet();

        if lang == "arabic" {
            worksheet.set_right_to_left(true);
        }

        // Font family is Segoe UI for clean typography.
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

        // Zebra striping alternating row format
        let row_format_alt = Format::new()
            .set_font_name("Segoe UI")
            .set_font_size(10)
            .set_background_color(Color::RGB(0xF2F4F7)) // Light premium gray-blue
            .set_border(FormatBorder::Thin);

        let total_format = Format::new()
            .set_font_name("Segoe UI")
            .set_font_size(10)
            .set_bold()
            .set_border(FormatBorder::Thin)
            .set_background_color(Color::RGB(0xEAEDF1));

        // Write headers
        let headers = vec![
            "Package", "Material Name", "Technical Specs", "Brand",
            "Unit", "Quantity", "Basis", "Confidence", "Remarks"
        ];
        for (col, text) in headers.iter().enumerate() {
            worksheet.write_string_with_format(0, col as u16, *text, &header_format)?;
        }

        let mut row_count = 0;

        // Write data rows
        if let Some(arr) = data.as_array() {
            row_count = arr.len();
            for (row_idx, item) in arr.iter().enumerate() {
                let row = (row_idx + 1) as u32;
                let fmt = if row_idx % 2 == 0 { &row_format } else { &row_format_alt };

                worksheet.write_string_with_format(row, 0, item["package"].as_str().unwrap_or(""), fmt)?;
                worksheet.write_string_with_format(row, 1, item["material_name"].as_str().unwrap_or(""), fmt)?;
                worksheet.write_string_with_format(row, 2, item["technical_specs"].as_str().unwrap_or(""), fmt)?;
                worksheet.write_string_with_format(row, 3, item["brand"].as_str().unwrap_or(""), fmt)?;
                worksheet.write_string_with_format(row, 4, item["unit"].as_str().unwrap_or(""), fmt)?;
                
                let qty = item["quantity"].as_f64().unwrap_or(0.0);
                worksheet.write_number_with_format(row, 5, qty, fmt)?;

                worksheet.write_string_with_format(row, 6, item["basis"].as_str().unwrap_or(""), fmt)?;
                worksheet.write_string_with_format(row, 7, item["confidence"].as_str().unwrap_or(""), fmt)?;
                worksheet.write_string_with_format(row, 8, item["remarks"].as_str().unwrap_or(""), fmt)?;
            }
        }

        // Add =SUM calculation row if there are data rows
        if row_count > 0 {
            let total_row = (row_count + 1) as u32;
            
            // Empty cells styling for the total row
            for col in 0..9 {
                if col == 4 {
                    worksheet.write_string_with_format(total_row, col as u16, "Total", &total_format)?;
                } else if col == 5 {
                    let formula = format!("=SUM(F2:F{})", total_row);
                    worksheet.write_formula_with_format(total_row, col as u16, formula.as_str(), &total_format)?;
                } else {
                    worksheet.write_string_with_format(total_row, col as u16, "", &total_format)?;
                }
            }
        }

        // Set column widths automatically for visual excellence
        worksheet.autofit();

        workbook.save(output_path)?;
        Ok(())
    }
}
