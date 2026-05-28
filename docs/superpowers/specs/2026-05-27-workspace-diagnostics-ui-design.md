# Specs: Workspace & Diagnostics UI Rebuild (Glassmorphism Dark Theme)

This specification details the UX/UI overhaul of the Tawreed Procurement Assistant's Workspace and Diagnostics views to optimize workflow feedback, active tracking, and visual polish.

## 1. Visual Theme & Style Tokens

To achieve the **Ultra-Modern Glassmorphic Dark UI** theme:
*   **Colors:**
    *   `--bg-base`: `#0a0a0f` (deep base black)
    *   `--bg-surface`: `rgba(20, 20, 30, 0.45)` (frosted translucent cards)
    *   `--bg-surface-opaque`: `#12121a` (fallback for solid overlays)
    *   `--border-color`: `rgba(255, 255, 255, 0.08)` (subtle borders)
    *   `--brand-primary`: `#d35400` (Rust Orange)
    *   `--brand-secondary`: `#e67e22` (Bright Rust Accent)
    *   `--diag-blue`: `#3498db` (Diagnostics Accent)
    *   `--text-primary`: `#ffffff`
    *   `--text-secondary`: `#a0aec0`
    *   `--text-muted`: `#718096`
*   **Effects:**
    *   `backdrop-filter: blur(12px)` on all glass cards.
    *   `box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37)` for depth.
*   **Animations:**
    *   `stepper-pulse`: Gentle scaling and color shifting on active progress nodes.
    *   `wizard-show`: Smooth scale-in transition for checkpoint overlays.

---

## 2. Workspace Panel Rebuild

The Workspace pane has three dynamic states:

### A. Pre-Job State (Upload & Config)
*   **Dropzone Card:** A large drag-and-drop area. The background is a translucent black. It features a dashed accent border (`rgba(211, 84, 0, 0.4)`) that changes to a solid pulsing orange border during dragover events. The upload icon has a subtle float animation.
*   **Parameters Section:** Grouped below the dropzone in a unified card containing:
    *   Language select dropdown (Bilingual, Arabic, English).
    *   Output directory textbox + browse button.
    *   "Start Extraction Job" button (disabled until a file is selected; glows orange when active).

### B. Active Processing State (Stepper & Console)
*   **Linear Stepper UI:** Replaces the upload dropzone dynamically when the job starts.
    *   Consists of a horizontal track connecting 5 progress circles:
        1.  `Parsing` (Document loading and serialization)
        2.  `Planning` (Column mapping and chunk planning)
        3.  `Extraction` (AI chunk processing)
        4.  `QA Review` (Multi-iteration critique checks)
        5.  `Export` (Excel/CSV formulation)
    *   *Step styling:* Completed steps are highlighted in green (`#2ecc71`) with a checkmark. Active steps pulse in orange (`#d35400`) with a circular loading progress overlay. Pending steps remain muted gray.
*   **Docked Console Log:** Positions directly beneath the stepper. Features a scrollable monospace card (`background: rgba(0,0,0,0.3)`) showing real-time logs with colored tag prefixes (`[System]`, `[Planner]`, `[Extractor]`, etc.).

### C. Checkpoint State (Step-by-Step Wizard Card)
*   **Centered Card Dialog:** Appears in the center of the right pane over a translucent black background (`rgba(10, 10, 15, 0.7)` without blur to keep the logs visible underneath).
*   **Visual Structure:** 
    *   Header shows active checkpoint state (e.g. `Step 1 of 2: Taxonomy Verification`).
    *   Body houses the interactive checklist/tags or warning textareas.
    *   Footer contains cancel and confirm actions.

### D. Post-Job State (Success & Grid)
*   **Success Metrics Banner:** Displays total counts of Materials, Packages, Flags, and Warnings in a grid of 4 small glass badges.
*   **Workflow Action Row:** Contains buttons to open the Excel output, CSV file, output folder, and the new **"View Technical Diagnostics"** button.
    *   *Technical Diagnostics Button:* Styled with a secondary blue border (`#3498db`) and icon. Clicking it switches navigation to the Diagnostics panel and automatically selects the current job from the history list.
*   **Takeoff Grid:** Stretches full-width below the success banner, presenting a dark spreadsheet editor with zebra-stripes, clear borders, and action columns.

---

## 3. Diagnostics & History Rebuild

### A. Sidebar Job History List
*   **Job Items:** Cards showing the filename, timestamp, and metadata badges.
*   *Hover state:* Dynamic slide-in highlight effect.

### B. Diagnostics Panel View
*   **Tabs:** Clean horizontal selection tabs.
*   **Code-Viewer Console:** Styled as a code editor (`#0f0f15` background, Fira Code/Consolas font, light gray text).
*   **Utility Toolbar:** Docked on top of the code viewer with:
    *   `Copy to Clipboard` button.
    *   `Search console log` input field that dynamically highlights matches inside the log container.

---

## 4. Verification Plan

### Manual Verification
1.  Run the application and verify that the workspace defaults to a single full-width pane (no split screen).
2.  Select `sample_boq.xlsx` and verify the dropzone transitions correctly.
3.  Click "Start Extraction Job" and verify the parameter settings disappear, replaced by the linear 5-stage progress stepper and console logs.
4.  In Interactive Mode, verify the checkpoint wizard appears centered in a glass card modal, and that clicking "Proceed" advances the stepper.
5.  On completion, click the "View Technical Diagnostics" button on the success card and verify that the view switches to Diagnostics with the current Job ID selected.
