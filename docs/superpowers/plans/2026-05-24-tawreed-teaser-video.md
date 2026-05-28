# Spec: Tawreed Teaser Marketing Video Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a 60-second teaser marketing video for Tawreed using HyperFrames, featuring a professional AI-generated voiceover, synchronized captions, and high-fidelity mockups of Tawreed's UI and themed Excel output.

**Architecture:** A single-page HyperFrames composition that uses a unified GSAP timeline to coordinate visual animations (App workspace transitions, interactive virtual cursor, progress tracking, diagnostic logs, and Excel overlay fly-in) with a pre-recorded Kokoro voiceover track. Captions are dynamically synced using word-level timestamps generated from Whisper transcription.

**Tech Stack:** HTML5, CSS3 (Glassmorphism & Gradients), GSAP (animation timeline), Kokoro (Text-to-Speech), Whisper (transcription/alignment).

---

### Task 1: Generate Narration Audio and Word Timestamps

**Files:**
- Create: `video-teaser/script.txt`
- Create: `video-teaser/assets/voiceover.wav`
- Create: `video-teaser/transcript.json`

- [ ] **Step 1: Write script text**
  Create `video-teaser/script.txt` containing the voiceover paragraphs:
  ```text
  Struggling with messy, unformatted client Bills of Quantities? Scattered text, inconsistent layouts, and broken formulas make cost estimation a slow, manual nightmare.
  Enter Tawreed. Just drag and drop any BOQ, PDF, or scanned sheet. Our AI engine instantly reads, extracts, and organizes materials into structured packages in seconds.
  Get complete transparency under the hood. Review the system instructions, inspect the validated clean JSON, and track real-time repair logs to ensure 100% data integrity.
  The result? A professional, client-ready takeoff workbook. Formatted in Tawreed's signature theme with bilingual columns and clean quantities, ready for your estimating team.
  Stop wasting hours on manual takeoff entries. Build faster, bid smarter. Get started with Tawreed today.
  ```

- [ ] **Step 2: Generate speech audio using Kokoro TTS**
  Run:
  ```bash
  npx hyperframes tts video-teaser/script.txt --voice af_nova --output video-teaser/assets/voiceover.wav
  ```
  Expected: Success output and file generated under `video-teaser/assets/voiceover.wav`.

- [ ] **Step 3: Transcribe audio to get word-level timestamps**
  Run:
  ```bash
  npx hyperframes transcribe video-teaser/assets/voiceover.wav --model small.en
  ```
  Expected: Success output and JSON generated as `video-teaser/assets/voiceover.json` or `video-teaser/transcript.json`. Ensure it is renamed/copied to `video-teaser/transcript.json` with the required structure:
  ```json
  [
    { "id": "w0", "text": "Struggling", "start": 0.0, "end": 0.5 }
  ]
  ```

- [ ] **Step 4: Commit**
  Run:
  ```bash
  git add video-teaser/script.txt video-teaser/assets/voiceover.wav video-teaser/transcript.json
  git commit -m "feat: generate voiceover audio and transcript timestamps"
  ```

---

### Task 2: Video Layout Markup & Base CSS

**Files:**
- Create: `video-teaser/index.html`
- Create: `video-teaser/style.css`

- [ ] **Step 1: Write base HTML markup**
  Create `video-teaser/index.html` referencing scripts, stylesheet, and the audio element:
  ```html
  <!DOCTYPE html>
  <html lang="en">
  <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Tawreed Teaser Video</title>
      <link rel="stylesheet" href="style.css">
  </head>
  <body>
      <!-- Root Composition -->
      <div data-composition-id="tawreed-teaser" data-width="1920" data-height="1080">
          <!-- Audio track index 1 -->
          <audio id="voiceover" data-start="0" data-track-index="1" src="assets/voiceover.wav"></audio>

          <!-- Ambient Background Grid & Glows -->
          <div class="ambient-bg">
              <div class="grid-overlay"></div>
              <div class="glow-orange"></div>
              <div class="glow-yellow"></div>
          </div>

          <!-- Scenes Container -->
          <div class="scenes-viewport">
              <!-- Scene 1: Pain -->
              <div id="scene-pain" class="scene active"></div>
              
              <!-- App Layout (Scene 2, 3, 4) -->
              <div id="app-layout" class="scene">
                  <!-- Sidebar -->
                  <aside>
                      <div class="logo-section">
                          <div class="logo-icon"><img src="assets/icon.png" alt="Tawreed"></div>
                          <div class="logo-text">
                              <h1>Tawreed</h1>
                              <span>Procurement Assistant</span>
                          </div>
                      </div>
                      <nav>
                          <div class="nav-item active" id="nav-workspace">Workspace</div>
                          <div class="nav-item" id="nav-diagnostics">Diagnostics</div>
                      </nav>
                  </aside>
                  
                  <!-- Main Content Panels -->
                  <main>
                      <div id="workspace-panel" class="panel active"></div>
                      <div id="diagnostics-panel" class="panel"></div>
                  </main>
              </div>

              <!-- Scene 4 Overlay: Excel Window -->
              <div id="excel-overlay" class="excel-window-overlay"></div>

              <!-- Scene 5 Outro -->
              <div id="scene-outro" class="scene"></div>
          </div>

          <!-- Subtitle Floating Overlay -->
          <div id="subtitle-bar">
              <span id="subtitle-text"></span>
          </div>

          <!-- Virtual Mouse Cursor -->
          <div id="mouse-cursor">
              <svg viewBox="0 0 24 24" width="36" height="36" fill="white" stroke="black" stroke-width="1.5">
                  <path d="M4 3l14 11-6 1 5 8-3 1.5-5-8.5-5 5z" />
              </svg>
              <div id="click-ripple"></div>
          </div>
      </div>

      <!-- Scripts -->
      <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
      <script src="script.js"></script>
  </body>
  </html>
  ```

