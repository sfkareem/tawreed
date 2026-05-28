# Design Specification: Tawreed (Foundational Build from Scratch)

Tawreed is an AI-powered desktop application designed to extract and process construction materials from Bills of Quantities (BOQs) and procurement documents. This document outlines the clean-slate design for the foundational implementation of the application.

---

## 1. Goal Description
The objective is to rebuild Tawreed from scratch as a lightweight, zero-dependency, local-first Tauri v2 application. This build will focus exclusively on the core features required for a minimal viable product (MVP):
1. **Document Ingestion**: Supporting Excel (.xlsx, .xls), Word (.docx), PDF (.pdf), CSV (.csv), and Images (.png, .jpg) completely offline.
2. **AI Material Extraction**: Fully automated extraction using reqwest HTTP clients to Google Gemini (`gemini-2.0-flash`) and OpenAI (`gpt-4o-mini`).
3. **Structured Takeoff Grid**: Interactive and editable frontend table to review and tweak quantities and units before export.
4. **Professional Excel Export**: High-fidelity zebra-striped Excel generation with Segoe UI typography and basic formula sums.

---

## 2. Technical Stack
* **Backend**: Rust (Tauri v2, Tokio, Calamine, rust_xlsxwriter, pdf-extract, pdfium-render, zip, reqwest)
* **Frontend**: HTML5 + Vanilla CSS (Glassmorphism & Dark theme) + Vanilla JavaScript (ES6 Modules)

---

## 3. Core Component Specifications

### 3.1 Settings Configuration (`src-tauri/src/config.rs`)
* Config is persisted at `~/.tawreed/config.json`.
* Atomic writes using `tempfile` prevent file corruption.
* Standard fields: `api_provider`, `api_key`, `model_name`, `preferred_language`, `theme`.

### 3.2 Ingestion & Document Parsers (`src-tauri/src/parsers.rs`)
* **Excel Reader**: Utilizes `calamine`. Implements vertical forward-fill logic for the first column to retain category/package headings.
* **Word Reader**: Parses `.docx` files by opening them as zip archives, extracting text directly from `word/document.xml` using a simple XML tag-stripping tokenizer.
* **CSV Reader**: Parses comma-separated text into structured row-column arrays.
* **PDF Reader**: Extracts digital text via `pdf-extract`. If character density is low, it renders pages to JPEGs using `pdfium-render` for Vision LLM ingestion.
* **Image Reader**: Reads raw bytes and base64-encodes them.

### 3.3 LLM Client & Prompt Engine (`src-tauri/src/ai_service.rs`)
* Manually builds raw reqwest HTTP POST calls.
* **Gemini**: Targets `/v1beta/models/{model}:generateContent`. Supports image arrays using the native `inlineData` structure.
* **OpenAI**: Targets `/v1/chat/completions`. Supports image inputs via `image_url` data URIs.
* Enforces JSON responses (`response_mime_type: "application/json"` or `"response_format": { "type": "json_object" }`).
* Implements robust JSON shielding: strips markdown blocks and `<think>` reasoning tags, resolving braces to run standard deserialization.

### 3.4 Exporter (`src-tauri/src/exporter.rs`)
* Writes files to disk using `rust_xlsxwriter`.
* Customizes styles (Segoe UI font, orange headers, RTL alignment for Arabic, cell borders, number formatting, and `=SUM` calculation rows).

### 3.5 Frontend GUI (`gui/`)
* **App Shell**: Layout with a sidebar and three tabs:
  1. *Workspace*: Upload dropzone, option controls, console console log, editable table, and Excel export.
  2. *Settings*: API credentials configuration and theme selector.
  3. *About*: Credit details.
* **Theme Styling**: Clean Glassmorphism dark-mode variables, card sweeps, scanning animations, and responsive container columns.

---

## 4. Verification Plan

### Automated Verification
* Unit tests for configuration file loading, saving, and path resolution.
* Unit tests for the ZIP-based Word docx text extractor.
* Integration tests verifying Gemini/OpenAI HTTP request formatting.

### Manual Verification
* Run the application in developer mode: `npm run tauri dev`.
* Verify document uploads and check console prints during AI processing.
* Inspect the generated Excel file structure and formulas in MS Excel.
