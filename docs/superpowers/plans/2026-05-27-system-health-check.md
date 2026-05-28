# System Health Check & Downloader Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ingest a premium live diagnostic panel directly into the Tawreed desktop app that checks all system dependencies and settings, offers UAC-approved automatic downloads with real-time progress for missing tools, and validates configurations to ensure a robust setup.

**Architecture:** A Python diagnostic engine checks for Edge, WebView2, latency, file storage permissions, and credentials validity, while a new tab-based HTML5 dashboard renders status cards and interactive progress bars for downloads, communicating via asynchronous callbacks.

**Tech Stack:** Python (Registry query, Requests stream, subprocess), Javascript, HTML5, Vanilla CSS

---

### Task 1: Sidebar Navigation Tab Integration

**Files:**
- Modify: `gui/index.html`

- [ ] **Step 1: Add Navigation Item for System Health**
  Insert the tab selector button inside the `<aside>` navigation bar (around line 25, right before the settings tab):
  ```html
  <button class="nav-item" data-panel="health-panel" id="nav-health">
      <span class="nav-icon">⚡</span>
      <span class="nav-text">System Health</span>
      <span class="status-badge" id="health-badge"></span>
  </button>
  ```
- [ ] **Step 2: Commit**
  ```bash
  git add gui/index.html
  git commit -m "feat(ui): add system health tab to sidebar layout"
  ```

---

### Task 2: Health Check Panel Layout HTML

**Files:**
- Modify: `gui/index.html`

- [ ] **Step 1: Add Health Panel Container**
  Insert the `#health-panel` container inside `<div id="main-content">` (around line 500, right next to other panels):
  ```html
  <!-- System Health Panel -->
  <div id="health-panel" class="content-panel" style="display: none;">
      <div class="panel-header">
          <h2>⚡ System Diagnostics & Readiness</h2>
          <p class="panel-subtitle">Live health status check of dependencies, storage access, and AI endpoints.</p>
      </div>
      
      <!-- Overall Health Index Banner -->
      <div class="health-summary-banner" id="health-summary">
          <div class="summary-icon">🔍</div>
          <div class="summary-details">
              <h3 id="health-summary-title">Scanning System...</h3>
              <p id="health-summary-desc">Analyzing installation parameters and active configurations.</p>
          </div>
      </div>

      <!-- Diagnostic Cards Grid -->
      <div class="health-grid">
          <!-- WebView2 Card -->
          <div class="health-card" id="card-webview2">
              <div class="card-status-indicator"></div>
              <h4>Edge WebView2 Engine</h4>
              <p class="status-value">Checking...</p>
              <p class="status-detail"></p>
          </div>

          <!-- Microsoft Edge Card -->
          <div class="health-card" id="card-edge">
              <div class="card-status-indicator"></div>
              <h4>Microsoft Edge (PDF Renderer)</h4>
              <p class="status-value">Checking...</p>
              <p class="status-detail"></p>
              <div class="health-action-container" style="display: none;">
                  <button id="btn-fix-edge" class="btn btn-primary btn-sm">Fix Automatically</button>
              </div>
              <!-- Download progress layout -->
              <div class="download-progress-container" style="display: none;">
                  <div class="download-progress-meta">
                      <span class="download-speed">0 KB/s</span>
                      <span class="download-percent">0%</span>
                  </div>
                  <div class="download-progress-bar">
                      <div class="download-progress-fill"></div>
                  </div>
              </div>
          </div>

          <!-- Network & Latency Card -->
          <div class="health-card" id="card-network">
              <div class="card-status-indicator"></div>
              <h4>Internet & Latency</h4>
              <p class="status-value">Checking...</p>
              <p class="status-detail"></p>
          </div>

          <!-- Workspace Permissions Card -->
          <div class="health-card" id="card-storage">
              <div class="card-status-indicator"></div>
              <h4>Workspace Privileges</h4>
              <p class="status-value">Checking...</p>
              <p class="status-detail"></p>
          </div>

          <!-- Credentials Config Card -->
          <div class="health-card" id="card-settings">
              <div class="card-status-indicator"></div>
              <h4>Settings & Credentials</h4>
              <p class="status-value">Checking...</p>
              <p class="status-detail"></p>
          </div>
      </div>
  </div>
  ```