- [ ] **Step 2: Write base styling**
  Create `video-teaser/style.css` with dark theme styling, Outfit & Inter fonts, and basic layouts:
  ```css
  @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;700;800&family=Inter:wght@400;500;600;700&display=swap');

  :root {
      --bg-base: #0f0f15;
      --bg-surface: rgba(26, 26, 38, 0.7);
      --border-color: rgba(255, 255, 255, 0.08);
      --brand-primary: #d35400;
      --brand-accent: #f39c12;
      --text-primary: #f5f6fa;
      --text-secondary: #a0a5c1;
      --text-muted: #676b85;
      --font-sans: 'Inter', sans-serif;
      --font-display: 'Outfit', sans-serif;
  }

  * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
  }

  body {
      background: var(--bg-base);
      color: var(--text-primary);
      font-family: var(--font-sans);
      overflow: hidden;
  }

  [data-composition-id="tawreed-teaser"] {
      position: relative;
      width: 1920px;
      height: 1080px;
      background: var(--bg-base);
      overflow: hidden;
  }

  .ambient-bg {
      position: absolute;
      inset: 0;
      z-index: 1;
  }

  .grid-overlay {
      position: absolute;
      inset: 0;
      background-image: radial-gradient(rgba(255,255,255,0.015) 1px, transparent 1px);
      background-size: 40px 40px;
  }

  .glow-orange {
      position: absolute;
      top: 20%;
      left: 15%;
      width: 800px;
      height: 800px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(211, 84, 0, 0.12) 0%, rgba(211, 84, 0, 0) 70%);
      filter: blur(40px);
  }

  .glow-yellow {
      position: absolute;
      bottom: 10%;
      right: 15%;
      width: 800px;
      height: 800px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(243, 156, 18, 0.08) 0%, rgba(243, 156, 18, 0) 70%);
      filter: blur(50px);
  }

  .scenes-viewport {
      position: absolute;
      inset: 0;
      z-index: 2;
  }

  .scene {
      position: absolute;
      inset: 0;
      display: none;
  }

  .scene.active {
      display: flex;
  }
  ```

- [ ] **Step 3: Copy icon asset**
  Copy the existing app icon file:
  `cp icon.png video-teaser/assets/icon.png` (or execute standard OS copy)

- [ ] **Step 4: Commit**
  Run:
  ```bash
  git add video-teaser/index.html video-teaser/style.css
  git commit -m "feat: setup main HTML framework and stylesheet skeleton"
  ```

---

### Task 3: Excel Mockup Sheet Design (Scene 1 & Scene 4)

**Files:**
- Modify: `video-teaser/index.html`
- Modify: `video-teaser/style.css`

