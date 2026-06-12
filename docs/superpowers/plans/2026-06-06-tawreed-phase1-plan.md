# Tawreed Phase 1: Foundation & Architecture Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Strip out the old Vite/React frontend, initialize a Next.js (Static Export) frontend within the Tauri shell, and implement the Rust SQLite initialization routine for `~/.tawreed`.

**Architecture:** Next.js static export bundled into Tauri. Rust handles app initialization, ensuring `~/.tawreed` hidden folders and `tawreed.db` exist before the UI loads.

**Tech Stack:** Next.js (App Router), Tailwind CSS, Framer Motion, Tauri, Rust, `rusqlite`.

---

### Task 1: Next.js & Tauri Integration Setup

**Files:**
- Modify: `package.json`
- Create/Modify: `next.config.mjs`
- Modify: `src-tauri/tauri.conf.json`

- [ ] **Step 1: Replace Vite with Next.js in package.json**
Run: `npm uninstall vite @vitejs/plugin-react`
Run: `npm install next react react-dom framer-motion lucide-react`
Run: `npm install -D tailwindcss postcss autoprefixer typescript @types/node @types/react @types/react-dom`

Modify `package.json` scripts:
```json
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "tauri": "tauri"
  }
```

- [ ] **Step 2: Configure Next.js for Static Export**
Create `next.config.mjs`:
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  distDir: 'dist',
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
```

- [ ] **Step 3: Update Tauri Config for Next.js**
Modify `src-tauri/tauri.conf.json`:
Change `build.beforeBuildCommand` to `npm run build`.
Ensure `build.distDir` is set to `../dist`.
Ensure `build.devPath` is set to `http://localhost:3000`.

- [ ] **Step 4: Scaffold Next.js App Directory**
Run: `rm -rf src/*`
Create `src/app/layout.tsx`:
```tsx
import './globals.css'
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
```
Create `src/app/page.tsx`:
```tsx
export default function Home() {
  return <h1>Tawreed Workspace</h1>
}
```
Create `src/app/globals.css`:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

- [ ] **Step 5: Run Build to verify Next.js static export**
Run: `npm run build`
Expected: Passes and creates `dist` folder.

- [ ] **Step 6: Commit**
```bash
git add package.json next.config.mjs src-tauri/tauri.conf.json src/
git commit -m "chore: migrate frontend from Vite to Next.js Static Export"
```

---

### Task 2: Rust System Initialization (`~/.tawreed`)

**Files:**
- Modify: `src-tauri/Cargo.toml`
- Create: `src-tauri/src/system.rs`
- Modify: `src-tauri/src/main.rs`

- [ ] **Step 1: Add rusqlite and directories dependencies**
Run: `cd src-tauri && cargo add rusqlite -F bundled && cargo add directories`

- [ ] **Step 2: Create Initialization Logic**
Create `src-tauri/src/system.rs`:
```rust
use std::fs;
use std::path::PathBuf;
use directories::UserDirs;
use rusqlite::{Connection, Result};

pub fn init_tawreed_env() -> Result<PathBuf, String> {
    let user_dirs = UserDirs::new().ok_or("Could not find user home directory")?;
    let tawreed_dir = user_dirs.home_dir().join(".tawreed");
    
    let data_dir = tawreed_dir.join("data");
    let logs_dir = tawreed_dir.join("logs");
    let db_dir = tawreed_dir.join("db");
    
    fs::create_dir_all(&data_dir).map_err(|e| e.to_string())?;
    fs::create_dir_all(&logs_dir).map_err(|e| e.to_string())?;
    fs::create_dir_all(&db_dir).map_err(|e| e.to_string())?;
    
    let db_path = db_dir.join("tawreed.db");
    let conn = Connection::open(&db_path).map_err(|e| e.to_string())?;
    
    conn.execute(
        "CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY,
            api_key TEXT,
            model_id TEXT,
            language TEXT
        )",
        [],
    ).map_err(|e| e.to_string())?;

    conn.execute(
        "CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY,
            timestamp TEXT,
            project_name TEXT,
            packages_count INTEGER,
            output_path TEXT
        )",
        [],
    ).map_err(|e| e.to_string())?;

    Ok(tawreed_dir)
}
```

- [ ] **Step 3: Hook Initialization into Tauri Startup**
Modify `src-tauri/src/main.rs`:
```rust
// Add at the top:
mod system;

// Modify main function:
fn main() {
    // Initialize env
    match system::init_tawreed_env() {
        Ok(path) => println!("Tawreed environment initialized at {:?}", path),
        Err(e) => eprintln!("Failed to initialize Tawreed env: {}", e),
    }

    tauri::Builder::default()
        // inject handlers...
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

- [ ] **Step 4: Run backend to verify compilation and execution**
Run: `cd src-tauri && cargo run`
Expected: App launches, console prints "Tawreed environment initialized at...". `~/.tawreed` folder is created.

- [ ] **Step 5: Commit**
```bash
git add src-tauri/Cargo.toml src-tauri/src/
git commit -m "feat: initialize ~/.tawreed environment and SQLite database"
```
