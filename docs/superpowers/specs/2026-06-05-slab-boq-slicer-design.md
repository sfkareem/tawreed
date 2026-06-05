# Slab: LLM-Driven BOQ Slicer

## Purpose
A minimal, portable Windows executable (`.exe`) that takes a raw construction Bill of Quantities (BOQ) Excel file, uses an LLM to categorize each item into Work Packages, and outputs a new Excel workbook where **each Work Package is placed on its own dedicated sheet** (e.g., one sheet for Masonry, one sheet for Plaster, etc.).

## Architecture & Tech Stack
- **Framework:** Tauri (React/Tailwind frontend, Rust backend). Ensures a minimal executable size and native performance.
- **Frontend:** React with Tailwind CSS for a modern, clean UI.
- **Backend:** Rust.
  - **Excel Reading:** `calamine` crate.
  - **LLM Integration:** `reqwest` crate to handle batched API calls to any OpenAI-compatible endpoint.
  - **Excel Writing:** `rust_xlsxwriter` crate to generate the output Excel workbook with multiple sheets.

## Core Features & Data Flow
1. **Settings Configuration:** User configures their LLM (Base URL, Model ID, API Key) in the UI.
2. **Input:** User drags and drops a messy BOQ Excel file into the app.
3. **Parsing & Batching:** The Rust backend reads the BOQ, extracting rows. It chunks the data into manageable batches to avoid hitting LLM context limits.
4. **LLM Processing:** The LLM reads the item descriptions and assigns a standardized Work Package to each row.
5. **Output Generation:** Rust groups the original data by the LLM-assigned Work Packages. It then writes a new Excel file, iterating through the groups and creating a separate Excel sheet for each Work Package containing its respective items.

## Error Handling & Edge Cases
- **API Limits:** Implements retry logic for rate limits or API timeouts during batch processing.
- **Uncategorized Items:** Any items the LLM fails to categorize are placed in an "Uncategorized" sheet so no data is lost.
- **Performance:** Asynchronous batching prevents the UI from freezing during the processing of thousands of rows.