- [ ] **Step 1: Write Scene 1 (Pain Sheet) and Scene 4 (Takeoff Sheet) HTML**
  Add mock Excel markup inside `#scene-pain` and `#excel-overlay` in `video-teaser/index.html`:
  ```html
  <!-- Inside #scene-pain -->
  <div class="excel-mockup pain-version">
      <div class="excel-titlebar">
          <span>Microsoft Excel - client_boq_v3_draft.xlsx</span>
      </div>
      <div class="excel-grid">
          <div class="excel-row header-letters"><div></div><div>A</div><div>B</div><div>C</div><div>D</div><div>E</div></div>
          <div class="excel-row"><div>1</div><div class="bold">Item</div><div class="bold">Description</div><div class="bold">Qty</div><div class="bold">Rate</div><div class="bold">Total</div></div>
          <div class="excel-row"><div>2</div><div>1.1</div><div>Porcelain Floor Tiles 60x60</div><div>120.0</div><div class="error-text">#REF!</div><div class="error-text">#REF! <span class="error-badge">⚠ Formula Error</span></div></div>
          <div class="excel-row"><div>3</div><div>1.2</div><div>Solid teak wood skirting 10cm</div><div class="error-text">?</div><div>45.00</div><div class="error-text">#VALUE! <span class="error-badge">⚠ Missing Quantity</span></div></div>
          <div class="excel-row"><div>4</div><div>1.3</div><div>Glazed timber door frame</div><div>4</div><div class="error-text">0.00</div><div class="error-text">#DIV/0! <span class="error-badge">⚠ Div by Zero</span></div></div>
      </div>
  </div>

  <!-- Inside #excel-overlay -->
  <div class="excel-mockup signature-version">
      <div class="excel-titlebar signature-bar">
          <span>Tawreed_Takeoff_BOQ_Final.xlsx - Excel</span>
          <span class="theme-badge">TAWREED SIGNATURE THEME</span>
      </div>
      
      <!-- Summary Sheet View -->
      <div id="excel-sheet-summary" class="excel-sheet active">
          <h2 class="excel-h2">Project Materials Estimation Summary / ملخص تقدير مواد المشروع</h2>
          <table class="excel-table">
              <tr class="table-header"><th>Package Category / باقة المواد</th><th>Item Count / عدد المواد</th><th>Action</th></tr>
              <tr><td class="bold">Fit-out BOQ / جدول كميات التجهيز</td><td class="bold text-green">5</td><td class="link-text">Go to Sheet</td></tr>
              <tr><td class="bold">Finishes / التشطيبات</td><td class="bold text-green">2</td><td class="link-text">Go to Sheet</td></tr>
              <tr class="total-row"><td>Total Extracted Materials / إجمالي المواد</td><td>7</td><td></td></tr>
          </table>
      </div>

      <!-- Fit-out BOQ Sheet View (hidden initially) -->
      <div id="excel-sheet-details" class="excel-sheet">
          <h2 class="excel-h2">Fit-out Takeoff Details / تفاصيل كميات التجهيز</h2>
          <table class="excel-table dense">
              <tr class="table-header"><th>Material (EN) / اسم المادة</th><th>Specification (EN) / المواصفات</th><th>Unit</th><th>Qty</th><th>Unit Rate</th></tr>
              <tr><td>Porcelain Tiles 60x60</td><td>High quality beige tiles</td><td>m2</td><td>120.0</td><td class="input-cell">$0.00</td></tr>
              <tr><td>Teak wood skirting</td><td>Teak wood, satin lacquer</td><td>m</td><td>85.0</td><td class="input-cell">$0.00</td></tr>
              <tr><td>Timber doors 900x2200</td><td>Solid core timber door</td><td>No</td><td>12.0</td><td class="input-cell">$0.00</td></tr>
          </table>
      </div>

      <!-- Excel Sheet Tabs -->
      <div class="excel-tabs">
          <div class="excel-tab active" id="tab-summary">Summary</div>
          <div class="excel-tab" id="tab-details">Fit-out BOQ</div>
      </div>
  </div>
  ```

- [ ] **Step 2: Style Excel mockups**
  Add styles in `video-teaser/style.css` to format these elements:
  ```css
  .excel-mockup {
      width: 1100px;
      background: white;
      border-radius: 12px;
      border: 1px solid rgba(0, 0, 0, 0.15);
      box-shadow: 0 25px 60px rgba(0, 0, 0, 0.4);
      display: flex;
      flex-direction: column;
      overflow: hidden;
      color: #333;
      font-size: 14px;
      font-family: 'Segoe UI', Tahoma, sans-serif;
  }

  .excel-titlebar {
      background: #107c41; /* Excel green */
      padding: 12px 20px;
      color: white;
      font-weight: 600;
      display: flex;
      justify-content: space-between;
      align-items: center;
  }

  .signature-bar {
      background: #d35400; /* Tawreed Orange Excel header */
  }

  .theme-badge {
      background: rgba(255, 255, 255, 0.2);
      font-size: 11px;
      padding: 3px 8px;
      border-radius: 4px;
      font-weight: 700;
  }

  .excel-grid {
      display: flex;
      flex-direction: column;
  }

  .excel-row {
      display: grid;
      grid-template-columns: 40px 100px 300px 80px 100px 1fr;
      border-bottom: 1px solid #e1e1e1;
      height: 36px;
      align-items: center;
  }

  .excel-row.header-letters {
      background: #f3f2f1;
      font-weight: bold;
      color: #666;
      text-align: center;
  }

  .excel-row > div {
      padding: 0 10px;
      border-right: 1px solid #e1e1e1;
      height: 100%;
      display: flex;
      align-items: center;
  }

  .excel-row > div:first-child {
      background: #f3f2f1;
      color: #666;
      justify-content: center;
  }

  .error-text {
      color: #e74c3c;
      font-weight: 600;
      position: relative;
  }

  .error-badge {
      position: absolute;
      left: 100px;
      background: #e74c3c;
      color: white;
      padding: 2px 6px;
      border-radius: 4px;
      font-size: 11px;
      white-space: nowrap;
      border: 1px solid white;
  }

  /* Signature Excel Styling */
  .excel-sheet {
      display: none;
      padding: 24px;
      background: white;
      flex-grow: 1;
      min-height: 400px;
  }

  .excel-sheet.active {
      display: block;
  }

  .excel-h2 {
      font-size: 16px;
      color: #d35400;
      margin-bottom: 16px;
  }

  .excel-table {
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 20px;
  }

  .excel-table th, .excel-table td {
      border: 1px solid #d1d1d1;
      padding: 10px 12px;
      text-align: left;
  }

  .excel-table th {
      background: #d35400;
      color: white;
  }

  .excel-table.dense td {
      padding: 8px 10px;
  }

  .total-row {
      background: #fff8f5;
      font-weight: bold;
      border-bottom: 3px double #333;
  }

  .text-green {
      color: #2ecc71;
  }

  .link-text {
      color: #d35400;
      text-decoration: underline;
      cursor: pointer;
  }

  .input-cell {
      color: #0000ff;
      font-weight: bold;
      background: #f5f8ff;
  }

  .excel-tabs {
      background: #f3f2f1;
      border-top: 1px solid #d1d1d1;
      display: flex;
      padding-left: 20px;
  }

  .excel-tab {
      padding: 10px 20px;
      border-right: 1px solid #d1d1d1;
      cursor: pointer;
      font-weight: 500;
      background: #e1dfdd;
  }

  .excel-tab.active {
      background: white;
      font-weight: 600;
      border-bottom: 2px solid #d35400;
  }
  ```

