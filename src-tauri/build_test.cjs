const fs = require('fs');
let code = fs.readFileSync('src/processor.rs', 'utf8');
code = code.replace(/app:\s*AppHandle,[\s\S]*?\r?\n\s*/g, '');
code = code.replace(/use tauri::\{AppHandle,\s*Emitter\};[\s\S]*?\r?\n/g, '');
code = code.replace(/let _ = app\.emit\(\s*"boq-progress"\s*,\s*([\s\S]*?)\);/g, 'println!("Progress: {}", $1);');
code = code.replace(/let _ = app\.emit\(\s*"boq-token"[\s\S]*?\);\r?\n?/g, '');
code = code.replace(/pub async fn extract_work_packages/g, 'async fn extract_work_packages');

const mainFn = `#[path = "../system.rs"]
mod system;

fn main() {
    let file = r#"C:\\Users\\karee\\Desktop\\طلب مقاول لأعمال غرف التفتيش.xlsx"#;
    let base = "https://api.minimax.io/v1";
    let model = "MiniMax-M3";
    let key = "${process.env.TAWREED_API_KEY || ''}";
    
    println!("Starting test runner...");
    tauri::async_runtime::block_on(async {
        match extract_work_packages(file, base, model, key).await {
            Ok((path, count)) => println!("SUCCESS: {} with {} packages", path, count),
            Err(e) => println!("ERROR: {}", e),
        }
    });
}
`;

fs.mkdirSync('src/bin', { recursive: true });
fs.writeFileSync('src/bin/test_boq.rs', mainFn + code);
console.log('Created src/bin/test_boq.rs');
