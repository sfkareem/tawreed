# Design Specification: Tawreed App Upgrades & Optimization

This design document outlines the architectural changes, optimizations, and new features to be integrated into Tawreed. 

---

## 1. Goal & Context
Tawreed is an AI-powered quantity surveying desktop tool. This upgrade aims to:
- Reduce application startup latency from ~20s to <2s.
- Add an automated update checker that displays release notes and links to GitHub Releases.
- Improve job history accessibility via search and filtering.
- Elevate diagnostics transparency using a JSON syntax highlighter and warning list view.
- Align with professional application publishing and distribution practices.

---

## 2. Technical Design & Architecture

### Section 1: Startup Optimization (Lazy Loading)
- **Problem:** Top-level imports of heavy data engineering libraries (`pandas`, `openpyxl`, `pdfplumber`, `fitz`/PyMuPDF, `python-docx`) block python runtime parsing on launch. In single-file PyInstaller mode, self-extraction of these libraries adds massive disk I/O overhead.
- **Solution:** 
  - Relocate import statements inside functions where they are actually called.
  - In `main.py`, remove heavy imports and launch `webview` instantly.
  - Delay loading heavy parsers/exporters until a document is uploaded and `generate()` is called.

### Section 2: GitHub Update Checker
- **Version Tracking:** Set `APP_VERSION = "0.0.1"` in both `main.py` and `tawreed_backend.py`.
- **API Endpoint:** Safe, asynchronous background requests to the public GitHub API:
  `GET https://api.github.com/repos/sfkareem/tawreed/releases/latest`
- **UI Integration:**
  - On application load, perform a background update check. If `latest_tag > APP_VERSION`, pop up a modal displaying release notes and a button opening the GitHub download link.
  - In **AI Settings**, add an "App Version" section showing the current version along with a **Check for Updates** button to trigger a manual check.

### Section 3: History Search & Filter
- **UI Design:** Add a modern search box (`#history-search`) in the History view right above the job items.
- **Logic:** Filter active jobs in real-time by matching filename, date, or material count. If no jobs match, display a friendly "No matching jobs found" state.

### Section 4: Diagnostics JSON Highlighter & Warning Tab
- **Visual Syntax Highlighting:** Convert raw clean JSON and AI responses into colored HTML text using custom CSS rules.
  - *Colors:* Coral/Rust Orange (keys), Forest Green (strings), Warm Gold (numbers), Slate Blue (booleans/null).
- **Warnings tab:** Parse the warnings list from the extracted JSON and render it as a list of yellow warning alert cards rather than unformatted JSON strings.

---

## 3. Production & Publishing Best Practices
- **CI/CD Build Automation:** Implement a GitHub Actions workflow (`.github/workflows/build.yml`) to automatically compile the standalone executable (`dist/Tawreed.exe`) on tags or pushes to `main`.
- **Release Assets:** Upload the compiled executable as a release asset in GitHub Releases for quick deployment.
- **UPX Compression:** Enable UPX in the spec file to reduce the size of the executable.

---

## 4. Verification Plan

### Manual Verification
1. **Startup Speed Test:** Measure application startup time using python timers in developer mode to ensure the UI renders in <2 seconds.
2. **Update Checker Test:** Modify `APP_VERSION` locally to `0.0.0` and verify the modal triggers automatically on launch, displaying release notes from GitHub.
3. **Filter Test:** Create multiple dummy history logs and type in the search box to check real-time filtering.
4. **Syntax Highlighter Test:** View a completed job's diagnostics and verify that keys, strings, and numbers are colored correctly.