- [ ] **Step 3: Commit**
  Run:
  ```bash
  git add video-teaser/index.html video-teaser/style.css
  git commit -m "feat: design mockups for plain Excel sheet and signature Excel takeoff outputs"
  ```

---

### Task 4: Interactive UI Mockups (Scene 2 & Scene 3)

**Files:**
- Modify: `video-teaser/index.html`
- Modify: `video-teaser/style.css`

- [ ] **Step 1: Write HTML components for Ingestion (Workspace) and Diagnostics views**
  Inside `video-teaser/index.html`, add workspace panel structure and diagnostics panel structure:
  ```html
  <!-- Inside #workspace-panel -->
  <div class="workspace-grid-layout">
      <!-- Left Card: Ingestion progress -->
      <div class="glass-card left-ingest-card">
          <!-- Dropzone -->
          <div id="mock-dropzone" class="mock-dropzone">
              <svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                  <polyline points="17 8 12 3 7 8" />
                  <line x1="12" y1="3" x2="12" y2="15" />
              </svg>
              <h3>Click to select project file</h3>
              <p>Drag and drop BOQ file here</p>
          </div>
          <!-- Uploaded file box -->
          <div id="mock-file-box" class="mock-file-box" style="display:none;">
              <span class="file-name">sample_boq.xlsx</span>
              <span class="file-path">C:\Users\karee\Desktop\QS Mind\tawreed\sample_boq.xlsx</span>
          </div>
          <!-- Extraction Progress -->
          <div id="mock-progress-container" class="mock-progress" style="display:none;">
              <div class="progress-details">
                  <span id="progress-step-title">Querying AI Extractor...</span>
                  <span id="progress-step-percent">0%</span>
              </div>
              <div class="progress-bar-track">
                  <div id="progress-bar-fill" class="progress-bar-fill-bar"></div>
              </div>
              <div class="progress-checklist">
                  <div class="check-item" id="chk-1">Reading files</div>
                  <div class="check-item" id="chk-2">Extracting materials</div>
                  <div class="check-item" id="chk-3">Validating JSON structure</div>
                  <div class="check-item" id="chk-4">Formatting signature workbook</div>
              </div>
          </div>
          <!-- Success State -->
          <div id="mock-success-card" class="mock-success-details" style="display:none;">
              <span class="success-title">Materials Extracted Successfully!</span>
              <div class="success-stats">
                  <div><span>7</span><span>Materials</span></div>
                  <div><span>2</span><span>Packages</span></div>
                  <div><span class="warning-text">1</span><span>Review Flags</span></div>
              </div>
              <button class="primary-btn" id="btn-open-excel">Open Excel File</button>
          </div>
      </div>

      <!-- Right Card: Params -->
      <div class="glass-card right-params-card">
          <h3>Job Parameters</h3>
          <div class="form-group">
              <label>Output Language</label>
              <select disabled><option>Bilingual (EN/AR) / ثنائي اللغة</option></select>
          </div>
          <div class="form-group">
              <label>Output Directory</label>
              <input type="text" value="C:\Users\karee\.tawreed" readonly>
          </div>
          <button class="primary-btn block-btn" id="btn-start-extraction" disabled>Start Extraction Job</button>
      </div>
  </div>

  <!-- Inside #diagnostics-panel -->
  <div class="diagnostics-grid-layout">
      <!-- Left side: Job history list -->
      <div class="glass-card job-history-card">
          <h3>Past Jobs</h3>
          <div class="job-list-item active">
              <div><strong>sample_boq.xlsx</strong><br><small>2026-05-24 07:11:42</small></div>
              <span class="badge success-badge">Success</span>
          </div>
      </div>

      <!-- Right side: Diagnostics tab outputs -->
      <div class="glass-card diagnostics-details-card">
          <div class="diag-header">
              <h3>Job Diagnostics: job_4d89a71b</h3>
          </div>
          <div class="diag-tabs">
              <button class="diag-tab active" id="tab-prompt">System Prompt</button>
              <button class="diag-tab" id="tab-json">Clean JSON</button>
              <button class="diag-tab" id="tab-logs">Repair Logs</button>
          </div>
          <div class="diag-console-container">
              <pre id="diag-console-text"></pre>
          </div>
      </div>
  </div>
  ```

