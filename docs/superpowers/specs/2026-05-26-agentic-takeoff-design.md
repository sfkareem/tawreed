# 🏗️ Tawreed Upgrade: Agentic Takeoff Workbench Design Specification

- **Date**: 2026-05-26
- **Status**: APPROVED
- **Author**: Antigravity (AI Architect)

---

## 🎯 Goal & Overview

The goal of this upgrade is to transform **Tawreed (توريد)** from a black-box document-to-Excel converter into a professional **Agentic Takeoff Workbench**. By integrating in-app source document viewers, toggleable multi-agent checkpoints, and an interactive, Excel-like editable grid, estimators will gain complete control over the extraction, validation, and packaging of construction Materials takeoff data before exporting to client-ready spreadsheets.

---

## 🎨 1. UI/UX & Layout Architecture

The workspace tab of the desktop client ([gui/index.html](file:///C:/Users/karee/Desktop/QS%20Mind/tawreed/gui/index.html)) will be refactored into a responsive **split-screen viewer panel**.

### Left Pane: In-App Document Viewer
To allow side-by-side verification, the left pane will render the uploaded document:
- **PDF & Image Files**: Embedded via a sandboxed viewer utilizing `PDF.js` styled to match the application's glassmorphic dark theme.
- **Word Documents (`.docx`)**: Parsed client-side and rendered as standard HTML text blocks.
- **Excel & CSV Sheets**: Read locally via **SheetJS (xlsx.js)**. SheetJS parses the binary stream, extracts sheet metadata, and renders read-only styled HTML table sheets selectable via tab buttons.

### Right Pane: Interactive Takeoff Workbench
Displays the real-time agent output and the resulting takeoff list:
- **Mode Toggle**: A header widget to select between:
  - **Batch Mode (Autopilot)**: Runs extraction, QA, merging, and exports files without interruption.
  - **Interactive Mode**: Pauses at checkpoints to consult the user.
- **Interactive Checkpoint Panel**: Displays active questions, proposed packages, or warning logs when the agent is waiting for user approval.
- **Interactive Takeoff Grid**: Renders the extracted materials using a custom table implementation or a lightweight grid library (e.g. Jspreadsheet CE or Tabulator). Features:
  - **Collapsible Packages**: Nested groupings sorted by material category (e.g., Concrete, Finishes).
  - **Advanced Editing**: Inline double-click editing, column sorting, dragging to reorder, row addition/deletion, and spreadsheet keyboard navigation (copy-paste, undo-redo).
  - **Row Action Trigger Menu**: Actions like `Re-extract`, `Split Item` (to separate compound items), and `Translate`.

---

## ⚙️ 2. Asynchronous State Engine & API Bridge

We will establish an asynchronous message-passing loop between the UI thread (Javascript) and the background extraction thread (Python).

### Checkpoint Operations
1. **Checkpoint 1 (Package Approval)**: The planner agent finishes chunk analysis and yields the initial set of packages. It raises a `CHECKPOINT_1_PAUSE` event. The python thread halts on an event lock. The UI displays the package list as editable chips. The user submits the list, calling `submit_approved_packages`, releasing the event lock and passing parameters back.
2. **Checkpoint 2 (QA Critique & Resolution)**: The QA Reviewer agent generates a list of warnings or low-confidence materials. It halts execution, raising `CHECKPOINT_2_PAUSE`. The UI displays the flagged items alongside a prompt window for manual resolution. Resuming releases the event lock and supplies resolutions to the merger agent.

### Python API Interface additions ([main.py](file:///C:/Users/karee/Desktop/QS%20Mind/tawreed/main.py))
```python
class TawreedAPI:
    def submit_approved_packages(self, job_id: str, packages: list) -> bool:
        """Resumes background execution with approved packages."""
        
    def submit_warning_resolutions(self, job_id: str, resolutions: dict) -> bool:
        """Resumes background execution with warning resolution guidelines."""
        
    def trigger_row_action(self, row_data: dict, action_type: str, instruction: str) -> dict:
        """Invokes a row-specific agent operation (re-extract, split, translate)."""
```

---

## 📊 3. Data Flow & Local State Management

### State Synchronization
- **Client Cache**: The entire grid state is held in local memory in [gui/app.js](file:///C:/Users/karee/Desktop/QS%20Mind/tawreed/gui/app.js).
- **Delayed Disk Writing**: Edits in the grid do not trigger immediate file exports. Updates are collected in the JS model and committed in bulk to [tawreed_backend.py](file:///C:/Users/karee/Desktop/QS%20Mind/tawreed/tawreed_backend.py) when the user clicks **"Save & Export"**.
- **Compound Item Splitter**: Selecting "Split Item" on a compound material row triggers a Python bridge function. The Python agent parses the row, splits it into child rows, assigns estimated quantities, and inserts them directly under the corresponding package sections in the JS grid model.

---

## 🚨 4. Error Handling & Recovery

- **Connection Interruption Recovery**: If connection drops during a checkpoint, the UI shows a reconnection dialog. Estimates can be saved locally, and settings (such as API keys) can be modified on-the-fly without resetting job progress.
- **Automatic Recovery Logs**: At each checkpoint, a JSON state snapshot is auto-saved to `~/.tawreed/logs/<job_id>/recovery_state.json`. In case of unexpected shutdown, the job can be resumed from the diagnostics log dashboard.
- **UI History Stack**: An Undo/Redo history stack (up to 50 operations) is maintained in Javascript for row operations.

---

## 🛠️ 5. Affected Files & Packages

- **Modify**: [tawreed_backend.py](file:///C:/Users/karee/Desktop/QS%20Mind/tawreed/tawreed_backend.py) (Add checkpoint event locks, support row operations, state recovery).
- **Modify**: [main.py](file:///C:/Users/karee/Desktop/QS%20Mind/tawreed/main.py) (Expose new API bridge methods).
- **Modify**: [gui/index.html](file:///C:/Users/karee/Desktop/QS%20Mind/tawreed/gui/index.html) (Implement split-pane container and tab panels).
- **Modify**: [gui/style.css](file:///C:/Users/karee/Desktop/QS%20Mind/tawreed/gui/style.css) (Add grid layout, dark theme sheet overrides, toggle styling).
- **Modify**: [gui/app.js](file:///C:/Users/karee/Desktop/QS%20Mind/tawreed/gui/app.js) (Coordinate views, SheetJS loading, table binding, event loop).
- **Verify**: [requirements.txt](file:///C:/Users/karee/Desktop/QS%20Mind/tawreed/requirements.txt) (Ensure `openpyxl` and `pandas` versions match state serialization formats).
