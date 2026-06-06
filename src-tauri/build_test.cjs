const fs = require('fs');
let code = fs.readFileSync('src/processor.rs', 'utf8');
code = code.replace(/app:\s*AppHandle,\r?\n\s*/g, '');
code = code.replace(/use tauri::\{AppHandle, Emitter\};\r?\n/g, '');
code = code.replace(/let _ = app.emit\([^,]+,\s*(.+?)\);/g, 'println!("Progress: {}", $1);');
code = code.replace(/pub async fn slice_boq/g, 'async fn slice_boq');

const mainFn = `
fn main() {
    let file = r#"C:\\Users\\karee\\Desktop\\طلب مقاول لأعمال غرف التفتيش.xlsx"#;
    let base = "https://api.minimax.io/v1";
    let model = "MiniMax-M3";
    let key = "${process.env.TAWREED_API_KEY || ''}";
    
    println!("Starting test runner...");
    tauri::async_runtime::block_on(async {
        match slice_boq(file, base, model, key).await {
            Ok(path) => println!("SUCCESS: {}", path),
            Err(e) => println!("ERROR: {}", e),
        }
    });
}
`;

fs.mkdirSync('src/bin', { recursive: true });
fs.writeFileSync('src/bin/test_boq.rs', mainFn + code);
console.log('Created src/bin/test_boq.rs');
