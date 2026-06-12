# Tawreed Phase 2: Workspace UI & Engine Upgrades Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the premium, Framer Motion-powered Next.js Workspace screen and upgrade the Rust Excel engine to fix formulas and output correct file names.

**Architecture:** A static Next.js frontend invoking the `process_boq` Tauri command. The Rust backend uses `rust_xlsxwriter` to create dynamic, formula-safe Excel files named dynamically based on the project and current date.

**Tech Stack:** Next.js (App Router), Tailwind CSS, Framer Motion, Tauri, Rust, `rust_xlsxwriter`, `chrono` (for date formatting).

---

### Task 1: Add Rust Date Handling Dependency

**Files:**
- Modify: `src-tauri/Cargo.toml`

- [ ] **Step 1: Add chrono to Cargo.toml**
Run: `cd src-tauri && cargo add chrono`
Expected: `chrono` is added to dependencies.

- [ ] **Step 2: Commit**
```bash
git add src-tauri/Cargo.toml src-tauri/Cargo.lock
git commit -m "chore: add chrono for date formatting"
```

---

### Task 2: Refactor Rust Excel Engine

**Files:**
- Modify: `src-tauri/src/processor.rs`

- [ ] **Step 1: Fix Output File Naming & Value Types**
Modify `slice_boq` in `processor.rs` to implement the correct naming convention and fix `#Value` errors. 

```rust
use chrono::Local;
use std::path::Path;
// Add to the top if not present

// Inside slice_boq function:
// 1. Generate new file name
// Replace the old output_file logic with:
let date_str = Local::now().format("%Y-%m-%d").to_string();
let safe_project_name = project_name.replace(" ", "_").replace("/", "_");
let file_name = format!("{}_{}_Work_Packages_Tawreed.xlsx", date_str, safe_project_name);
let output_dir = std::path::Path::new(&file_path).parent().unwrap_or(std::path::Path::new(""));
let output_file = output_dir.join(&file_name).to_string_lossy().into_owned();

// 2. Fix the `#Value` errors by writing numbers as numbers, not strings.
// When writing rows (e.g., around line 300 depending on exact file state), replace:
// sheet.write_string(row_idx as u32, col_idx as u16, value, &format)
// With a check that attempts to parse as f64 first:
/*
if let Ok(num) = value.parse::<f64>() {
    sheet.write_number(row_idx as u32, col_idx as u16, num, &format).unwrap();
} else {
    sheet.write_string(row_idx as u32, col_idx as u16, value, &format).unwrap();
}
*/
```

- [ ] **Step 2: Run Cargo Check**
Run: `cd src-tauri && cargo check`
Expected: Passes without errors.

- [ ] **Step 3: Commit**
```bash
git add src-tauri/src/processor.rs
git commit -m "fix: implement correct file naming and number typing in excel engine"
```

---

### Task 3: Build Premium Workspace UI

**Files:**
- Modify: `src/app/page.tsx`

- [ ] **Step 1: Replace page.tsx with Framer Motion UI**
Replace the contents of `src/app/page.tsx` with:

```tsx
"use client";

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Upload, FileSpreadsheet, Play, CheckCircle, AlertCircle } from 'lucide-react';
import { invoke } from '@tauri-apps/api/core';
import { open } from '@tauri-apps/plugin-dialog';

export default function Workspace() {
  const [filePath, setFilePath] = useState('');
  const [status, setStatus] = useState<'idle' | 'processing' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');

  const selectFile = async () => {
    try {
      const selected = await open({
        multiple: false,
        filters: [{ name: 'Excel', extensions: ['xlsx', 'xls'] }]
      });
      if (selected && typeof selected === 'string') {
        setFilePath(selected);
        setStatus('idle');
      }
    } catch (err) {
      console.error(err);
    }
  };

  const processFile = async () => {
    if (!filePath) return;
    setStatus('processing');
    try {
      // In reality, API keys and model would be fetched from SQLite/Settings
      const res: string = await invoke('process_boq', {
        filePath,
        baseUrl: 'https://api.minimax.io/v1',
        model: 'MiniMax-M3',
        apiKey: 'sk-cp-ucyiKsDruv0-1ruecr0A-hoHvr9kTQH9WQUTikhd5r_cuAzGnD8aSjF-L2k1rvQ5oBRdqKyfoPSywKqER6dshrlspCmusOzbNhJENwyD40KiIrNE7nWPGwA'
      });
      setMessage(res);
      setStatus('success');
    } catch (err: any) {
      setMessage(err.toString());
      setStatus('error');
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 flex flex-col items-center justify-center p-8">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-2xl w-full bg-slate-900 border border-slate-800 rounded-3xl p-10 shadow-2xl"
      >
        <div className="text-center mb-10">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-indigo-500 bg-clip-text text-transparent mb-4">
            Tawreed Workspace
          </h1>
          <p className="text-slate-400 text-lg">Intelligent BOQ Analysis & Slicing</p>
        </div>

        <div 
          onClick={selectFile}
          className="border-2 border-dashed border-slate-700 hover:border-blue-500 hover:bg-slate-800/50 transition-all rounded-2xl p-12 text-center cursor-pointer mb-8 group"
        >
          <motion.div whileHover={{ scale: 1.05 }} className="flex justify-center mb-4">
            <Upload className="w-12 h-12 text-slate-500 group-hover:text-blue-400 transition-colors" />
          </motion.div>
          {filePath ? (
            <div className="flex items-center justify-center gap-3 text-blue-400 font-medium">
              <FileSpreadsheet className="w-5 h-5" />
              <span className="truncate max-w-xs">{filePath.split('\\').pop() || filePath.split('/').pop()}</span>
            </div>
          ) : (
            <p className="text-slate-400 font-medium text-lg">Click to select BOQ file</p>
          )}
        </div>

        <button
          onClick={processFile}
          disabled={!filePath || status === 'processing'}
          className="w-full bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:hover:bg-blue-600 transition-colors py-4 rounded-xl font-bold text-lg flex justify-center items-center gap-3"
        >
          {status === 'processing' ? (
            <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1, ease: "linear" }}>
              <Play className="w-6 h-6" />
            </motion.div>
          ) : (
            <Play className="w-6 h-6" />
          )}
          {status === 'processing' ? 'Processing Package...' : 'Generate Packages'}
        </button>

        {status === 'success' && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mt-6 p-4 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded-xl flex gap-3">
            <CheckCircle className="w-6 h-6 flex-shrink-0" />
            <p>{message}</p>
          </motion.div>
        )}
        
        {status === 'error' && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mt-6 p-4 bg-rose-500/10 border border-rose-500/20 text-rose-400 rounded-xl flex gap-3">
            <AlertCircle className="w-6 h-6 flex-shrink-0" />
            <p>{message}</p>
          </motion.div>
        )}
      </motion.div>
    </div>
  );
}
```

- [ ] **Step 2: Verify Build**
Run: `npm run build`
Expected: Next.js compiles without errors.

- [ ] **Step 3: Commit**
```bash
git add src/app/page.tsx
git commit -m "feat: implement Framer Motion Workspace UI"
```
