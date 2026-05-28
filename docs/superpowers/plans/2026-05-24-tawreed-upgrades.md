# Tawreed App Upgrades & Optimization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Optimize startup performance, integrate an asynchronous GitHub updater, add a history search filter, and implement a visual JSON syntax highlighter/warnings view.

**Architecture:** Relocate heavy Python module imports inside local scopes. Implement background API updater requests from pywebview to the GitHub Releases API. Apply real-time caching filters in JavaScript for job history, and write a regex syntax highlighter for diagnostic views.

**Tech Stack:** Python 3.10+, PyWebView, JavaScript, Vanilla CSS, HTML5.

---

### Task 1: Backend Lazy Loading (Speed Optimization)

**Files:**
- Modify: [tawreed_backend.py](file:///c:/Users/karee/Desktop/QS%20Mind/tawreed/tawreed_backend.py)

- [ ] **Step 1: Relocate top-level imports to local scopes**
  Remove module-level imports of `pandas`, `openpyxl`, `pdfplumber`, `docx`, `fitz`, `json_repair` and relocate them inside their respective functions.

  **Changes in `tawreed_backend.py`:**
  - Remove lines:
    ```python
    import pandas as pd
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    import pdfplumber
    import docx
    import fitz  # PyMuPDF
    try:
        import json_repair
    except ImportError:
        json_repair = None
    ```
  - Place `import pandas as pd` inside `DocumentParser.parse_excel` and `DocumentParser.parse_csv`.
  - Place `import docx` inside `DocumentParser.parse_word`.
  - Place `import pdfplumber` inside `DocumentParser.parse_digital_pdf`.
  - Place `import fitz` inside `DocumentParser.render_pdf_pages_to_images`.
  - Place imports for `openpyxl`, styles, and utils inside `ExcelExporter.export`.
  - Place local try-except import of `json_repair` inside `JSONRepairService.repair_json` and check `if 'json_repair' in sys.modules:`.

- [ ] **Step 2: Commit backend lazy loading changes**
  ```bash
  git add tawreed_backend.py
  git commit -m "perf: move heavy imports to local functions for lazy loading"
  ```

---

### Task 2: Entrypoint Optimization & App Versioning

**Files:**
- Modify: [main.py](file:///c:/Users/karee/Desktop/QS%20Mind/tawreed/main.py)
- Modify: [tawreed_backend.py](file:///c:/Users/karee/Desktop/QS%20Mind/tawreed/tawreed_backend.py)

- [ ] **Step 1: Set central version constant**
  Define `APP_VERSION = "0.0.1"` at the top level of both `main.py` and `tawreed_backend.py`.

- [ ] **Step 2: Lazy import backend classes in `main.py`**
  Modify imports from `tawreed_backend.py` to import only config and directory constants at module load.
  
  **Changes in `main.py`:**
  - Remove module level import:
    ```python
    from tawreed_backend import (
        load_config,
        save_config,
        JobProcessor,
        AIService,
        CONFIG_DIR,
        LOG_DIR
    )
    ```
  - Replace with:
    ```python
    from tawreed_backend import (
        load_config,
        save_config,
        CONFIG_DIR,
        LOG_DIR,
        APP_VERSION
    )
    ```
  - In `TawreedAPI.test_connection()`, add local import:
    ```python
    from tawreed_backend import AIService
    ```
  - In `TawreedAPI.generate()`, add local import:
    ```python
    from tawreed_backend import JobProcessor
    ```

- [ ] **Step 3: Commit entrypoint optimization**
  ```bash
  git add main.py tawreed_backend.py
  git commit -m "perf: optimize main entrypoint load time and add APP_VERSION"
  ```

---

### Task 3: Backend GitHub Update Checker

**Files:**
- Modify: [main.py](file:///c:/Users/karee/Desktop/QS%20Mind/tawreed/main.py)

- [ ] **Step 1: Implement `check_for_updates` API method**
  Add update checker code inside `TawreedAPI` class to query GitHub API securely and perform semver comparisons.
  
  **Add to `TawreedAPI` class in `main.py`:**
  ```python
  def get_app_version(self) -> str:
      """Returns current application version."""
      return APP_VERSION

  def check_for_updates(self) -> dict:
      """Checks the GitHub repository for updates."""
      import requests
      owner = "sfkareem"
      repo = "tawreed"
      url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
      try:
          response = requests.get(url, timeout=5)
          if response.status_code != 200:
              return {"status": "error", "message": f"GitHub status code {response.status_code}"}
          
          release = response.json()
          latest_tag = release.get("tag_name", "").strip()
          
          # Semver check
          latest_ver = latest_tag.lstrip('v')
          local_ver = APP_VERSION.lstrip('v')
          
          latest_parts = [int(x) for x in latest_ver.split('.') if x.isdigit()]
          local_parts = [int(x) for x in local_ver.split('.') if x.isdigit()]
          
          while len(latest_parts) < 3: latest_parts.append(0)
          while len(local_parts) < 3: local_parts.append(0)
          
          update_available = latest_parts > local_parts
          
          return {
              "status": "success",
              "update_available": update_available,
              "latest_version": latest_tag,
              "current_version": APP_VERSION,
              "release_notes": release.get("body", ""),
              "html_url": release.get("html_url", "")
          }
      except Exception as e:
          return {"status": "error", "message": str(e)}
  ```

- [ ] **Step 2: Commit update checker backend**
  ```bash
  git add main.py
  git commit -m "feat: add check_for_updates backend API wrapper"
  ```

---

### Task 4: Updater Frontend UI & Settings Button

**Files:**
- Modify: [gui/index.html](file:///c:/Users/karee/Desktop/QS%20Mind/tawreed/gui/index.html)
- Modify: [gui/style.css](file:///c:/Users/karee/Desktop/QS%20Mind/tawreed/gui/style.css)
- Modify: [gui/app.js](file:///c:/Users/karee/Desktop/QS%20Mind/tawreed/gui/app.js)

- [ ] **Step 1: Add Update Modal HTML**
  Append update modal layout in `gui/index.html` inside the `<body>`.
  
  ```html
  <!-- Update Notification Modal -->
  <div id="update-modal" class="modal-overlay" style="display:none;">
      <div class="modal-card">
          <div class="modal-header">
              <h3>Update Available 🚀</h3>
              <button id="close-update-modal" class="close-btn">&times;</button>
          </div>
          <div class="modal-body">
              <p>A new version of Tawreed (<strong id="latest-version-text"></strong>) is available. You are currently on <span id="current-version-text"></span>.</p>
              <h4>Release Notes:</h4>
              <div class="release-notes-container">
                  <pre id="release-notes-text"></pre>
              </div>
          </div>
          <div class="modal-footer">
              <button id="update-later-btn" class="btn">Later</button>
              <button id="update-now-btn" class="btn btn-primary">Update Now</button>
          </div>
      </div>
  </div>
  ```

- [ ] **Step 2: Add version layout and button in settings tab**
  Insert App Info card in settings panel in `gui/index.html` under the save settings button.
  
  ```html
  <div class="settings-group" style="margin-top:24px; border-top:1px solid var(--border-color); padding-top:16px;">
      <label>Application Info</label>
      <div style="display: flex; align-items: center; justify-content: space-between; margin-top: 8px;">
          <span style="font-size: 13px; color: var(--text-secondary);">Current Version: <strong id="app-version-display">v0.0.1</strong></span>
          <button id="manual-check-update-btn" class="btn btn-primary" style="padding: 6px 12px; font-size: 12px;">Check for Updates</button>
      </div>
  </div>
  ```

- [ ] **Step 3: Style the Update Modal**
  Add modal overlay and design styles to `gui/style.css`.
  
  ```css
  /* Update Modal overlay & card */
  .modal-overlay {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0, 0, 0, 0.6);
      backdrop-filter: blur(8px);
      display: flex;
      justify-content: center;
      align-items: center;
      z-index: 1000;
  }
  .modal-card {
      background: var(--bg-surface-opaque);
      border: 1px solid var(--border-color);
      border-radius: 16px;
      width: 500px;
      max-width: 90%;
      box-shadow: var(--shadow-premium);
      display: flex;
      flex-direction: column;
      overflow: hidden;
      animation: modalFadeIn 0.3s ease;
  }
  @keyframes modalFadeIn {
      from { transform: scale(0.95); opacity: 0; }
      to { transform: scale(1); opacity: 1; }
  }
  .modal-header {
      padding: 16px 20px;
      border-bottom: 1px solid var(--border-color);
      display: flex;
      justify-content: space-between;
      align-items: center;
  }
  .modal-header h3 {
      margin: 0;
      color: var(--brand-primary);
  }
  .modal-header .close-btn {
      background: none;
      border: none;
      font-size: 24px;
      cursor: pointer;
      color: var(--text-muted);
  }
  .modal-body {
      padding: 20px;
      max-height: 300px;
      overflow-y: auto;
  }
  .release-notes-container {
      background: rgba(0, 0, 0, 0.2);
      border-radius: 8px;
      padding: 12px;
      margin-top: 10px;
      border: 1px solid var(--border-color);
      max-height: 150px;
      overflow-y: auto;
  }
  .release-notes-container pre {
      margin: 0;
      white-space: pre-wrap;
      font-family: 'Consolas', monospace;
      font-size: 12px;
      color: var(--text-secondary);
  }
  .modal-footer {
      padding: 16px 20px;
      border-top: 1px solid var(--border-color);
      display: flex;
      justify-content: flex-end;
      gap: 12px;
  }
  ```

- [ ] **Step 4: Hook up Javascript functions in `gui/app.js`**
  Add the updater call on startup and connect buttons.
  
  **In `gui/app.js`:**
  - Update `initApp()`:
    ```javascript
    async function initApp() {
        setupNavigation();
        setupDropzone();
        setupSettingsEvents();
        setupWorkspaceEvents();
        setupDiagnosticsEvents();
        
        await loadConfig();
        await refreshJobHistory();
        
        // Fetch current version for UI settings display
        const ver = await pywebview.api.get_app_version();
        document.getElementById("app-version-display").innerText = `v${ver}`;
        
        // Asynchronous non-blocking update check on launch
        setTimeout(() => checkForUpdates(true), 1000);
    }
    ```
  - Add updater UI controls:
    ```javascript
    async function checkForUpdates(autoTrigger = true) {
        const updateModal = document.getElementById("update-modal");
        const closeUpdateModal = document.getElementById("close-update-modal");
        const updateLaterBtn = document.getElementById("update-later-btn");
        const updateNowBtn = document.getElementById("update-now-btn");
        
        try {
            const res = await pywebview.api.check_for_updates();
            if (res.status === "success" && res.update_available) {
                document.getElementById("latest-version-text").innerText = res.latest_version;
                document.getElementById("current-version-text").innerText = `v${res.current_version}`;
                document.getElementById("release-notes-text").innerText = res.release_notes || "No release notes available.";
                
                // Show modal
                updateModal.style.display = "flex";
                
                // Bind buttons
                const closeAction = () => { updateModal.style.display = "none"; };
                closeUpdateModal.onclick = closeAction;
                updateLaterBtn.onclick = closeAction;
                
                updateNowBtn.onclick = () => {
                    pywebview.api.open_folder(res.html_url); // Opens GitHub Releases URL in default browser
                    updateModal.style.display = "none";
                };
            } else if (!autoTrigger) {
                showToast("Tawreed is up to date!", "success");
            }
        } catch (e) {
            if (!autoTrigger) {
                showToast("Failed to check for updates.", "error");
            }
        }
    }
    ```
  - In `setupSettingsEvents()`, add trigger:
    ```javascript
    document.getElementById("manual-check-update-btn").addEventListener("click", () => {
        checkForUpdates(false);
    });
    ```

- [ ] **Step 5: Commit Update UI implementation**
  ```bash
  git add gui/index.html gui/style.css gui/app.js
  git commit -m "feat: implement update checker modal UI and manual button"
  ```

---

### Task 5: Job History Search & Filtering

**Files:**
- Modify: [gui/index.html](file:///c:/Users/karee/Desktop/QS%20Mind/tawreed/gui/index.html)
- Modify: [gui/app.js](file:///c:/Users/karee/Desktop/QS%20Mind/tawreed/gui/app.js)

- [ ] **Step 1: Add Search Bar HTML**
  Insert the search input box inside the History tab in `gui/index.html`.
  
  **In `gui/index.html`:**
  - Above `<div id="jobs-list" class="jobs-list">`:
    ```html
    <div class="search-bar-container" style="margin-bottom: 16px; position: relative;">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: var(--text-muted); pointer-events: none;"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
        <input type="text" id="history-search" placeholder="Search past jobs by filename, date, or material count..." style="width: 100%; padding: 12px 16px 12px 40px; border-radius: 8px; font-size: 13px; box-sizing: border-box;">
    </div>
    ```

- [ ] **Step 2: Integrate Filtering Logic in `gui/app.js`**
  Modify `refreshJobHistory()` to support client-side query matching against cache.
  
  **In `gui/app.js`:**
  - Define top-level `let jobHistoryCache = [];`
  - Rewrite `refreshJobHistory()` and bind input filtering:
    ```javascript
    let jobHistoryCache = [];

    async function refreshJobHistory() {
        try {
            // Load cache from backend if not already loaded or on manual tab switch
            jobHistoryCache = await pywebview.api.get_jobs_history();
            renderFilteredHistory();
        } catch (e) {
            showToast("Failed to load jobs history.", "error");
        }
    }

    function renderFilteredHistory() {
        const listContainer = document.getElementById("jobs-list");
        const searchQuery = (document.getElementById("history-search").value || "").toLowerCase().trim();
        listContainer.innerHTML = ""; // Clear
        
        const filtered = jobHistoryCache.filter(job => {
            const dateStr = new Date(job.timestamp).toLocaleString().toLowerCase();
            const filename = job.source_file.split(/[\\/]/).pop().toLowerCase();
            const materialsCount = String(job.summary.total_materials_extracted || 0);
            
            return filename.includes(searchQuery) || 
                   dateStr.includes(searchQuery) || 
                   materialsCount === searchQuery ||
                   (searchQuery.startsWith(">") && parseInt(materialsCount) > parseInt(searchQuery.slice(1))) ||
                   (searchQuery.startsWith("<") && parseInt(materialsCount) < parseInt(searchQuery.slice(1)));
        });

        if (filtered.length === 0) {
            listContainer.innerHTML = `
                <div class="empty-state">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                    <h4>No matching jobs found</h4>
                    <p>Try refining your search query.</p>
                </div>
            `;
            document.getElementById("diagnostics-panel").style.display = "none";
            return;
        }

        filtered.forEach(job => {
            const dateStr = new Date(job.timestamp).toLocaleString();
            const filename = job.source_file.split(/[\\/]/).pop();
            const item = document.createElement("div");
            item.className = "job-item";
            item.setAttribute("data-id", job.job_id);
            
            item.innerHTML = `
                <div class="job-item-left">
                    <span class="job-filename">${filename}</span>
                    <span class="job-date">${dateStr}</span>
                </div>
                <div class="job-item-right">
                    <span class="job-metrics-preview">
                        ${job.summary.total_materials_extracted || 0} Materials | 
                        <span style="color:var(--warning);">${job.flags_count || 0} Flags</span>
                    </span>
                    <span class="job-status-badge">Success</span>
                </div>
            `;
            
            item.addEventListener("click", () => {
                document.querySelectorAll(".job-item").forEach(j => j.classList.remove("selected"));
                item.classList.add("selected");
                loadJobDiagnostics(job.job_id);
            });
            
            listContainer.appendChild(item);
        });
    }

    // Bind real-time input event on DOM load
    document.addEventListener("DOMContentLoaded", () => {
        window.addEventListener('pywebviewready', () => {
            document.getElementById("history-search").addEventListener("input", renderFilteredHistory);
        });
    });
    ```

- [ ] **Step 3: Commit search feature**
  ```bash
  git add gui/index.html gui/app.js
  git commit -m "feat: implement real-time job history search and filter"
  ```

---

### Task 6: Visual JSON syntax Highlighter & Warnings view

**Files:**
- Modify: [gui/index.html](file:///c:/Users/karee/Desktop/QS%20Mind/tawreed/gui/index.html)
- Modify: [gui/style.css](file:///c:/Users/karee/Desktop/QS%20Mind/tawreed/gui/style.css)
- Modify: [gui/app.js](file:///c:/Users/karee/Desktop/QS%20Mind/tawreed/gui/app.js)

- [ ] **Step 1: Add Warnings Tab Button**
  Insert Warnings tab button in diagnostics HTML header inside `gui/index.html`.
  
  ```html
  <button class="tab-btn" data-tab="warnings">Warnings</button>
  ```

- [ ] **Step 2: Add Syntax Highlighting styles to `gui/style.css`**
  ```css
  /* JSON Syntax Highlighting */
  .json-key { color: #d35400; font-weight: bold; }      /* Rust Orange */
  .json-string { color: #27ae60; }                   /* Soft Green */
  .json-number { color: #f39c12; }                   /* Gold/Orange */
  .json-boolean { color: #2980b9; }                  /* Blue */
  .json-null { color: #7f8c8d; font-style: italic; } /* Muted Gray */

  /* Warning Cards Container */
  .warnings-list-container {
      display: flex;
      flex-direction: column;
      gap: 12px;
      padding: 10px;
  }
  .warning-card {
      background: rgba(243, 156, 18, 0.08);
      border-left: 4px solid #f39c12;
      border-radius: 6px;
      padding: 12px 16px;
      display: flex;
      align-items: flex-start;
      gap: 12px;
  }
  .warning-card-title {
      font-weight: bold;
      color: #f39c12;
      margin-bottom: 4px;
      font-size: 13px;
  }
  .warning-card-desc {
      font-size: 12px;
      color: var(--text-secondary);
      line-height: 1.4;
  }
  ```

- [ ] **Step 3: Add `syntaxHighlightJSON` and Warnings view in `gui/app.js`**
  Implement highlighting logic and update `renderDiagTabContent()`.
  
  **In `gui/app.js`:**
  - Add highlighting function:
    ```javascript
    function syntaxHighlightJSON(jsonStr) {
        // Escape HTML
        jsonStr = jsonStr.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
        return jsonStr.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+-]?\d+)?)/g, function (match) {
            let cls = 'number';
            if (/^"/.test(match)) {
                if (/:$/.test(match)) {
                    cls = 'key';
                } else {
                    cls = 'string';
                }
            } else if (/true|false/.test(match)) {
                cls = 'boolean';
            } else if (/null/.test(match)) {
                cls = 'null';
            }
            return '<span class="json-' + cls + '">' + match + '</span>';
        });
    }
    ```
  - Rewrite `renderDiagTabContent()`:
    ```javascript
    function renderDiagTabContent() {
        if (!activeJobDiagnostics) return;
        
        const pre = document.getElementById("diagnostics-text");
        
        // Special case: Warnings Tab
        if (currentDiagTab === "warnings") {
            pre.style.display = "none";
            
            // Check if warning-container exists, if not create
            let container = document.getElementById("warnings-tab-container");
            if (!container) {
                container = document.createElement("div");
                container.id = "warnings-tab-container";
                pre.parentNode.appendChild(container);
            }
            container.style.display = "block";
            container.innerHTML = "";
            
            try {
                const cleanData = JSON.parse(activeJobDiagnostics["extracted_data"]);
                const warnings = cleanData.warnings || [];
                
                if (warnings.length === 0) {
                    container.innerHTML = `
                        <div style="text-align:center; padding:30px; color:var(--text-muted);">
                            <svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="#27ae60" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom:12px;"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
                            <h4 style="color:#27ae60;">No Warnings Found</h4>
                            <p style="font-size:12px; margin-top:4px;">This takeoff job executed successfully with no data anomalies.</p>
                        </div>
                    `;
                } else {
                    const listWrapper = document.createElement("div");
                    listWrapper.className = "warnings-list-container";
                    warnings.forEach((warn, idx) => {
                        const card = document.createElement("div");
                        card.className = "warning-card";
                        card.innerHTML = `
                            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#f39c12" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-top:2px; flex-shrink:0;"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
                            <div>
                                <div class="warning-card-title">Warning #${idx + 1}</div>
                                <div class="warning-card-desc">${warn}</div>
                            </div>
                        `;
                        listWrapper.appendChild(card);
                    });
                    container.appendChild(listWrapper);
                }
            } catch(e) {
                container.innerHTML = `<div style="padding:20px; color:var(--text-muted);">Failed to parse warnings list. View Clean JSON tab instead.</div>`;
            }
            return;
        }
        
        // Restore defaults for non-warnings tabs
        pre.style.display = "block";
        const container = document.getElementById("warnings-tab-container");
        if (container) container.style.display = "none";

        let content = activeJobDiagnostics[currentDiagTab] || "";
        
        if (!content.trim()) {
            pre.innerHTML = "[Empty Log / Not Applicable for this job]";
            return;
        }
        
        // Apply JSON styling
        if (currentDiagTab === "extracted_data" || currentDiagTab === "manifest") {
            try {
                const parsed = JSON.parse(content);
                const pretty = JSON.stringify(parsed, null, 4);
                pre.innerHTML = syntaxHighlightJSON(pretty);
                return;
            } catch(e) {}
        }
        
        // Fallback for regular text
        pre.innerText = content;
    }
    ```

- [ ] **Step 4: Commit Highlighter changes**
  ```bash
  git add gui/index.html gui/style.css gui/app.js
  git commit -m "feat: add JSON syntax highlighting and warnings tab in diagnostics panel"
  ```
