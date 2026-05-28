# Workspace Wizard UI Design Specification

## Overview
This specification details the transition of the Tawreed main Workspace interface from a side-by-side dashboard layout into a focused, 4-step wizard layout. This change is designed to guide users sequentially through file upload, configuration, real-time extraction monitoring, and final takeoff review/export.

## User Flow
The new Workspace interface is divided into four distinct phases:
1. **Step 1: Upload File**
   * Displays a prominent Drag & Drop area in the center of the panel.
   * Selecting or dropping a file renders a visual file details card (filename, size, type).
   * Shows a "Next: Configure Settings" button to proceed.
2. **Step 2: Configure Settings**
   * Displays a centered settings card.
   * Offers selections for Extraction Mode (Interactive Mode vs. Batch Mode), preferred language (Bilingual, English, Arabic), and the target output directory.
   * Includes "Back" (returns to Step 1) and "Start Extraction" buttons.
3. **Step 3: Execution & Logs**
   * Displays the 5-stage progress stepper and active console logs in full focus.
   * If a checkpoint (interactive step) is reached, checkpoint selection cards (approving packages, QA resolutions) render directly inline on the screen, keeping the console log scrollable underneath.
4. **Step 4: Review & Export**
   * Displays the success card metrics and download buttons.
   * Renders the Takeoff Grid in full screen width.
   * Features a "Show/Hide Document Preview" toggle to split the screen with the PDF document viewer side-by-side.
   * Features a "Start New Extraction" button to return to Step 1.

---

## Technical Architecture

### 1. HTML Container Structure (`gui/index.html`)
Inside `#workspace-view`, the layout will be restructured into four semantic wizard step containers:
```html
<!-- Wizard Progress Tracker (Header) -->
<div class="wizard-progress-bar" id="wizard-progress-bar">
    <div class="wizard-step-indicator active" id="wiz-indicator-1">
        <span class="wiz-step-number">1</span>
        <span class="wiz-step-text">Upload</span>
    </div>
    <div class="wizard-line"></div>
    <div class="wizard-step-indicator" id="wiz-indicator-2">
        <span class="wiz-step-number">2</span>
        <span class="wiz-step-text">Configure</span>
    </div>
    <div class="wizard-line"></div>
    <div class="wizard-step-indicator" id="wiz-indicator-3">
        <span class="wiz-step-number">3</span>
        <span class="wiz-step-text">Extracting</span>
    </div>
    <div class="wizard-line"></div>
    <div class="wizard-step-indicator" id="wiz-indicator-4">
        <span class="wiz-step-number">4</span>
        <span class="wiz-step-text">Review</span>
    </div>
</div>

<!-- Step 1: Upload Container -->
<div id="wizard-step-1-container" class="wizard-step-container">
    <!-- Dropzone and Selected File Metadata Card -->
</div>

<!-- Step 2: Configure Container -->
<div id="wizard-step-2-container" class="wizard-step-container">
    <!-- Centered Glassmorphic Configuration Card -->
</div>

<!-- Step 3: Execution & Inline Checkpoint Container -->
<div id="wizard-step-3-container" class="wizard-step-container">
    <!-- Stepper & Logs, or Inline Checkpoint approval UI -->
</div>

<!-- Step 4: Final Review Container -->
<div id="wizard-step-4-container" class="wizard-step-container">
    <!-- Success Card and Full-Width Takeoff Grid with Toggle PDF Split Button -->
</div>
```

### 2. CSS View State Switcher (`gui/style.css`)
The workspace layout will use attribute selectors based on a `data-wizard-step` parameter placed on `#workspace-view` to handle visibility toggles. This approach eliminates loading delays and guarantees zero-flicker state changes:
```css
/* Container defaults */
.wizard-step-container {
    display: none;
    flex-direction: column;
    width: 100%;
    height: 100%;
}

/* Visibility rules */
#workspace-view[data-wizard-step="1"] #wizard-step-1-container { display: flex; }
#workspace-view[data-wizard-step="2"] #wizard-step-2-container { display: flex; }
#workspace-view[data-wizard-step="3"] #wizard-step-3-container { display: flex; }
#workspace-view[data-wizard-step="4"] #wizard-step-4-container { display: flex; }
```

### 3. JavaScript Wizard Controller (`gui/app.js`)
We will track and transition the steps through a unified state manager:
```javascript
let currentWizardStep = 1;

function setWizardStep(step) {
    currentWizardStep = step;
    
    // Update data attribute on workspace container
    const workspaceView = document.getElementById("workspace-view");
    if (workspaceView) {
        workspaceView.setAttribute("data-wizard-step", step);
    }
    
    // Update progress tracker visual indicators
    for (let i = 1; i <= 4; i++) {
        const indicator = document.getElementById(`wiz-indicator-${i}`);
        if (!indicator) continue;
        
        indicator.classList.remove("active", "completed");
        if (i < step) {
            indicator.classList.add("completed");
        } else if (i === step) {
            indicator.classList.add("active");
        }
    }
}
```

### 4. Interactive Checkpoints Inline Integration
* If the agent triggers a checkpoint (`receiveAgentUpdate` hears `event.checkpoint`), instead of showing a modal overlay, we will toggle the content of `#wizard-step-3-container` to show the checkpoint approval buttons, options, or warning inputs.
* The `#agent-console` log output remains visible at the bottom of `#wizard-step-3-container`.
* Once submitted, the view toggles back to show the progress stepper.

---

## Verification Plan

### Manual Verification
1. **Step 1:** Confirm that drag-and-drop or file upload opens the file selection box and renders the file info card (with name, size, type) and the "Next" button.
2. **Step 2:** Confirm that clicking "Next" opens the settings card, and clicking "Back" returns to the upload dropzone.
3. **Step 3:** Confirm that starting the extraction shifts to the execution panel, showing the stepper and logs. Confirm that checkpoints render inline within this panel instead of a modal overlay.
4. **Step 4:** Verify that successful runs auto-advance to Step 4, rendering the takeoff grid in full width. Toggle "Show Document Preview" to check split-screen layout.