- [ ] **Step 2: Style UI Panels**
  Add styles to `video-teaser/style.css`:
  ```css
  #app-layout {
      width: 100%;
      height: 100%;
  }

  aside {
      width: 280px;
      background: rgba(18, 18, 26, 0.95);
      border-right: 1px solid var(--border-color);
      padding: 32px 20px;
      display: flex;
      flex-direction: column;
      gap: 40px;
  }

  .logo-section {
      display: flex;
      align-items: center;
      gap: 12px;
  }

  .logo-icon {
      width: 44px;
      height: 44px;
      border-radius: 10px;
      background: linear-gradient(135deg, var(--brand-primary), var(--brand-accent));
      display: flex;
      align-items: center;
      justify-content: center;
  }

  .logo-icon img {
      width: 80%;
      height: 80%;
      object-fit: contain;
  }

  .logo-text h1 {
      font-family: var(--font-display);
      font-size: 22px;
      background: linear-gradient(to right, #ffffff, var(--brand-primary));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
  }

  .logo-text span {
      font-size: 11px;
      color: var(--text-muted);
  }

  nav {
      display: flex;
      flex-direction: column;
      gap: 8px;
  }

  .nav-item {
      padding: 12px 16px;
      border-radius: 8px;
      color: var(--text-secondary);
      font-weight: 600;
  }

  .nav-item.active {
      background: linear-gradient(90deg, rgba(211, 84, 0, 0.15), rgba(211, 84, 0, 0.02));
      border-left: 3px solid var(--brand-primary);
      color: white;
  }

  main {
      flex-grow: 1;
      padding: 48px;
      display: flex;
      flex-direction: column;
      overflow: hidden;
  }

  .panel {
      display: none;
      width: 100%;
      height: 100%;
      flex-direction: column;
  }

  .panel.active {
      display: flex;
  }

  .glass-card {
      background: var(--bg-surface);
      backdrop-filter: blur(12px);
      border: 1px solid var(--border-color);
      border-radius: 16px;
      padding: 28px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  }

  .workspace-grid-layout, .diagnostics-grid-layout {
      display: grid;
      grid-template-columns: 1.4fr 1fr;
      gap: 28px;
      align-items: start;
      width: 100%;
  }

  .diagnostics-grid-layout {
      grid-template-columns: 1fr 2fr;
  }

  /* Dropzone, File Box, Progress, Buttons */
  .mock-dropzone {
      border: 2px dashed rgba(255, 255, 255, 0.15);
      border-radius: 12px;
      padding: 60px 20px;
      text-align: center;
      color: var(--text-secondary);
  }

  .mock-file-box {
      background: rgba(255,255,255,0.03);
      padding: 16px;
      border-radius: 12px;
      border: 1px solid var(--border-color);
  }

  .mock-progress {
      display: flex;
      flex-direction: column;
      gap: 16px;
  }

  .progress-details {
      display: flex;
      justify-content: space-between;
  }

  .progress-bar-track {
      height: 6px;
      background: rgba(255,255,255,0.05);
      border-radius: 3px;
      overflow: hidden;
  }

  .progress-bar-fill-bar {
      height: 100%;
      width: 0%;
      background: linear-gradient(90deg, var(--brand-primary), var(--brand-accent));
      border-radius: 3px;
  }

  .progress-checklist {
      display: flex;
      flex-direction: column;
      gap: 8px;
  }

  .check-item {
      color: var(--text-muted);
      font-size: 13px;
  }

  .check-item.active {
      color: var(--brand-primary);
  }

  .check-item.completed {
      color: #2ecc71;
  }

  .primary-btn {
      background: linear-gradient(135deg, var(--brand-primary), var(--brand-primary));
      color: white;
      font-weight: bold;
      border: none;
      border-radius: 8px;
      padding: 14px 20px;
      cursor: pointer;
  }

  .primary-btn.block-btn {
      width: 100%;
  }

  /* Diags, Console, Virtual Cursor */
  .diag-tabs {
      display: flex;
      gap: 8px;
      background: rgba(0,0,0,0.2);
      padding: 4px;
      border-radius: 8px;
      margin-bottom: 16px;
  }

  .diag-tab {
      background: transparent;
      color: var(--text-secondary);
      border: none;
      padding: 8px 16px;
      border-radius: 6px;
      font-weight: 600;
  }

  .diag-tab.active {
      background: var(--brand-primary);
      color: white;
  }

  .diag-console-container {
      background: #07070a;
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 16px;
      height: 280px;
      overflow-y: auto;
  }

  #diag-console-text {
      font-family: 'Courier New', Courier, monospace;
      color: #a0a5c1;
      font-size: 13px;
      white-space: pre-wrap;
  }

  #mouse-cursor {
      position: absolute;
      z-index: 9999;
      pointer-events: none;
      transform: translate(0, 0);
  }

  #click-ripple {
      position: absolute;
      left: 0;
      top: 0;
      width: 30px;
      height: 30px;
      border-radius: 50%;
      border: 3px solid var(--brand-primary);
      transform: translate(-50%, -50%) scale(0);
      opacity: 0;
  }
  ```

