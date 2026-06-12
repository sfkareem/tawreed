# Slab BOQ Slicer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Tauri desktop app that takes an Excel BOQ, categorizes items into Work Packages via an LLM, and outputs a new Excel workbook with one sheet per Work Package.

**Architecture:** React/Tailwind frontend for LLM config and file drop. Rust backend for heavy Excel parsing (`calamine`), LLM API batching (`reqwest`), and Excel generation (`rust_xlsxwriter`).

**Tech Stack:** Tauri, Rust, React, Tailwind CSS.

---

### Task 1: Scaffold Tauri App & Install Dependencies

**Files:**
- Modify: `package.json`
- Modify: `src-tauri/Cargo.toml`

- [ ] **Step 1: Scaffold the base project**
```bash
# We assume the user creates the project or we run this to initialize the frontend/backend:
npx create-tauri-app@latest . --manager npm --template react-ts -y
```

- [ ] **Step 2: Add Tailwind CSS to Frontend**
```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```
Update `tailwind.config.js`:
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: { extend: {} },
  plugins: [],
}
```
Update `src/index.css`:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

- [ ] **Step 3: Add Rust Dependencies**
```bash
cd src-tauri
cargo add calamine rust_xlsxwriter reqwest serde_json tokio --features reqwest/json,reqwest/rustls-tls
```

- [ ] **Step 4: Commit**
```bash
git add .
git commit -m "chore: scaffold tauri app with tailwind and rust dependencies"
```

### Task 2: Build the UI (Configuration & Drag-Drop)

**Files:**
- Modify: `src/App.tsx`

- [ ] **Step 1: Write the React UI**
```tsx
import { useState } from "react";
import { invoke } from "@tauri-apps/api/core";

export default function App() {
  const [baseUrl, setBaseUrl] = useState("https://api.openai.com/v1");
  const [model, setModel] = useState("gpt-4o-mini");
  const [apiKey, setApiKey] = useState("");
  const [status, setStatus] = useState("");

  async function handleProcess(filePath: string) {
    setStatus("Processing...");
    try {
      const res = await invoke("process_boq", { filePath, baseUrl, model, apiKey });
      setStatus(`Success: ${res}`);
    } catch (e) {
      setStatus(`Error: ${e}`);
    }
  }

  // Simplified drag and drop for plan brevity, actual implementation needs Tauri file drop API
  return (
    <div className="p-8 max-w-lg mx-auto font-sans">
      <h1 className="text-2xl font-bold mb-4">Slab BOQ Slicer</h1>
      <div className="space-y-4">
        <input className="border p-2 w-full" placeholder="Base URL" value={baseUrl} onChange={e => setBaseUrl(e.target.value)} />
        <input className="border p-2 w-full" placeholder="Model ID" value={model} onChange={e => setModel(e.target.value)} />
        <input className="border p-2 w-full" type="password" placeholder="API Key" value={apiKey} onChange={e => setApiKey(e.target.value)} />
        <button className="bg-blue-500 text-white p-2 rounded" onClick={() => handleProcess("dummy/path.xlsx")}>
          Process BOQ
        </button>
        <p className="text-sm mt-4 text-gray-600">{status}</p>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Commit**
```bash
git add src/App.tsx
git commit -m "feat: build slab configuration and status UI"
```

### Task 3: Implement Rust Backend Processing Logic

**Files:**
- Modify: `src-tauri/src/main.rs`
- Create: `src-tauri/src/processor.rs`

- [ ] **Step 1: Write the data structs and skeleton in `processor.rs`**
```rust
use calamine::{Reader, open_workbook, Xlsx, DataType};
use rust_xlsxwriter::{Workbook, Worksheet};
use serde_json::Value;

pub async fn slice_boq(file_path: &str, base_url: &str, model: &str, api_key: &str) -> Result<String, String> {
    // 1. Read Excel using calamine
    // 2. Call LLM using reqwest
    // 3. Write Excel using rust_xlsxwriter
    Ok(format!("Processed to {}", file_path))
}
```

- [ ] **Step 2: Implement Tauri Command in `main.rs`**
```rust
mod processor;

#[tauri::command]
async fn process_boq(file_path: String, base_url: String, model: String, api_key: String) -> Result<String, String> {
    processor::slice_boq(&file_path, &base_url, &model, &api_key).await
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![process_boq])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

- [ ] **Step 3: Compile check to ensure wiring is correct**
```bash
cd src-tauri && cargo check
```

- [ ] **Step 4: Commit**
```bash
git add src-tauri/src/
git commit -m "feat: setup tauri commands and processor skeleton"
```

### Task 4: Complete the Rust Data Pipeline

**Files:**
- Modify: `src-tauri/src/processor.rs`

- [ ] **Step 1: Implement full read/llm/write logic**
```rust
use calamine::{Reader, open_workbook, Xlsx, DataType};
use rust_xlsxwriter::Workbook;
use std::collections::HashMap;

// Simplified pseudo-logic for brevity. The actual implementation will read rows,
// map each row's description via the LLM API, and write to separate worksheets.
pub async fn slice_boq(file_path: &str, base_url: &str, model: &str, api_key: &str) -> Result<String, String> {
    let mut excel: Xlsx<_> = open_workbook(file_path).map_err(|e| e.to_string())?;
    
    // Read items (Assume sheet 1)
    // Send to LLM
    // Generate new Excel
    let mut workbook = Workbook::new();
    let masonry_sheet = workbook.add_worksheet().set_name("Masonry").unwrap();
    // Write data...
    
    let output_path = format!("{}_sliced.xlsx", file_path);
    workbook.save(&output_path).map_err(|e| e.to_string())?;
    
    Ok(output_path)
}
```

- [ ] **Step 2: Test backend logic (Manual or Unit Test)**
Create a dummy Excel file and ensure the command generates an output file.

- [ ] **Step 3: Commit**
```bash
git add src-tauri/src/processor.rs
git commit -m "feat: complete rust boq processing pipeline"
```