- [ ] **Step 2: Commit**
  ```bash
  git add gui/index.html
  git commit -m "feat(ui): add system health dashboard structure and status cards"
  ```

---

### Task 3: CSS Diagnostics Layout & Progress Bar Styling

**Files:**
- Modify: `gui/style.css`

- [ ] **Step 1: Append Style Rules for Health Check Dashboard**
  Append these styles to the end of `gui/style.css`:
  ```css
  /* System Health Styling */
  .health-summary-banner {
      background: rgba(30, 30, 45, 0.6);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 16px;
      display: flex;
      align-items: center;
      gap: 16px;
      margin-bottom: 24px;
      transition: all 0.3s ease;
  }
  .health-summary-banner.healthy {
      border-color: #2ecc71;
      background: rgba(46, 204, 113, 0.05);
  }
  .health-summary-banner.warning {
      border-color: #f1c40f;
      background: rgba(241, 196, 15, 0.05);
  }
  .health-summary-banner.danger {
      border-color: #e74c3c;
      background: rgba(231, 76, 60, 0.05);
  }
  .summary-icon {
      font-size: 28px;
  }
  .summary-details h3 {
      margin: 0 0 4px 0;
      font-size: 16px;
  }
  .summary-details p {
      margin: 0;
      font-size: 12px;
      color: var(--text-muted);
  }
  .health-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 16px;
  }
  .health-card {
      background: rgba(25, 25, 35, 0.4);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 16px;
      position: relative;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      gap: 8px;
  }
  .card-status-indicator {
      width: 4px;
      position: absolute;
      top: 0;
      bottom: 0;
      left: 0;
      background: var(--border-color);
      transition: background 0.3s ease;
  }
  .health-card.healthy .card-status-indicator {
      background: #2ecc71;
  }
  .health-card.warning .card-status-indicator {
      background: #f1c40f;
  }
  .health-card.danger .card-status-indicator {
      background: #e74c3c;
  }
  .health-card h4 {
      margin: 0;
      font-size: 14px;
      color: var(--text-primary);
  }
  .health-card .status-value {
      margin: 0;
      font-size: 18px;
      font-weight: 600;
  }
  .health-card .status-detail {
      margin: 0;
      font-size: 11px;
      color: var(--text-muted);
  }
  .health-action-container {
      margin-top: auto;
      padding-top: 8px;
  }
  .download-progress-container {
      margin-top: auto;
      padding-top: 8px;
      display: flex;
      flex-direction: column;
      gap: 6px;
  }
  .download-progress-meta {
      display: flex;
      justify-content: space-between;
      font-size: 10px;
      color: var(--text-muted);
  }
  .download-progress-bar {
      height: 6px;
      border-radius: 3px;
      background: rgba(255, 255, 255, 0.08);
      overflow: hidden;
  }
  .download-progress-fill {
      height: 100%;
      width: 0%;
      background: linear-gradient(90deg, var(--brand-primary) 0%, var(--brand-secondary) 100%);
      transition: width 0.15s ease-out;
  }
  /* Status Badge in Tab */
  .status-badge {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      display: inline-block;
      margin-left: auto;
      background: transparent;
      transition: all 0.3s ease;
  }
  .status-badge.healthy {
      background: #2ecc71;
  }
  .status-badge.warning {
      background: #f1c40f;
  }
  .status-badge.danger {
      background: #e74c3c;
      animation: pulse-danger 1.5s infinite;
  }
  @keyframes pulse-danger {
      0% { opacity: 0.3; transform: scale(0.9); }
      50% { opacity: 1; transform: scale(1.1); }
      100% { opacity: 0.3; transform: scale(0.9); }
  }
  ```
