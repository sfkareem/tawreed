# Tawreed Agentic Takeoff Workbench Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform the single-column workspace in the Tawreed client into a split-screen Quantity Surveying workbench with local document viewers, interactive checkpoints, and an editable takeoff grid.

**Architecture:** We will implement a split-screen flex container inside the HTML UI. The background Python thread will use thread-safe queues to pause and await state notifications from the PyWebView thread during checkpoints. The frontend will hold the active takeoff database in an in-memory JS cache, updating the ExcelExporter only on bulk save.

**Tech Stack:** Python 3.10+, PyWebView, Vanilla HTML5/CSS3/JS, SheetJS (for client-side Excel rendering), PDF.js (for client-side PDF rendering), openpyxl.

---

### Task 1: UI HTML Structure & Split-Screen Shell

**Files:**
- Modify: `gui/index.html` (Rewrite the workspace view section to include the split panes and toggle controls)

- [ ] **Step 1: Replace workspace container inside index.html**
Modify the `<div id="workspace-view" ...>` block inside [gui/index.html](file:///C:/Users/karee/Desktop/QS%20Mind/tawreed/gui/index.html#L71-L223) to introduce the split container:
```html
            <div id="workspace-view" class="view-panel active">
                <header class="workspace-header">
                    <div>
                        <h2>Procurement Workspace</h2>
                        <p>Upload a BOQ, cost breakdown, or image to extract a structured materials list.</p>
                    </div>
                    <!-- Mode Selector Toggle -->
                    <div class="mode-toggle-container">
                        <span class="mode-toggle-label">Agent Mode:</span>
                        <div class="toggle-switch-wrapper">
                            <input type="checkbox" id="agent-mode-checkbox" checked>
                            <label for="agent-mode-checkbox" class="toggle-switch-slider"></label>
                        </div>
                        <span id="agent-mode-status-text" class="mode-toggle-status active">Interactive</span>
                    </div>
                </header>

                <div class="workspace-split-container">
                    <!-- Left Pane: Source Document Viewer -->
                    <div class="split-pane pane-left glass-card">
                        <div class="pane-header">
                            <h3>Source Document</h3>
                            <div class="viewer-tabs" id="viewer-tabs" style="display: none;">
                                <!-- Dynamically generated sheet tabs for Excel -->
                            </div>
                        </div>
                        <div class="pane-content" id="viewer-content">
                            <!-- Initial Dropzone -->
                            <div id="dropzone" class="dropzone-container">
                                <div class="drop-icon-wrapper">
                                    <svg viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                                        <polyline points="17 8 12 3 7 8"></polyline>
                                        <line x1="12" y1="3" x2="12" y2="15"></line>
                                    </svg>
                                </div>
                                <div class="drop-text-wrapper">
                                    <h3>Click to select project file</h3>
                                    <p>Excel, CSV, PDF, Word, or screenshots</p>
                                </div>
                            </div>
                            <div id="viewer-iframe-container" style="display: none; width: 100%; height: 100%;">
                                <iframe id="doc-iframe" style="width: 100%; height: 100%; border: none;"></iframe>
                            </div>
                            <div id="excel-render-container" style="display: none; overflow: auto; width: 100%; height: 100%;"></div>
                        </div>
                    </div>

                    <!-- Right Pane: Active Takeoff Grid -->
                    <div class="split-pane pane-right glass-card">
                        <div class="pane-header">
                            <h3>Takeoff Grid</h3>
                            <div class="grid-actions-bar" id="grid-actions-bar" style="display: none;">
                                <button id="grid-add-row-btn" class="btn btn-sm">Add Row</button>
                                <button id="grid-save-btn" class="btn btn-primary btn-sm">Save & Export</button>
                            </div>
                        </div>
                        <div class="pane-content" id="workbench-content">
                            <!-- Selected File Banner -->
                            <div id="file-selected-box" class="file-selected-box" style="display: none;">
                                <div class="file-info-left">
                                    <div class="file-details">
                                        <h4 id="selected-file-name">filename.xlsx</h4>
                                    </div>
                                </div>
                                <button id="remove-file-btn" class="remove-file-btn">&times;</button>
                            </div>

                            <!-- Progress Checkpoint Status Bar -->
                            <div id="progress-container" class="progress-container" style="display: none;">
                                <div class="progress-header">
                                    <h4 id="progress-status-text">Processing job...</h4>
                                    <span id="progress-percentage">0%</span>
                                </div>
                                <div class="progress-bar-bg">
                                    <div id="progress-bar-fill" class="progress-bar-fill"></div>
                                </div>
                            </div>

                            <!-- Interactive Prompt Panel (Checkpoint Gate) -->
                            <div id="checkpoint-overlay" class="checkpoint-overlay" style="display: none;">
                                <div class="checkpoint-card">
                                    <h4 id="checkpoint-title">Checkpoint Title</h4>
                                    <div class="checkpoint-body" id="checkpoint-body"></div>
                                    <div class="checkpoint-footer">
                                        <button id="checkpoint-cancel-btn" class="btn">Cancel Job</button>
                                        <button id="checkpoint-submit-btn" class="btn btn-primary">Submit & Continue</button>
                                    </div>
                                </div>
                            </div>

                            <!-- The Editable Takeoff Grid -->
                            <div id="takeoff-grid-container" class="takeoff-grid-container" style="display: none;">
                                <!-- Generated spreadsheet table -->
                            </div>

                            <!-- Terminal Agent Console -->
                            <div class="agent-console" id="agent-console">
                                <div style="color: #48bb78; margin-bottom: 8px;">> System initialized. Awaiting job...</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
```

- [ ] **Step 2: Commit layout structure**
Run: `git commit -am "feat: update index.html workspace view for split-screen shell"`

---

### Task 2: Styles for Split Layout & Grid Components

**Files:**
- Modify: `gui/style.css` (Add layout rules for split screen, tabs, check toggles, and grid elements)

- [ ] **Step 1: Write styling parameters**
Append style definitions inside [gui/style.css](file:///C:/Users/karee/Desktop/QS%20Mind/tawreed/gui/style.css):
```css
/* Mode Toggle switch */
.workspace-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}
.mode-toggle-container {
    display: flex;
    align-items: center;
    gap: 10px;
    background: rgba(255, 255, 255, 0.05);
    padding: 8px 16px;
    border-radius: 20px;
    border: 1px solid var(--border-color);
}
.toggle-switch-wrapper {
    position: relative;
    width: 50px;
    height: 24px;
}
.toggle-switch-wrapper input {
    opacity: 0;
    width: 0;
    height: 0;
}
.toggle-switch-slider {
    position: absolute;
    cursor: pointer;
    top: 0; left: 0; right: 0; bottom: 0;
    background-color: #4a5568;
    transition: .4s;
    border-radius: 24px;
}
.toggle-switch-slider:before {
    position: absolute;
    content: "";
    height: 18px;
    width: 18px;
    left: 3px;
    bottom: 3px;
    background-color: white;
    transition: .4s;
    border-radius: 50%;
}
input:checked + .toggle-switch-slider {
    background-color: var(--brand-accent);
}
input:checked + .toggle-switch-slider:before {
    transform: translateX(26px);
}
.mode-toggle-status {
    font-size: 13px;
    font-weight: bold;
    color: #a0aec0;
}
.mode-toggle-status.active {
    color: var(--brand-accent);
}

/* Split Panes */
.workspace-split-container {
    display: flex;
    gap: 20px;
    height: calc(100vh - 180px);
    width: 100%;
}
.split-pane {
    flex: 1;
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow: hidden;
}
.pane-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 12px;
    margin-bottom: 12px;
}
.pane-content {
    flex: 1;
    overflow-y: auto;
    position: relative;
    display: flex;
    flex-direction: column;
}

/* Sheet JS tabs styling */
.viewer-tabs {
    display: flex;
    gap: 6px;
}
.viewer-tab-btn {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid var(--border-color);
    color: var(--text-secondary);
    padding: 4px 10px;
    border-radius: 4px;
    font-size: 12px;
    cursor: pointer;
}
.viewer-tab-btn.active {
    background: var(--brand-accent);
    color: white;
}

/* Takeoff Grid UI styling */
.takeoff-grid-container {
    flex: 1;
    overflow: auto;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    background: rgba(0, 0, 0, 0.2);
}
.grid-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
}
.grid-table th {
    background: rgba(211, 84, 0, 0.9); /* Rust Orange Accent */
    color: white;
    padding: 8px 10px;
    position: sticky;
    top: 0;
    z-index: 10;
    text-align: left;
    border-right: 1px solid var(--border-color);
}
.grid-table td {
    padding: 6px 10px;
    border-bottom: 1px solid var(--border-color);
    border-right: 1px solid var(--border-color);
    color: var(--text-primary);
}
.grid-table tr:nth-child(even) {
    background: rgba(255, 255, 255, 0.02);
}
.grid-table tr.package-header-row {
    background: rgba(255, 255, 255, 0.08) !important;
    font-weight: bold;
    cursor: pointer;
}
.cell-editable {
    outline: none;
}
.cell-editable:focus {
    background: rgba(255, 255, 255, 0.15);
    border: 1px solid var(--brand-accent);
}

/* Checkpoint Box overlay */
.checkpoint-overlay {
    background: rgba(0, 0, 0, 0.8);
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    z-index: 20;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
}
.checkpoint-card {
    background: #1e1e2f;
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 20px;
    width: 100%;
    max-width: 500px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.5);
}
```

- [ ] **Step 2: Commit styling additions**
Run: `git commit -am "style: add responsive split pane layout, mode selectors, tabs and grids"`

---

### Task 3: Load SheetJS Library & Implement local Excel Viewer

**Files:**
- Modify: `gui/index.html` (Include the CDN script for SheetJS)
- Modify: `gui/app.js` (Implement FileReader and XLSX workbook rendering inside Left Pane)

- [ ] **Step 1: Include CDN in index.html**
Insert the SheetJS script inside the `<head>` tag of [gui/index.html](file:///C:/Users/karee/Desktop/QS%20Mind/tawreed/gui/index.html#L3-L8):
```html
    <script src="https://cdn.sheetjs.com/xlsx-latest/package/dist/xlsx.full.min.js"></script>
```

- [ ] **Step 2: Implement file read and render logic in app.js**
Inside [gui/app.js](file:///C:/Users/karee/Desktop/QS%20Mind/tawreed/gui/app.js), implement the XLSX reader:
```javascript
let currentWorkbook = null;

function renderLocalExcelFile(fileDataArrayBuffer) {
    const data = new Uint8Array(fileDataArrayBuffer);
    const workbook = XLSX.read(data, {type: 'array'});
    currentWorkbook = workbook;

    const tabsContainer = document.getElementById("viewer-tabs");
    const renderContainer = document.getElementById("excel-render-container");
    const dropzone = document.getElementById("dropzone");
    const iframeContainer = document.getElementById("viewer-iframe-container");

    tabsContainer.innerHTML = "";
    tabsContainer.style.display = "flex";
    dropzone.style.display = "none";
    iframeContainer.style.display = "none";
    renderContainer.style.display = "block";

    workbook.SheetNames.forEach((sheetName, index) => {
        const btn = document.createElement("button");
        btn.className = "viewer-tab-btn" + (index === 0 ? " active" : "");
        btn.innerText = sheetName;
        btn.addEventListener("click", () => {
            document.querySelectorAll(".viewer-tab-btn").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            displayExcelSheet(sheetName);
        });
        tabsContainer.appendChild(btn);
    });

    displayExcelSheet(workbook.SheetNames[0]);
}

function displayExcelSheet(sheetName) {
    if (!currentWorkbook) return;
    const worksheet = currentWorkbook.Sheets[sheetName];
    const html = XLSX.utils.sheet_to_html(worksheet, {
        header: '',
        footer: ''
    });
    
    const container = document.getElementById("excel-render-container");
    container.innerHTML = html;
    
    // Inject styling directly into table rows
    const table = container.querySelector("table");
    if (table) {
        table.className = "grid-table";
    }
}
```

- [ ] **Step 3: Hook into File Selection**
Update `handleFileSelection` inside [gui/app.js](file:///C:/Users/karee/Desktop/QS%20Mind/tawreed/gui/app.js) to trigger rendering. Since the PyWebView JS engine has access to the local disk, we can read the file data directly in Javascript or offload the file content read to Python:
```javascript
async function handleFileSelection(filePath) {
    currentFile = filePath;
    const fileName = filePath.split(/[\\/]/).pop();
    
    document.getElementById("selected-file-name").innerText = fileName;
    document.getElementById("selected-file-path").innerText = filePath;
    document.getElementById("dropzone").style.display = "none";
    document.getElementById("file-selected-box").style.display = "flex";
    
    const ext = fileName.split('.').pop().toLowerCase();
    if (['xlsx', 'xls', 'xlsm', 'csv'].includes(ext)) {
        try {
            // Read binary array via a custom python bridge function (implemented in next task)
            const fileBytesBase64 = await pywebview.api.read_binary_file(filePath);
            const binaryString = window.atob(fileBytesBase64);
            const len = binaryString.length;
            const bytes = new Uint8Array(len);
            for (let i = 0; i < len; i++) {
                bytes[i] = binaryString.charCodeAt(i);
            }
            renderLocalExcelFile(bytes.buffer);
        } catch (e) {
            showToast("Failed to render local excel: " + e.message, "error");
        }
    } else if (ext === 'pdf') {
        const iframeContainer = document.getElementById("viewer-iframe-container");
        const docIframe = document.getElementById("doc-iframe");
        docIframe.src = "file:///" + filePath.replace(/\\/g, "/");
        iframeContainer.style.display = "block";
    }
    
    if (appSettings.api_key) {
        document.getElementById("generate-btn").disabled = false;
    }
}
```

- [ ] **Step 4: Commit UI file rendering logic**
Run: `git commit -am "feat: integrate SheetJS client-side local Excel viewer and iframe PDF hook"`

---

### Task 4: Python Backend State Engine & Events

**Files:**
- Modify: `tawreed_backend.py` (Implement checkpoint signals, event blocks, and row splitter)

- [ ] **Step 1: Define Job Queues and Event States**
Add a static class or module variables in [tawreed_backend.py](file:///C:/Users/karee/Desktop/QS%20Mind/tawreed/tawreed_backend.py) to manage active job processes:
```python
import threading

class JobStateEngine:
    # Key: job_id, Value: dict containing threading.Event and inputs
    active_checkpoints: Dict[str, dict] = {}

    @classmethod
    def register_job(cls, job_id: str):
        cls.active_checkpoints[job_id] = {
            "checkpoint_event": threading.Event(),
            "approved_packages": None,
            "resolved_warnings": None,
            "aborted": False
        }

    @classmethod
    def await_checkpoint_1(cls, job_id: str, proposed_packages: list) -> list:
        state = cls.active_checkpoints.get(job_id)
        if not state:
            return proposed_packages
        state["proposed_packages"] = proposed_packages
        state["checkpoint_event"].clear()
        
        # Halt execution thread until UI releases the event lock
        state["checkpoint_event"].wait()
        
        if state["aborted"]:
            raise Exception("Job aborted by user at Checkpoint 1.")
            
        return state["approved_packages"] or proposed_packages

    @classmethod
    def await_checkpoint_2(cls, job_id: str, warnings: list) -> dict:
        state = cls.active_checkpoints.get(job_id)
        if not state:
            return {}
        state["warnings"] = warnings
        state["checkpoint_event"].clear()
        
        # Halt execution thread
        state["checkpoint_event"].wait()
        
        if state["aborted"]:
            raise Exception("Job aborted by user at Checkpoint 2.")
            
        return state["resolved_warnings"] or {}
```

- [ ] **Step 2: Inject Checkpoint Hook inside JobProcessor.run**
Insert Checkpoint 1 (Package Approval) after the Planner completes package detection in `tawreed_backend.py:1680`:
```python
        # Register job in active states
        JobStateEngine.register_job(job_id)
        interactive_mode = config.get("agent_interactive_mode", True)
        
        if interactive_mode:
            # Gather proposed package names
            proposed_packages = list(set([
                mat.get("package_en") or mat.get("package") or "General"
                for chunk_data in all_parsed_data for mat in chunk_data.get("materials", [])
            ]))
            
            emit("Planner", "Halting at Checkpoint 1: Awaiting Package list confirmation...", 30)
            
            # Send pause notification to UI via callback
            if event_callback:
                event_callback({
                    "agent": "Planner",
                    "checkpoint": "checkpoint_1",
                    "job_id": job_id,
                    "proposed_packages": proposed_packages
                })
            
            # Wait for user input
            try:
                approved_packages = JobStateEngine.await_checkpoint_1(job_id, proposed_packages)
                emit("Planner", f"Resuming job. Confirmed packages: {approved_packages}", 32)
            except Exception as aborted_e:
                emit("System", "Job aborted by user.")
                raise aborted_e
```

Insert Checkpoint 2 (QA Critique & Warnings) before the Merger step in `tawreed_backend.py:1757`:
```python
        if interactive_mode:
            # Collect warnings and low confidence items
            critique_warnings = []
            for chunk_idx, chunk_data in enumerate(all_parsed_data):
                for flag in chunk_data.get("review_flags", []):
                    critique_warnings.append({
                        "id": f"{chunk_idx}_{flag.get('material_name')}",
                        "material_name": flag.get("material_name"),
                        "issue_type": flag.get("issue_type"),
                        "description": flag.get("description"),
                        "severity": flag.get("severity")
                    })
            
            if critique_warnings:
                emit("QA Reviewer", f"Halting at Checkpoint 2: Resolving {len(critique_warnings)} critique warning(s)...", 80)
                if event_callback:
                    event_callback({
                        "agent": "QA Reviewer",
                        "checkpoint": "checkpoint_2",
                        "job_id": job_id,
                        "warnings": critique_warnings
                    })
                try:
                    resolutions = JobStateEngine.await_checkpoint_2(job_id, critique_warnings)
                    emit("QA Reviewer", f"Resumed. Received {len(resolutions)} warning corrections.", 82)
                except Exception as aborted_e:
                    emit("System", "Job aborted by user.")
                    raise aborted_e
```

- [ ] **Step 3: Implement Row Splitter Logic**
Add a static utility to split compound materials in `tawreed_backend.py`:
```python
    @staticmethod
    def execute_row_action(row_data: dict, action_type: str, instruction: str) -> dict:
        """Processes row splits, re-extraction or translation."""
        if action_type == "split":
            # Call AI to parse single item description into multiple discrete sub-material entities
            prompt = f"""You are a Quantity Surveyor. Split the following compound BOQ item into its individual sub-materials.
            Item: {row_data.get('material_name')}
            Specification: {row_data.get('specification')}
            Unit: {row_data.get('unit')}
            Quantity: {row_data.get('estimated_quantity')}
            
            Instruction constraints: {instruction}
            
            Return ONLY a valid JSON object matching this schema:
            {{
                "sub_materials": [
                    {{
                        "material_name": "Concrete block",
                        "specification": "Standard size",
                        "unit": "pcs",
                        "estimated_quantity": 100,
                        "package": "Masonry"
                    }}
                ]
            }}"""
            # Call default configured AI
            from tawreed_backend import load_config, AIService, JSONRepairService
            config = load_config()
            raw_res, err = AIService.call_ai(config, prompt)
            if err:
                return {"status": "error", "message": err}
            try:
                parsed = JSONRepairService.repair_json(raw_res)
                return {"status": "success", "sub_materials": parsed.get("sub_materials", [])}
            except Exception as e:
                return {"status": "error", "message": f"Malformed split output: {str(e)}"}
        return {"status": "error", "message": "Action type not supported"}
```

- [ ] **Step 4: Commit Python backend updates**
Run: `git commit -am "feat: add thread-blocking checkpoints and row split logic in backend"`

---

### Task 5: Expose Bridge API functions

**Files:**
- Modify: `main.py` (Add binary file reader and link submission commands to the thread lock state)

- [ ] **Step 1: Expose API methods in main.py**
Add the interface bridge commands inside [main.py](file:///C:/Users/karee/Desktop/QS%20Mind/tawreed/main.py#L27-L256):
```python
    def read_binary_file(self, file_path: str) -> str:
        """Reads a file to binary Base64 representation to allow rendering client-side."""
        if not os.path.exists(file_path):
            return ""
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def submit_approved_packages(self, job_id: str, packages: list) -> bool:
        """Resumes checkpoint 1 in backend."""
        from tawreed_backend import JobStateEngine
        state = JobStateEngine.active_checkpoints.get(job_id)
        if state:
            state["approved_packages"] = packages
            state["checkpoint_event"].set()
            return True
        return False

    def submit_warning_resolutions(self, job_id: str, resolutions: dict) -> bool:
        """Resumes checkpoint 2 in backend."""
        from tawreed_backend import JobStateEngine
        state = JobStateEngine.active_checkpoints.get(job_id)
        if state:
            state["resolved_warnings"] = resolutions
            state["checkpoint_event"].set()
            return True
        return False

    def trigger_row_action(self, row_data: dict, action_type: str, instruction: str) -> dict:
        """Resumes checkpoint 2 in backend."""
        from tawreed_backend import JobProcessor
        return JobProcessor.execute_row_action(row_data, action_type, instruction)
```

- [ ] **Step 2: Commit bridge functions**
Run: `git commit -am "feat: expose file bytes read and checkpoint submission API methods"`

---

### Task 6: UI Checkpoints Interaction & Grid Editing Handler

**Files:**
- Modify: `gui/app.js` (Implement checkpoint overlay dialogues, row edits, and category collapsible rendering)

- [ ] **Step 1: Implement Checkpoint Dialog rendering**
Add checkpoint rendering callbacks inside [gui/app.js](file:///C:/Users/karee/Desktop/QS%20Mind/tawreed/gui/app.js):
```javascript
let currentActiveCheckpoint = null;
let currentActiveJobId = null;

function renderCheckpoint(event) {
    currentActiveJobId = event.job_id;
    currentActiveCheckpoint = event.checkpoint;
    
    const overlay = document.getElementById("checkpoint-overlay");
    const title = document.getElementById("checkpoint-title");
    const body = document.getElementById("checkpoint-body");
    
    body.innerHTML = "";
    overlay.style.display = "flex";
    
    if (event.checkpoint === "checkpoint_1") {
        title.innerText = "Confirm Package Taxonomy";
        
        const intro = document.createElement("p");
        intro.innerText = "The planner agent identified the following packages. Double-click to edit or click 'x' to remove.";
        body.appendChild(intro);
        
        const chipsContainer = document.createElement("div");
        chipsContainer.className = "chips-container";
        chipsContainer.style.display = "flex";
        chipsContainer.style.flexWrap = "wrap";
        chipsContainer.style.gap = "8px";
        chipsContainer.style.margin = "12px 0";
        
        event.proposed_packages.forEach(pkg => {
            const chip = document.createElement("div");
            chip.className = "package-chip";
            chip.style.cssText = "background: rgba(211, 84, 0, 0.2); border: 1px solid var(--brand-accent); padding: 4px 10px; border-radius: 12px; display: flex; align-items: center; gap: 6px; font-size: 13px;";
            chip.innerHTML = `<span contenteditable="true">${pkg}</span><span class="remove-chip" style="cursor:pointer; color:red;">&times;</span>`;
            
            chip.querySelector(".remove-chip").addEventListener("click", () => chip.remove());
            chipsContainer.appendChild(chip);
        });
        body.appendChild(chipsContainer);
    } 
    else if (event.checkpoint === "checkpoint_2") {
        title.innerText = "Review Material Warnings";
        
        const intro = document.createElement("p");
        intro.innerText = "Please provide instruction corrections for the following low-confidence flags:";
        body.appendChild(intro);
        
        const listContainer = document.createElement("div");
        listContainer.style.cssText = "display: flex; flex-direction: column; gap: 12px; max-height: 250px; overflow-y: auto; margin-top: 10px;";
        
        event.warnings.forEach(warn => {
            const item = document.createElement("div");
            item.style.cssText = "border: 1px solid var(--border-color); padding: 10px; border-radius: 6px; background: rgba(255,255,255,0.02);";
            item.innerHTML = `
                <div style="font-weight: bold; color: var(--warning);">${warn.material_name} (${warn.issue_type})</div>
                <div style="font-size: 12px; color: var(--text-secondary); margin: 4px 0;">${warn.description}</div>
                <input type="text" data-warn-id="${warn.id}" placeholder="Type correction instruction (e.g. Set size to 90cm) or leave blank to ignore" style="width: 100%; font-size: 12px; padding: 6px; background: rgba(0,0,0,0.2); border: 1px solid var(--border-color); border-radius: 4px; color: white;">
            `;
            listContainer.appendChild(item);
        });
        body.appendChild(listContainer);
    }
}
```

- [ ] **Step 2: Implement Checkpoint Submission**
Connect overlay actions to Python bridge triggers:
```javascript
document.getElementById("checkpoint-submit-btn").addEventListener("click", async () => {
    const overlay = document.getElementById("checkpoint-overlay");
    overlay.style.display = "none";
    
    if (currentActiveCheckpoint === "checkpoint_1") {
        const packageChips = document.querySelectorAll(".package-chip span[contenteditable]");
        const packages = Array.from(packageChips).map(el => el.innerText.trim()).filter(p => p !== "");
        await pywebview.api.submit_approved_packages(currentActiveJobId, packages);
    } 
    else if (currentActiveCheckpoint === "checkpoint_2") {
        const resolutionInputs = document.querySelectorAll("input[data-warn-id]");
        const resolutions = {};
        resolutionInputs.forEach(input => {
            const warnId = input.getAttribute("data-warn-id");
            resolutions[warnId] = input.value.trim();
        });
        await pywebview.api.submit_warning_resolutions(currentActiveJobId, resolutions);
    }
});
```

- [ ] **Step 3: Modify Agent Callback Listener**
Update the global `window.receiveAgentUpdate` callback inside [gui/app.js](file:///C:/Users/karee/Desktop/QS%20Mind/tawreed/gui/app.js#L376-L398) to handle checkpoint pauses:
```javascript
    window.receiveAgentUpdate = function(event) {
        // Logging in terminal console
        const consoleEl = document.getElementById("agent-console");
        if (consoleEl) {
            const entry = document.createElement("div");
            entry.style.marginBottom = "4px";
            let color = "#a0aec0";
            if (event.agent === "Planner") color = "#ecc94b";
            if (event.agent === "Extractor") color = "#63b3ed";
            if (event.agent === "QA Reviewer") color = "#f56565";
            if (event.agent === "Merger") color = "#9f7aea";
            if (event.agent === "System") color = "#48bb78";
            
            entry.innerHTML = `<span style="color: ${color}; font-weight: bold;">[${event.agent}]</span> ${event.message}`;
            consoleEl.appendChild(entry);
            consoleEl.scrollTop = consoleEl.scrollHeight;
        }
        
        // Handle Checkpoint halting
        if (event.checkpoint) {
            renderCheckpoint(event);
        }
        
        if (event.progress !== undefined && event.progress !== null) {
            updateProgressBar(event.progress, event.message);
        }
    };
```

- [ ] **Step 4: Commit UI checkpoint callbacks**
Run: `git commit -am "feat: bind interactive package and QA checkpoint overlays to frontend state"`

---

### Task 7: Interactive Data Grid Integration

**Files:**
- Modify: `gui/app.js` (Render editable material rows, collapsible category sections, row action handlers)

- [ ] **Step 1: Write interactive grid rendering logic**
Add grid build functions in [gui/app.js](file:///C:/Users/karee/Desktop/QS%20Mind/tawreed/gui/app.js):
```javascript
let currentTakeoffData = null;

function renderInteractiveGrid(data) {
    currentTakeoffData = data;
    const container = document.getElementById("takeoff-grid-container");
    const actionsBar = document.getElementById("grid-actions-bar");
    
    container.innerHTML = "";
    container.style.display = "block";
    actionsBar.style.display = "flex";
    
    // Group materials by package
    const grouped = {};
    data.materials.forEach((mat, index) => {
        const pkg = mat.package_en || mat.package || "General";
        if (!grouped[pkg]) grouped[pkg] = [];
        grouped[pkg].push({ ...mat, originalIndex: index });
    });
    
    const table = document.createElement("table");
    table.className = "grid-table";
    
    // Headers
    const headers = ["Package / Material", "Spec / Brand", "Qty", "Unit", "Conf", "Actions"];
    const thead = document.createElement("thead");
    const headerRow = document.createElement("tr");
    headers.forEach(h => {
        const th = document.createElement("th");
        th.innerText = h;
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);
    
    const tbody = document.createElement("tbody");
    
    Object.keys(grouped).forEach(pkg => {
        // Collapsible header row
        const pkgRow = document.createElement("tr");
        pkgRow.className = "package-header-row";
        pkgRow.innerHTML = `<td colspan="6" style="background: rgba(255,255,255,0.06); font-weight: bold;">📁 ${pkg} (${grouped[pkg].length} items)</td>`;
        
        let collapsed = false;
        pkgRow.addEventListener("click", () => {
            collapsed = !collapsed;
            document.querySelectorAll(`.row-pkg-${pkg.replace(/\s+/g, '-')}`).forEach(r => {
                r.style.display = collapsed ? "none" : "table-row";
            });
        });
        tbody.appendChild(pkgRow);
        
        grouped[pkg].forEach(mat => {
            const tr = document.createElement("tr");
            tr.className = `row-pkg-${pkg.replace(/\s+/g, '-')}`;
            
            tr.innerHTML = `
                <td class="cell-editable" contenteditable="true" data-field="material_name" data-idx="${mat.originalIndex}">${mat.material_name_en || mat.material_name}</td>
                <td class="cell-editable" contenteditable="true" data-field="specification" data-idx="${mat.originalIndex}">${mat.specification_en || mat.specification}</td>
                <td class="cell-editable" contenteditable="true" data-field="estimated_quantity" data-idx="${mat.originalIndex}">${mat.estimated_quantity || ''}</td>
                <td class="cell-editable" contenteditable="true" data-field="unit" data-idx="${mat.originalIndex}">${mat.unit_en || mat.unit || ''}</td>
                <td style="color: ${mat.confidence === 'High' ? '#48bb78' : '#ecc94b'};">${mat.confidence}</td>
                <td>
                    <button class="btn btn-sm split-row-btn" data-idx="${mat.originalIndex}">Split</button>
                </td>
            `;
            
            // Listen to cell changes
            tr.querySelectorAll(".cell-editable").forEach(cell => {
                cell.addEventListener("blur", () => {
                    const field = cell.getAttribute("data-field");
                    const idx = parseInt(cell.getAttribute("data-idx"));
                    let val = cell.innerText.trim();
                    if (field === "estimated_quantity") {
                        val = parseFloat(val) || 0;
                    }
                    currentTakeoffData.materials[idx][field] = val;
                });
            });
            
            // Bind Split Item Action
            tr.querySelector(".split-row-btn").addEventListener("click", async () => {
                const idx = parseInt(tr.querySelector(".split-row-btn").getAttribute("data-idx"));
                const rowObj = currentTakeoffData.materials[idx];
                
                const splitInstruction = prompt("Add split instructions (e.g. separate into frame and leaf):");
                if (splitInstruction !== null) {
                    const res = await pywebview.api.trigger_row_action(rowObj, "split", splitInstruction);
                    if (res.status === "success" && res.sub_materials) {
                        // Remove original row and splice in sub-materials
                        currentTakeoffData.materials.splice(idx, 1);
                        currentTakeoffData.materials.push(...res.sub_materials);
                        renderInteractiveGrid(currentTakeoffData);
                        showToast("Row successfully split into sub-materials!", "success");
                    } else {
                        showToast("Split action failed: " + res.message, "error");
                    }
                }
            });
            
            tbody.appendChild(tr);
        });
    });
    
    table.appendChild(tbody);
    container.appendChild(table);
}
```

- [ ] **Step 2: Commit Interactive Table Grid**
Run: `git commit -am "feat: implement collapsible package table rendering, inline grid edits, and row splitting"`

---

### Task 8: Integration and Verification Check

**Files:**
- Modify: `gui/app.js` (Wire the final run extraction response to show the grid, save config options)

- [ ] **Step 1: Bind generate parameters**
Ensure the `agent_interactive_mode` configuration parameters toggles correctly. In `gui/app.js` update `generate-btn` handler:
```javascript
    generateBtn.addEventListener("click", async () => {
        if (!currentFile) return;
        
        generateBtn.disabled = true;
        document.getElementById("progress-container").style.display = "block";
        document.getElementById("success-card").style.display = "none";
        document.getElementById("takeoff-grid-container").style.display = "none";
        document.getElementById("agent-console").innerHTML = "";
        
        const preferredLang = document.getElementById("preferred-language").value;
        const outputDir = currentOutputDir || "";
        const agentInteractiveMode = document.getElementById("agent-mode-checkbox").checked;
        
        // Save current interactive mode parameter state
        appSettings.agent_interactive_mode = agentInteractiveMode;
        await pywebview.api.save_settings(appSettings);
        
        try {
            const res = await pywebview.api.generate(currentFile, outputDir, preferredLang);
            if (res.status === "success") {
                renderInteractiveGrid(res.data);
                showToast("Takeoff extracted. Review materials list below.", "success");
            } else {
                showToast("Job failed: " + res.message, "error");
            }
        } catch (e) {
            showToast("Job runtime error: " + e.message, "error");
        } finally {
            generateBtn.disabled = false;
        }
    });
```

- [ ] **Step 2: Wire the Bulk Save & Export Button**
Ensure edits can be saved back to Python. Update the grid save button inside `setupWorkspaceEvents` in [gui/app.js](file:///C:/Users/karee/Desktop/QS%20Mind/tawreed/gui/app.js):
```javascript
    document.getElementById("grid-save-btn").addEventListener("click", async () => {
        if (!currentTakeoffData) return;
        
        const preferredLang = document.getElementById("preferred-language").value;
        const baseNameNoExt = currentFile.split(/[\\/]/).pop().split('.').slice(0, -1).join('.');
        
        // Save back Excel/CSV
        try {
            await pywebview.api.save_takeoff_state(currentTakeoffData, currentFile, preferredLang);
            showToast("Grid state saved and exported to Excel successfully!", "success");
        } catch (e) {
            showToast("Export failed: " + e.message, "error");
        }
    });
```

- [ ] **Step 3: Implement save_takeoff_state inside main.py**
Expose the state save method inside [main.py](file:///C:/Users/karee/Desktop/QS%20Mind/tawreed/main.py):
```python
    def save_takeoff_state(self, takeoff_data: dict, source_file: str, language: str) -> bool:
        """Saves current interactive grid data back to Excel and CSV files."""
        from tawreed_backend import ExcelExporter, CSVExporter, CONFIG_DIR
        import os
        base_name_no_ext = os.path.splitext(os.path.basename(source_file))[0]
        out_base_name = f"Tawreed_{base_name_no_ext}.xlsx"
        output_path = os.path.join(CONFIG_DIR, out_base_name)
        
        out_csv_name = f"Tawreed_{base_name_no_ext}_for_erp.csv"
        output_csv = os.path.join(CONFIG_DIR, out_csv_name)
        
        ExcelExporter.export(takeoff_data, output_path, language)
        CSVExporter.export(takeoff_data, output_csv, language)
        return True
```

- [ ] **Step 4: Commit entire integration**
Run: `git commit -am "feat: final integration wiring for interactive workbench toggles, run triggers, and manual export saves"`

---

## 🔍 Verification & Testing Plan

### Automated Tests
Run unit validation to verify python parsing models:
```bash
python generate_sample_boq.py
# Execute a test run using the sample file
python -c "from tawreed_backend import load_config, JobProcessor; config=load_config(); JobProcessor.run('sample_boq.xlsx', '.', config, 'english')"
```

### Manual Verification
1. Launch the app locally: `python main.py`.
2. Toggle the "Agent Mode" to "Interactive".
3. Load `sample_boq.xlsx`.
4. Run "Start Extraction Job".
5. Verify Checkpoint 1 (Package Taxonomy Chips dialog) pops up, allowing package edit.
6. Verify Checkpoint 2 (Critique warning list) pops up.
7. Verify grid displays collapsible category sections.
8. Double-click cells to make changes, click "Split" to test row splitting, then click "Save & Export".
9. Open generated Excel and verify edits are preserved.
