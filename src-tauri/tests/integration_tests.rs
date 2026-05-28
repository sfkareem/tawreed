use tawreed::config::AppSettings;
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