- [ ] **Step 3: Commit**
  Run:
  ```bash
  git add video-teaser/index.html video-teaser/style.css
  git commit -m "feat: design ingestion panels, diagnostics tab containers, and mouse pointer layout"
  ```

---

### Task 5: Narration Subtitles Overlay

**Files:**
- Modify: `video-teaser/index.html`
- Modify: `video-teaser/style.css`
- Modify: `video-teaser/script.js`

- [ ] **Step 1: Style Subtitle bar**
  Add subtitle style specifications in `video-teaser/style.css`:
  ```css
  #subtitle-bar {
      position: absolute;
      bottom: 80px;
      left: 50%;
      transform: translateX(-50%);
      background: rgba(15, 15, 21, 0.85);
      backdrop-filter: blur(10px);
      border: 1px solid var(--border-color);
      border-radius: 16px;
      padding: 16px 36px;
      max-width: 80%;
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
      text-align: center;
      z-index: 1000;
  }

  #subtitle-text {
      font-family: var(--font-display);
      font-size: 32px;
      font-weight: 500;
      color: #f5f6fa;
      letter-spacing: 0.2px;
  }

  .highlight-word {
      color: var(--brand-primary);
      font-weight: 700;
      border-bottom: 2px solid var(--brand-primary);
  }
  ```

- [ ] **Step 2: Add script.js structure & sync subtitles to frames**
  Create `video-teaser/script.js` and implement dynamic subtitle updating driven by transcription data:
  ```javascript
  // Load transcription word data
  let transcripts = [];

  fetch('transcript.json')
      .then(r => r.json())
      .then(data => {
          transcripts = data;
          initCaptionTracking();
      });

  function initCaptionTracking() {
      // Monitor timeline updates
      const rootTl = window.__timelines["tawreed-teaser"];
      if (rootTl) {
          rootTl.eventCallback("onUpdate", updateCaptions);
      }
  }

  function updateCaptions() {
      const rootTl = window.__timelines["tawreed-teaser"];
      const currentTime = rootTl.time(); // Current playing seconds
      
      // Find current active words within time ranges
      // Group words into sentences based on timing breaks
      const activeWords = transcripts.filter(w => currentTime >= w.start && currentTime <= w.end);
      
      // Render subtitles text dynamically highlighting current words
      let htmlString = "";
      transcripts.forEach(w => {
          // Check if word falls in active window
          if (currentTime >= w.start - 1.5 && currentTime <= w.end + 1.5) {
              const isActive = currentTime >= w.start && currentTime <= w.end;
              htmlString += `<span class="${isActive ? 'highlight-word' : ''}">${w.text} </span>`;
          }
      });
      document.getElementById("subtitle-text").innerHTML = htmlString;
  }
  ```

- [ ] **Step 3: Commit**
  Run:
  ```bash
  git add video-teaser/script.js video-teaser/style.css
  git commit -m "feat: implement synced subtitles with word highlighting support"
  ```

---

### Task 6: GSAP Timeline Motion & Transitions Animation

**Files:**
- Modify: `video-teaser/index.html`
- Modify: `video-teaser/style.css`
- Modify: `video-teaser/script.js`

- [ ] **Step 1: Write Scene 5 (Outro) HTML**
  Add Outro elements in `video-teaser/index.html` inside `#scene-outro`:
  ```html
  <!-- Inside #scene-outro -->
  <div class="outro-content">
      <div class="outro-logo-glow"></div>
      <div class="outro-logo-card">
          <img src="assets/icon.png" alt="Tawreed" id="outro-logo">
      </div>
      <h2 id="outro-tagline">Build Faster, Bid Smarter</h2>
      <p id="outro-subtext">AI-powered construction procurement starts here.</p>
      <div id="outro-cta">
          <div class="cta-button">Start Your Free Trial</div>
          <span class="cta-url">github.com/sfkareem/tawreed</span>
      </div>
  </div>
  ```

- [ ] **Step 2: Add Outro styles**
  Add outro styling in `video-teaser/style.css`:
  ```css
  .outro-content {
      margin: auto;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 36px;
      text-align: center;
      position: relative;
  }

  .outro-logo-card {
      width: 120px;
      height: 120px;
      border-radius: 28px;
      background: linear-gradient(135deg, var(--brand-primary), var(--brand-accent));
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 0 35px rgba(211, 84, 0, 0.4);
  }

  .outro-logo-card img {
      width: 80px;
      height: 80px;
  }

  .outro-logo-glow {
      position: absolute;
      top: 50px;
      width: 250px;
      height: 250px;
      background: radial-gradient(circle, rgba(211,84,0,0.3) 0%, rgba(211,84,0,0) 70%);
      filter: blur(20px);
  }

  #outro-tagline {
      font-family: var(--font-display);
      font-size: 56px;
      font-weight: 800;
  }

  #outro-subtext {
      color: var(--text-secondary);
      font-size: 22px;
  }

  .cta-button {
      background: linear-gradient(135deg, var(--brand-primary), var(--brand-accent));
      color: white;
      padding: 16px 40px;
      border-radius: 12px;
      font-weight: bold;
      box-shadow: 0 10px 30px rgba(211,84,0,0.3);
      margin-bottom: 12px;
  }

  .cta-url {
      color: var(--text-muted);
      font-size: 15px;
      font-weight: 600;
  }
  ```

