# Project: Tawreed Python Rewrite

## Architecture
- **GUI Layer**: PySide6 desktop application with modern dark glassmorphic styling, responsive layouts, and auto-scrolling log console.
- **Database Layer**: SQLite database for local persistence of settings, API keys, and project history.
- **AI Processing Layer**: Asynchronous operations using QThread and signals to call OpenAI API with token-by-token streaming, avoiding GUI thread blocks.
- **Excel Processor Layer**: Pandas/openpyxl for reading and writing Excel sheets, extracting work packages and writing categorized BOQ files.

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | M1: Workspace Wipe & Setup | Delete old Rust/Next.js/Tauri files, configure fresh python virtual env with dependencies (PySide6, openai, pandas, openpyxl, pyinstaller). | None | DONE |
| 2 | M2: Database & Core AI Logic | Implement SQLite storage for settings/history and the core async AI client/Excel parsing. | M1 | DONE |
| 3 | M3: PySide6 GUI Implementation | Build the native PySide6 desktop interface (settings, processing tabs, glassmorphic logs). | M2 | DONE |
| 4 | M4: Packaging Setup | Create PyInstaller .spec file and verification build script to generate a standalone .exe. | M3 | IN_PROGRESS |
| 5 | M5: E2E Test & Verification | Construct E2E tests, run validations, and pass Forensic Auditor integrity audit. | M4 | PLANNED |

## Code Layout
- `main.py`: Entry point for launching the PySide6 app.
- `core/`:
  - `core/db.py`: SQLite connection and settings/history operations.
  - `core/ai.py`: OpenAI chat completion, streaming response handling, prompt templates.
  - `core/excel.py`: Excel reading (work package extraction) and writing (categorized output) logic.
- `gui/`:
  - `gui/main_window.py`: Main window container, tabs, and layout.
  - `gui/styles.py`: Glassmorphic style sheets (QSS) and theme colors.
  - `gui/worker.py`: QThread worker thread for running background AI extraction without freezing UI.
- `build_scripts/`:
  - `build_scripts/package.py`: PyInstaller compilation helper.
  - `tawreed.spec`: PyInstaller spec configuration.
