# Spec: Tawreed Tauri + Rust Migration & Legacy Codebase Cleanup

**Date:** 2026-05-27  
**Status:** Approved  
**Author:** Antigravity AI  

This specification outlines the architecture, components, dependencies, and migration path for rewriting the **Tawreed** desktop application backend from Python (`pywebview`) to **Tauri v2 + Rust**. It also defines the strategy for removing legacy Python files and assets to leave a clean compiled Rust-Tauri workspace.

---

## 1. Goals & Architectural Overview

### Objectives
1. **Performance & Memory Efficiency:** Replace the bloated Python interpreter and Pandas environment with a compiled Rust executable.
2. **Zero Runtime Dependencies:** Eliminate the requirement for a local Python runtime, virtual environment, and headless MS Edge browser installations on user machines.
3. **Robust Concurrency:** Use the Tokio async runtime to run multi-agent workflows without blocking the GUI or consuming excessive CPU.
4. **Clean Workspace:** Delete all legacy Python scripts (`main.py`, `tawreed_backend.py`, `requirements.txt`, etc.) and PyInstaller bundling configurations (`main.spec`) once compiling and verified.

### Architecture Diagram
```mermaid
graph TD
    subgraph Frontend [Tauri Frontend (HTML/CSS/JS)]
        UI[Wizard UI app.js] -->|invokes| API[Tauri API Command Bridge]
        DOC[mammoth.js] -->|Parses Word to HTML| UI
    end
    
    subgraph Backend [Tauri Backend (Rust)]
        API -->|spawns| JM[Job Manager State]
        JM -->|async future loops| TS[Tokio Task Pool]
        TS -->|Interviews/Prompts| LLM[genai Crate Client]
        TS -->|Ingests Tables| CAL[calamine Crate]
        TS -->|Generates Sheets| XLS[rust_xlsxwriter Crate]
        TS -->|Compiles PDF Reports| TYP[typst Crate]
        TS -->|Renders PDF Pages to Image| PDF[pdfium-render Crate]
        TS -->|Halts / Resumes| CH[oneshot Channels]
    end
    
    LLM -->|API Requests| OpenAI[OpenAI / Gemini / Anthropic]
```

---

## 2. Component Specifications

### 2.1. Frontend Native Tauri Refactoring (`gui/`)
Instead of mocking PyWebView with an adapter, the frontend code will be updated to interface directly with Tauri v2 APIs.
* **Imports:** Use `@tauri-apps/api/core` for `invoke` and `@tauri-apps/api/event` for listening to backend push events.
* **Commands Map:**
  - `pywebview.api.select_file()` ➔ `invoke("select_file")`
  - `pywebview.api.select_output_folder()` ➔ `invoke("select_output_folder")`
  - `pywebview.api.load_settings()` ➔ `invoke("load_settings")`
  - `pywebview.api.save_settings(settings)` ➔ `invoke("save_settings", { settings })`
  - `pywebview.api.generate(file, dir, lang)` ➔ `invoke("generate_job", { filePath: file, outputDir: dir, language: lang })`
  - `pywebview.api.submit_approved_packages(id, pkgs)` ➔ `invoke("submit_approved_packages", { jobId: id, packages: pkgs })`
  - `pywebview.api.submit_warning_resolutions(id, res)` ➔ `invoke("submit_warning_resolutions", { jobId: id, resolutions: res })`
  - `pywebview.api.abort_job(id)` ➔ `invoke("abort_job", { jobId: id })`
  - `pywebview.api.factory_reset()` ➔ `invoke("factory_reset")`
* **Realtime Updates:** Set up `listen('agent-update', (event) => receiveAgentUpdate(event.payload))` to process logs, progress percentages, and checkpoints.

### 2.2. Document Parsing Pipeline
* **Excel Reader (`calamine`):** Ingests uploaded BoQ/cost breakdown spreadsheets. Resolves category cells using a forward-fill algorithm on blank values programmatically.
* **Excel Writer (`rust_xlsxwriter`):** Generates output workbooks containing the dynamic Takeoff sheets, Summary index sheet (with formula counters and internal hyperlinks), Review Flags, Assumptions, and Warnings. Handles standard styling, Segoe UI fonts, gridlines, and RTL for Arabic.
* **Word Reader (`mammoth.js`):** Bound to the frontend File Upload step. When a `.docx` file is selected, it is parsed directly in WebView memory to clean HTML/Markdown text. This eliminates the experimental and unstable `docx-rs` reading crate in Rust.
* **PDF OCR Renderer (`pdfium-render`):** Renders PDF pages to raw JPEG images to be sent to Gemini's AI Vision API.