- [ ] **Step 3: Define complete GSAP animation timeline**
  Implement the choreography in `video-teaser/script.js`:
  ```javascript
  // Initialize paused timeline
  const tl = gsap.timeline({ paused: true });
  window.__timelines = window.__timelines || {};
  window.__timelines["tawreed-teaser"] = tl;

  // Scene 1: Pain (0s - 10s)
  tl.set("#scene-pain", { display: "flex" });
  tl.from(".pain-version", { scale: 0.85, opacity: 0, duration: 0.8, ease: "power3.out" }, 0.2);
  tl.from(".pain-version .excel-row:nth-child(3) .error-badge", { scale: 0, opacity: 0, duration: 0.5, ease: "back.out(1.7)" }, 2.0);
  tl.from(".pain-version .excel-row:nth-child(4) .error-badge", { scale: 0, opacity: 0, duration: 0.5, ease: "back.out(1.7)" }, 4.5);
  tl.from(".pain-version .excel-row:nth-child(5) .error-badge", { scale: 0, opacity: 0, duration: 0.5, ease: "back.out(1.7)" }, 7.0);

  // Transition Scene 1 -> Scene 2
  tl.to("#scene-pain", { y: -1080, duration: 0.8, ease: "power2.inOut" }, 9.5);
  tl.set("#app-layout", { display: "flex" }, 9.5);
  tl.from("#app-layout", { y: 1080, duration: 0.8, ease: "power2.inOut" }, 9.5);

  // Scene 2: Ingestion
  tl.set("#mouse-cursor", { x: 1000, y: 650 }, 10.0);
  tl.to("#mouse-cursor", { x: 560, y: 320, duration: 1.5, ease: "power2.out" }, 10.5); // Move to dropzone
  tl.to("#click-ripple", { scale: 2, opacity: 1, duration: 0.3, ease: "power1.out" }, 12.0); // Click dropzone
  tl.to("#click-ripple", { scale: 3, opacity: 0, duration: 0.2 }, 12.3);
  tl.set("#mock-dropzone", { display: "none" }, 12.3);
  tl.set("#mock-file-box", { display: "block" }, 12.3);

  // Move to Start Button
  tl.to("#mouse-cursor", { x: 850, y: 520, duration: 1.5, ease: "power2.out" }, 13.0);
  tl.set("#btn-start-extraction", { disabled: false }, 14.5);
  tl.to("#click-ripple", { scale: 2, opacity: 1, duration: 0.3, ease: "power1.out" }, 14.8); // Click start
  tl.to("#click-ripple", { scale: 3, opacity: 0, duration: 0.2 }, 15.1);
  tl.set("#mock-file-box", { display: "none" }, 15.1);
  tl.set("#mock-progress-container", { display: "flex" }, 15.1);

  // Progress Bar Filling
  tl.to("#progress-bar-fill", { width: "100%", duration: 6.0, ease: "none" }, 15.2);
  tl.set("#chk-1", { className: "check-item active" }, 15.2);
  tl.set("#chk-1", { className: "check-item completed" }, 16.5);
  tl.set("#chk-2", { className: "check-item active" }, 16.5);
  tl.set("#chk-2", { className: "check-item completed" }, 18.5);
  tl.set("#chk-3", { className: "check-item active" }, 18.5);
  tl.set("#chk-3", { className: "check-item completed" }, 20.0);
  tl.set("#chk-4", { className: "check-item active" }, 20.0);
  tl.set("#chk-4", { className: "check-item completed" }, 21.2);
  tl.set("#mock-progress-container", { display: "none" }, 21.5);
  tl.set("#mock-success-card", { display: "flex" }, 21.5);

  // Transition Scene 2 -> Scene 3: Nav Indicator
  tl.to("#nav-workspace", { className: "nav-item" }, 23.0);
  tl.to("#nav-diagnostics", { className: "nav-item active" }, 23.0);
  tl.set("#workspace-panel", { display: "none" }, 23.2);
  tl.set("#diagnostics-panel", { display: "flex" }, 23.2);

  // Scene 3: Diagnostics
  const systemPromptLog = "You are a material takeoff estimator...";
  const cleanJsonLog = "{\n  \"materials\": [\n    { \"name\": \"Tiles\" }\n  ]\n}";
  const repairLog = "[JobProcessor] Extraction completed in 4.2s.";
  tl.set("#diag-console-text", { textContent: systemPromptLog }, 23.2);

  // Move and Click Clean JSON
  tl.to("#mouse-cursor", { x: 720, y: 280, duration: 1.5, ease: "power2.out" }, 24.5);
  tl.to("#click-ripple", { scale: 2, opacity: 1, duration: 0.3, ease: "power1.out" }, 26.0);
  tl.to("#click-ripple", { scale: 3, opacity: 0, duration: 0.2 }, 26.3);
  tl.set("#tab-prompt", { className: "diag-tab" }, 26.3);
  tl.set("#tab-json", { className: "diag-tab active" }, 26.3);
  tl.set("#diag-console-text", { textContent: cleanJsonLog }, 26.3);
  // Scroll code text mockup
  tl.to(".diag-console-container", { scrollTop: 120, duration: 2.0 }, 27.0);

  // Move and Click Repair Logs
  tl.to("#mouse-cursor", { x: 830, y: 280, duration: 1.5, ease: "power2.out" }, 30.0);
  tl.to("#click-ripple", { scale: 2, opacity: 1, duration: 0.3, ease: "power1.out" }, 31.5);
  tl.to("#click-ripple", { scale: 3, opacity: 0, duration: 0.2 }, 31.8);
  tl.set("#tab-json", { className: "diag-tab" }, 31.8);
  tl.set("#tab-logs", { className: "diag-tab active" }, 31.8);
  tl.set("#diag-console-text", { textContent: repairLog }, 31.8);

  // Transition Scene 3 -> Scene 4
  tl.set("#diagnostics-panel", { display: "none" }, 38.0);
  tl.set("#workspace-panel", { display: "flex" }, 38.0);

  // Scene 4: Excel Takeoff
  tl.to("#mouse-cursor", { x: 580, y: 620, duration: 1.5, ease: "power2.out" }, 38.5);
  tl.to("#click-ripple", { scale: 2, opacity: 1, duration: 0.3, ease: "power1.out" }, 40.0);
  tl.to("#click-ripple", { scale: 3, opacity: 0, duration: 0.2 }, 40.3);
  
  // Excel Sheet Fly-In
  tl.set("#excel-overlay", { display: "flex", y: 1080 }, 40.3);
  tl.to("#excel-overlay", { y: 140, duration: 1.0, ease: "power4.out" }, 40.3);

  // Toggle tab in Excel
  tl.to("#mouse-cursor", { x: 510, y: 895, duration: 1.5, ease: "power2.out" }, 43.5);
  tl.to("#click-ripple", { scale: 2, opacity: 1, duration: 0.3, ease: "power1.out" }, 45.0);
  tl.to("#click-ripple", { scale: 3, opacity: 0, duration: 0.2 }, 45.3);
  tl.set("#tab-summary", { className: "excel-tab" }, 45.3);
  tl.set("#tab-details", { className: "excel-tab active" }, 45.3);
  tl.set("#excel-sheet-summary", { display: "none" }, 45.3);
  tl.set("#excel-sheet-details", { display: "block" }, 45.3);

  // Transition Scene 4 -> Scene 5
  tl.to("#excel-overlay", { y: 1080, duration: 0.8, ease: "power2.inOut" }, 50.0);
  tl.set("#app-layout", { display: "none" }, 50.8);
  tl.set("#scene-outro", { display: "flex" }, 50.8);

  // Scene 5: Outro
  tl.from(".outro-logo-card", { scale: 0, opacity: 0, duration: 0.8, ease: "elastic.out(1, 0.75)" }, 50.8);
  tl.from("#outro-tagline", { y: 30, opacity: 0, duration: 0.6, ease: "power3.out" }, 51.5);
  tl.from("#outro-subtext", { y: 20, opacity: 0, duration: 0.6, ease: "power3.out" }, 52.0);
  tl.from("#outro-cta", { y: 20, opacity: 0, duration: 0.6, ease: "power3.out" }, 53.0);

  // Fade out
  tl.to("[data-composition-id='tawreed-teaser']", { opacity: 0, duration: 1.5 }, 58.0);
  ```

