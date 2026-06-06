# Centralized Output Directory & File Opening UX Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Store generated Excel work packages in `~/.tawreed/outputs` and expose interactive UI buttons in the Next.js/Tauri frontend to open them directly.

**Architecture:** Update `system.rs` to create the outputs directory and provide its path. Redirect workbook savings in `processor.rs` to this directory. Implement an `open_file` command in `main.rs` calling `tauri_plugin_opener` and invoke it from both the successful generation page and the history record cards in `page.tsx`.

**Tech Stack:** Rust, Tauri v2, tauri-plugin-opener, React, Next.js, Lucide Icons

---

### Task 1: System outputs folder initialization

**Files:**
- Modify: `src-tauri/src/system.rs`

- [x] **Step 1: Update init_tawreed_env to create the outputs folder**
- [x] **Step 2: Add get_outputs_dir helper function**
- [x] **Step 3: Verify with cargo check**

---

### Task 2: Work package extractor redirection

**Files:**
- Modify: `src-tauri/src/processor.rs`

- [x] **Step 1: Redirect extract_work_packages path saving**
- [x] **Step 2: Verify with cargo check**

---

### Task 3: Open file command implementation

**Files:**
- Modify: `src-tauri/src/main.rs`

- [x] **Step 1: Define open_file Tauri Command**
- [x] **Step 2: Register command in Builder**
- [x] **Step 3: Verify with cargo check**

---

### Task 4: Frontend file opening UX and History UI

**Files:**
- Modify: `src/app/page.tsx`

- [x] **Step 1: Add ExternalLink icon to imports**
- [x] **Step 2: Implement handleOpenFile function**
- [x] **Step 3: Save generated file path state on success**
- [x] **Step 4: Update Success Screen to include "Open Work Packages File" button**
- [x] **Step 5: Add Open Button next to history record output path**
- [x] **Step 6: Verify with Next.js compilation and build**
