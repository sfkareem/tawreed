use calamine::{Reader, open_workbook_auto, Data};
use pdfium_render::prelude::*;
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
        let warnings = Vec::new();

        for sheet in workbook.sheet_names() {
            serialized.push(format!("--- Sheet: {} ---", sheet));
            let range = workbook.worksheet_range(&sheet)
                .map_err(|e| format!("Sheet read failure: {}", e))?;

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
        for page in document.pages().iter() {
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

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Write;

    #[test]
    fn test_parse_csv() {
        let dir = tempfile::tempdir().unwrap();
        let file_path = dir.path().join("test.csv");
        let mut file = File::create(&file_path).unwrap();
        writeln!(file, "Material,Quantity,Unit").unwrap();
        writeln!(file, "Concrete,100,m3").unwrap();

        let content = DocumentParser::parse_csv(file_path.to_str().unwrap()).unwrap();
        assert!(content.contains("Concrete"));
    }
}