- [ ] **Step 2: Commit**
  ```bash
  git add gui/style.css
  git commit -m "feat(ui): add dashboard layout styling and progress bar styling"
  ```

---

### Task 4: Diagnostic System Backend Python APIs

**Files:**
- Modify: `main.py`

- [ ] **Step 1: Ingest Python Diagnostic Logic**
  Open `main.py` and add the diagnostic methods inside the `TawreedAPI` class (around line 300, near settings APIs):
  ```python
      def check_system_health(self) -> dict:
          """Performs live system diagnostics on Edge, WebView2, Latency, Storage, and Config Settings."""
          import sys
          import os
          import time
          import requests
          
          health = {
              "webview2": {"status": "healthy", "value": "Unknown", "detail": "Active session rendering interface"},
              "edge": {"status": "danger", "value": "Missing", "detail": "Edge is required to export PDF reports", "path": ""},
              "network": {"status": "danger", "value": "Offline", "detail": "Disconnected from network"},
              "storage": {"status": "danger", "value": "Access Denied", "detail": "Storage access not verified"},
              "settings": {"status": "danger", "value": "Unconfigured", "detail": "Config file schema is empty"}
          }
          
          # 1. WebView2 Registry Check (Windows-specific)
          if sys.platform == "win32":
              import winreg
              try:
                  key_paths = [
                      (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}"),
                      (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}"),
                      (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}")
                  ]
                  version = None
                  for root_key, key_path in key_paths:
                      try:
                          key = winreg.OpenKey(root_key, key_path)
                          version, _ = winreg.QueryValueEx(key, "pv")
                          if version:
                              break
                      except Exception:
                          continue
                  if version:
                      health["webview2"]["value"] = f"Installed (v{version})"
                      health["webview2"]["status"] = "healthy"
                  else:
                      health["webview2"]["value"] = "Installed"
                      health["webview2"]["detail"] = "Active rendering session OK"
                      health["webview2"]["status"] = "healthy"
              except Exception as e:
                  health["webview2"]["detail"] = f"Detection skipped: {e}"
          else:
              health["webview2"]["value"] = "Installed (Non-Windows)"
              health["webview2"]["status"] = "healthy"

          # 2. Microsoft Edge Executable Path Check
          edge_paths = [
              r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
              r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
              os.path.expandvars(r"%LocalAppData%\Microsoft\Edge\Application\msedge.exe")
          ]
          edge_exec = None
          for path in edge_paths:
              if os.path.exists(path):
                  edge_exec = path
                  break
          if not edge_exec:
              try:
                  import winreg
                  key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\msedge.exe")
                  val, _ = winreg.QueryValue(key, None)
                  if val and os.path.exists(val):
                      edge_exec = val
              except Exception:
                  pass
          if edge_exec:
              health["edge"]["status"] = "healthy"
              health["edge"]["value"] = "Installed"
              health["edge"]["detail"] = f"Location: {edge_exec}"
              health["edge"]["path"] = edge_exec
          else:
              health["edge"]["status"] = "danger"
              health["edge"]["value"] = "Missing"
              health["edge"]["detail"] = "Edge is missing. Click Fix Automatically to download."

          # 3. Latency & Network Check
          try:
              start_t = time.perf_counter()
              # Perform head request to google
              res = requests.head("https://www.google.com", timeout=2.0)
              latency = int((time.perf_counter() - start_t) * 1000)
              health["network"]["status"] = "healthy"
              health["network"]["value"] = f"Connected ({latency}ms)"
              health["network"]["detail"] = "Global internet access verified"
          except Exception as e:
              health["network"]["status"] = "danger"
              health["network"]["value"] = "Offline"
              health["network"]["detail"] = f"Check failed: {e}"

          # 4. Storage Write Access Check
          from tawreed_backend import CONFIG_DIR
          try:
              os.makedirs(CONFIG_DIR, exist_ok=True)
              test_file = os.path.join(CONFIG_DIR, ".healthcheck")
              with open(test_file, "w") as f:
                  f.write("OK")
              os.remove(test_file)
              health["storage"]["status"] = "healthy"
              health["storage"]["value"] = "Writable"
              health["storage"]["detail"] = f"Full access: {CONFIG_DIR}"
          except Exception as e:
              health["storage"]["status"] = "danger"
              health["storage"]["value"] = "Read-Only"
              health["storage"]["detail"] = f"Storage lock error: {e}"

          # 5. Config Credentials Schema Validation
          try:
              from tawreed_backend import load_config
              config = load_config()
              provider = config.get("agent_api_provider", "")
              key = config.get("agent_api_key", "")
              if not provider:
                  health["settings"]["status"] = "warning"
                  health["settings"]["value"] = "Unconfigured"
                  health["settings"]["detail"] = "API Provider is not set. Complete onboarding setup."
              elif not key:
                  health["settings"]["status"] = "warning"
                  health["settings"]["value"] = "Key Missing"
                  health["settings"]["detail"] = f"Provider '{provider}' set, but key is empty."
              else:
                  health["settings"]["status"] = "healthy"
                  health["settings"]["value"] = "Configured"
                  health["settings"]["detail"] = f"Credentials set for provider: {provider}"
          except Exception as e:
              health["settings"]["status"] = "danger"
              health["settings"]["value"] = "Invalid"
              health["settings"]["detail"] = f"Settings read error: {e}"
              
          return health
  ```