- [ ] **Step 4: Commit**
  Run:
  ```bash
  git add video-teaser/index.html video-teaser/style.css video-teaser/script.js
  git commit -m "feat: choreograph full GSAP animation sequence and transition states"
  ```

---

### Task 7: Build Configuration and Validation

**Files:**
- Create: `video-teaser/package.json`

- [ ] **Step 1: Create package.json configuration**
  Create `video-teaser/package.json` with scripts to build, test, and render:
  ```json
  {
    "name": "tawreed-teaser",
    "version": "1.0.0",
    "scripts": {
      "lint": "npx hyperframes lint",
      "validate": "npx hyperframes validate",
      "inspect": "npx hyperframes inspect",
      "preview": "npx hyperframes preview",
      "render": "npx hyperframes render --output out/tawreed_teaser.mp4"
    }
  }
  ```

- [ ] **Step 2: Run verification**
  Run:
  ```bash
  npx hyperframes lint
  npx hyperframes validate
  ```
  Expected: Clear tests with zero timing anomalies and passed contrast reviews.

- [ ] **Step 3: Render**
  Run:
  ```bash
  npx hyperframes render --output video-teaser/out/tawreed_teaser.mp4
  ```
  Expected: Render compiles successfully and outputs the finished `tawreed_teaser.mp4` under `video-teaser/out/`.

- [ ] **Step 4: Commit**
  Run:
  ```bash
  git add video-teaser/package.json
  git commit -m "feat: add build commands and output final rendered teaser mockup"
  ```