### 2.3. Asynchronous Multi-Agent Engine
* **Job Sessions:** Spawns async Tokio tasks for each job session.
* **Oneshot Suspension:** The task registry maintains an active map of `oneshot::Sender` channels. When an agent reaches a checkpoint:
  1. It generates the data package.
  2. Emits an `agent-update` event with the checkpoint ID and data.
  3. Creates a new oneshot channel, registers the sender, and yields by awaiting the receiver: `let response = rx.await;`.
  4. The Tauri command `submit_approved_packages` fetches the sender from the registry, transmits the user's choices, and unblocks the execution thread.

### 2.4. LLM API Client (`genai` Crate)
* Interfaces with Gemini, OpenAI, Anthropic, and custom API endpoints under a single unified SDK.
* Handles serialization and deserialization of JSON payloads natively using `serde`.
* Standardizes system prompts, context truncation, and retry mechanics.

### 2.5. Native PDF Export (`typst` Crate)
* Generates printable PDF takeoff reports directly within Rust.
* Replaces the Edge headless browser subprocess.
* Renders layouts using Typst templates compiled directly to binary, removing Edge browser version mismatch issues.

---

## 3. Dependency Specification (Cargo)

The backend Rust application will utilize the following crates in `src-tauri/Cargo.toml`:

| Crate | Version | Purpose |
|---|---|---|
| `tauri` | `^2.0` | Core application container |
| `tauri-plugin-dialog` | `^2.0` | Native file and folder dialogs |
| `tauri-plugin-shell` | `^2.0` | Opening external folders and shells |
| `tokio` | `1.0` | Async runtime, task spawning, and oneshot channels |
| `serde` & `serde_json` | `1.0` | Serialization & deserialization of configs and JSON messages |
| `genai` | `^0.1` | Unified AI SDK (Gemini, OpenAI, Claude) |
| `calamine` | `^0.24` | Excel workbook reader |
| `rust_xlsxwriter` | `^0.64` | Excel workbook writer with styles & formulas |
| `pdfium-render` | `^0.8` | High-fidelity PDF page image rendering |
| `typst` | `^0.11` | Pure-Rust document compilation to PDF |
| `directories-next` | `^2.0` | OS-compliant local settings path discovery |
| `uuid` | `1.0` | Unique job identifiers |
| `log` & `simplelog` | `0.4` | Unified logging to file and console |
| `tempfile` | `3.0` | Atomic config file updates |

---

## 4. Legacy Codebase Cleanup Strategy

To ensure a complete and clean migration, the workspace cleanup will happen in phases:

1. **Scaffolding:** Initialize the Tauri workspace using `npx create-tauri-app` in the repository root.
2. **Implementation:** Migrate frontend events and build all Rust commands/libraries.
3. **Verification:** Validate that the application compiles, builds, and runs perfectly.
4. **Destructive Cleanup:** Permanently delete the following Python-related files:
   - `main.py` (App entry and window creation)
   - `tawreed_backend.py` (Core Python agents and parser logic)
   - `requirements.txt` (Python package list)
   - `main.spec` (PyInstaller specification)
   - `generate_sample_boq.py` (Sample helper)
   - Delete `.venv` (Virtual environment folder)
   - Delete `build/` and `dist/` folders (PyInstaller directories)
5. **Final Commit:** Commit the cleanup to git to keep a lean, 100% Rust-Tauri workspace.

---

## 5. Verification Plan

### Automated Verification
* Run `cargo test` to verify Excel reading (calamine) and writing (rust_xlsxwriter) logic.
* Run `cargo build` to ensure the Rust workspace compiles with zero warnings or errors.
* Validate Typst template compile syntax using test vectors.

### Manual Verification
* Run `cargo tauri dev` to test:
  1. Settings loading/saving and initial onboarding.
  2. Dialog file picking and output directory binding.
  3. Interactive checkpoints (Step 3: packages and warnings inline cards rendering).
  4. Workbook spreadsheet generation and PDF Typst report output.