- [ ] **Step 2: Commit**
  ```bash
  git add main.py
  git commit -m "feat(backend): add check_system_health API method and validation scripts"
  ```

---

### Task 5: Background Downloader Thread and UAC Setup Installer

**Files:**
- Modify: `main.py`

- [ ] **Step 1: Add Downloader Thread Class**
  Open `main.py` and append `EdgeDownloaderThread` and `start_edge_download` implementation details:
  ```python
  import threading
  import requests
  import os
  import subprocess

  class EdgeDownloaderThread(threading.Thread):
      def __init__(self, window):
          super().__init__()
          self.window = window
          self.daemon = True
          self.url = "https://go.microsoft.com/fwlink/?linkid=2108834"  # Official Edge setup bootstrapper
          self.temp_path = os.path.join(os.environ.get("TEMP", "."), "MicrosoftEdgeSetup.exe")

      def run(self):
          try:
              logger.info(f"Starting Microsoft Edge download from {self.url} to {self.temp_path}")
              response = requests.get(self.url, stream=True, timeout=15)
              total_size = int(response.headers.get('content-length', 0))
              bytes_downloaded = 0
              start_time = time.perf_counter()
              
              with open(self.temp_path, "wb") as f:
                  for chunk in response.iter_content(chunk_size=16384):
                      if chunk:
                          f.write(chunk)
                          bytes_downloaded += len(chunk)
                          
                          # Calculate speed & percentage
                          elapsed = time.perf_counter() - start_time
                          speed = bytes_downloaded / elapsed if elapsed > 0 else 0
                          speed_kb = int(speed / 1024)
                          percent = int((bytes_downloaded / total_size) * 100) if total_size > 0 else 0
                          
                          # Send progress updates to frontend via JS
                          js_code = f"if (window.updateDownloadProgress) {{ window.updateDownloadProgress({percent}, {speed_kb}, {bytes_downloaded}, {total_size}); }}"
                          self.window.evaluate_js(js_code)
              
              # Launch Edge installer causing Windows UAC dialog prompts
              logger.info("Download completed. Executing Edge Installer setup.exe")
              js_code = f"if (window.updateDownloadStatus) {{ window.updateDownloadStatus('installing'); }}"
              self.window.evaluate_js(js_code)
              
              # Runs installer and blocks until complete
              process = subprocess.Popen(self.temp_path, shell=True)
              process.wait()
              
              logger.info("Microsoft Edge installation completed.")
              js_code = f"if (window.updateDownloadStatus) {{ window.updateDownloadStatus('completed'); }}"
              self.window.evaluate_js(js_code)
              
          except Exception as e:
              logger.error(f"Failed to install Microsoft Edge: {e}")
              js_error = f"if (window.updateDownloadStatus) {{ window.updateDownloadStatus('error', '{str(e)}'); }}"
              self.window.evaluate_js(js_error)
          finally:
              if os.path.exists(self.temp_path):
                  try:
                      os.remove(self.temp_path)
                  except Exception:
                      pass
  ```
- [ ] **Step 2: Add API download trigger**
  Add the API trigger inside the `TawreedAPI` class (around `check_system_health` in `main.py`):
  ```python
      def start_edge_download(self) -> bool:
          """Triggers Microsoft Edge bootstrapper download in a background daemon thread."""
          try:
              thread = EdgeDownloaderThread(self._window)
              thread.start()
              return True
          except Exception as e:
              logger.error(f"Failed to start downloader thread: {e}")
          return False
  ```
- [ ] **Step 3: Commit**
  ```bash
  git add main.py
  git commit -m "feat(backend): add EdgeDownloaderThread and start_edge_download bridge trigger"
  ```

---

### Task 6: JS Handlers and Live Dashboard Updates

**Files:**
- Modify: `gui/app.js`

- [ ] **Step 1: Wire navigation panel visibility**
  Inside the panel switching event listeners (around lines 90-120), add the hook to run health checks whenever the System Health tab is loaded:
  ```javascript
      // Wire System Health Navigation Tab
      const navHealth = document.getElementById("nav-health");
      const healthPanel = document.getElementById("health-panel");
      
      if (navHealth) {
          navHealth.addEventListener("click", () => {
              // Hide all other panels
              document.querySelectorAll(".content-panel").forEach(p => p.style.display = "none");
              document.querySelectorAll(".nav-item").forEach(item => item.classList.remove("active"));
              
              // Display health check panel
              healthPanel.style.display = "block";
              navHealth.classList.add("active");
              
              // Trigger live system diagnosis check
              runDiagnostics();
          });
      }
  ```
- [ ] **Step 2: Add JS Diagnostics Update logic**
  Implement `runDiagnostics()` and status badge syncing functions inside `gui/app.js`:
  ```javascript
  // Live diagnostic update handlers
  function runDiagnostics() {
      if (!window.pywebview || !window.pywebview.api) return;
      
      window.pywebview.api.check_system_health().then(health => {
          let hasDanger = false;
          let hasWarning = false;
          
          // Update status cards
          for (const key in health) {
              const check = health[key];
              const card = document.getElementById(`card-${key}`);
              if (!card) continue;
              
              // Update CSS class
              card.className = `health-card ${check.status}`;
              
              // Update status text
              const valEl = card.querySelector(".status-value");
              const detailEl = card.querySelector(".status-detail");
              if (valEl) valEl.textContent = check.value;
              if (detailEl) detailEl.textContent = check.detail;
              
              if (check.status === "danger") hasDanger = true;
              if (check.status === "warning") hasWarning = true;
              
              // Specific to Edge
              if (key === "edge") {
                  const fixAction = document.getElementById("btn-fix-edge");
                  const actionContainer = card.querySelector(".health-action-container");
                  if (check.status === "danger") {
                      if (actionContainer) actionContainer.style.display = "block";
                  } else {
                      if (actionContainer) actionContainer.style.display = "none";
                  }
              }
          }
          
          // Update Tab status badge and Summary banner
          const badge = document.getElementById("health-badge");
          const summary = document.getElementById("health-summary");
          const title = document.getElementById("health-summary-title");
          const desc = document.getElementById("health-summary-desc");
          
          if (badge) {
              badge.className = "status-badge";
              if (hasDanger) {
                  badge.classList.add("danger");
              } else if (hasWarning) {
                  badge.classList.add("warning");
              } else {
                  badge.classList.add("healthy");
              }
          }
          
          if (summary && title && desc) {
              summary.className = "health-summary-banner";
              if (hasDanger) {
                  summary.classList.add("danger");
                  title.textContent = "Action Required";
                  desc.textContent = "Critical dependencies are missing. Run fix utilities to resolve them.";
              } else if (hasWarning) {
                  summary.classList.add("warning");
                  title.textContent = "Configuration Warnings";
                  desc.textContent = "Application dependencies are OK, but configurations require attention.";
              } else {
                  summary.classList.add("healthy");
                  title.textContent = "All Systems Healthy";
                  desc.textContent = "Your workspace, runtimes, and connections are running perfectly!";
              }
          }
      });
  }
  ```
- [ ] **Step 3: Define Downloader progress hooks**
  Define the global callback hooks inside `gui/app.js` and wire the "Fix Automatically" button listener:
  ```javascript
  // Set up global callback receivers for Python downloader thread
  window.updateDownloadProgress = function(percent, speed_kb, bytes_downloaded, total_bytes) {
      const edgeCard = document.getElementById("card-edge");
      if (!edgeCard) return;
      
      const progressContainer = edgeCard.querySelector(".download-progress-container");
      const actionContainer = edgeCard.querySelector(".health-action-container");
      const speedEl = edgeCard.querySelector(".download-speed");
      const percentEl = edgeCard.querySelector(".download-percent");
      const progressFill = edgeCard.querySelector(".download-progress-fill");
      
      if (actionContainer) actionContainer.style.display = "none";
      if (progressContainer) progressContainer.style.display = "flex";
      
      if (speedEl) speedEl.textContent = `${speed_kb} KB/s`;
      if (percentEl) percentEl.textContent = `${percent}%`;
      if (progressFill) progressFill.style.width = `${percent}%`;
      
      const valEl = edgeCard.querySelector(".status-value");
      if (valEl) valEl.textContent = `Downloading... (${percent}%)`;
  };

  window.updateDownloadStatus = function(status, errorMsg) {
      const edgeCard = document.getElementById("card-edge");
      if (!edgeCard) return;
      
      const valEl = edgeCard.querySelector(".status-value");
      const detailEl = edgeCard.querySelector(".status-detail");
      const progressContainer = edgeCard.querySelector(".download-progress-container");
      const actionContainer = edgeCard.querySelector(".health-action-container");
      
      if (status === "installing") {
          if (valEl) valEl.textContent = "Installing...";
          if (detailEl) detailEl.textContent = "Running Edge Web Installer. Please approve the UAC permission prompt.";
      } else if (status === "completed") {
          if (progressContainer) progressContainer.style.display = "none";
          if (actionContainer) actionContainer.style.display = "none";
          runDiagnostics();
      } else if (status === "error") {
          if (progressContainer) progressContainer.style.display = "none";
          if (actionContainer) actionContainer.style.display = "block";
          if (valEl) valEl.textContent = "Install Failed";
          if (detailEl) detailEl.textContent = `Error: ${errorMsg}`;
      }
  };

  // Wire download action button event listener
  document.addEventListener("DOMContentLoaded", () => {
      const fixBtn = document.getElementById("btn-fix-edge");
      if (fixBtn) {
          fixBtn.addEventListener("click", () => {
              const confirmInstall = confirm("Tawreed will download and execute Microsoft Edge web installer (~1.5 MB). Do you grant permission to run the installer?");
              if (confirmInstall && window.pywebview && window.pywebview.api) {
                  window.pywebview.api.start_edge_download();
              }
          });
      }
      
      // Auto-run checks on startup delay
      setTimeout(() => {
          runDiagnostics();
          // Periodically run diagnostic checks every 30 seconds
          setInterval(runDiagnostics, 30000);
      }, 1000);
  });
  ```
- [ ] **Step 4: Commit**
  ```bash
  git add gui/app.js
  git commit -m "feat(ui): implement JS logic for runDiagnostics and Edge installer progress callbacks"
  ```
