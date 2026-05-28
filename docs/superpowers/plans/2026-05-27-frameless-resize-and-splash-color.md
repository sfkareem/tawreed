# Resizable Frameless Window & Splash Background Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eliminate the red background on the splash screen by flattening the image, adjust workspace layout bounds to prevent bottom overflows, and implement custom HTML/CSS/JS resize handles to make the frameless window resizable with lag-free performance.

**Architecture:** We flatten `verified_icon.png` onto a solid `#1E1E2F` background, expose a `resize_window` API in Python, implement right/bottom/bottom-right resize handles in HTML/CSS/JS, throttle window resize events using `requestAnimationFrame`, and adjust layout constraints in `style.css`.

**Tech Stack:** Python (Pillow, pywebview), JS (requestAnimationFrame, mouse events), CSS (absolute positioning, col-resize/row-resize cursors)

---

### Task 1: Expose Window Resize API in Python

**Files:**
- Modify: `main.py`

- [ ] **Step 1: Add `resize_window` method in `TawreedAPI` class**
  Expose the `resize_window(self, width: int, height: int)` method inside the `TawreedAPI` class (around line 70, next to other window control methods):
  ```python
      def resize_window(self, width: int, height: int) -> bool:
          """Resizes the application window to the specified width and height."""
          try:
              if self._window:
                  self._window.resize(width, height)
                  return True
          except Exception as e:
              logger.error(f"Failed to resize window: {e}")
          return False
  ```
- [ ] **Step 2: Commit**
  ```bash
  git add main.py
  git commit -m "feat(backend): expose resize_window API to frontend"
  ```

---

### Task 2: Inject Custom HTML/CSS Resize Handles

**Files:**
- Modify: `gui/index.html`
- Modify: `gui/style.css`

- [ ] **Step 1: Add HTML elements for handles**
  In `gui/index.html`, append the resize handle divs right before the closing `</body>` tag (around line 770):
  ```html
      <!-- Custom Window Resize Handles -->
      <div class="resize-handle handle-r"></div>
      <div class="resize-handle handle-b"></div>
      <div class="resize-handle handle-br"></div>
  ```

- [ ] **Step 2: Style the handles in CSS**
  In `gui/style.css`, append the styling rules to the end of the file:
  ```css
  /* Custom Resize Handles for Frameless Window */
  .resize-handle {
      position: fixed;
      z-index: 100000;
      background: transparent;
      user-select: none;
  }
  .handle-r {
      top: 0;
      right: 0;
      width: 5px;
      height: 100vh;
      cursor: col-resize;
  }
  .handle-b {
      bottom: 0;
      left: 0;
      width: 100vw;
      height: 5px;
      cursor: row-resize;
  }
  .handle-br {
      bottom: 0;
      right: 0;
      width: 10px;
      height: 10px;
      cursor: se-resize;
  }
  ```

- [ ] **Step 3: Commit**
  ```bash
  git add gui/index.html gui/style.css
  git commit -m "feat(ui): append HTML structure and CSS styles for custom resize handles"
  ```

---

### Task 3: Implement Throttled Window Resize Event Handlers in JavaScript

**Files:**
- Modify: `gui/app.js`

- [ ] **Step 1: Ingest JS Resizing Controllers**
  At the end of `gui/app.js`, append the `setupWindowResizing()` function and initialize it inside `initApp()`:
  - Add inside `initApp()` (around line 125, next to update checks):
    ```javascript
        setupWindowResizing();
    ```
  - Append to the end of `gui/app.js`:
    ```javascript
    // Custom window resizing controllers for frameless viewports
    function setupWindowResizing() {
        const handleR = document.querySelector(".handle-r");
        const handleB = document.querySelector(".handle-b");
        const handleBR = document.querySelector(".handle-br");

        if (!handleR || !handleB || !handleBR) return;

        let startX, startY, startWidth, startHeight;
        let isResizing = false;
        let activeHandle = null;
        let resizeRAF = null;

        function onMouseDown(e, handle) {
            e.preventDefault();
            isResizing = true;
            activeHandle = handle;
            startX = e.screenX;
            startY = e.screenY;
            
            startWidth = window.outerWidth || window.innerWidth;
            startHeight = window.outerHeight || window.innerHeight;

            document.addEventListener("mousemove", onMouseMove);
            document.addEventListener("mouseup", onMouseUp);
        }

        handleR.addEventListener("mousedown", (e) => onMouseDown(e, 'r'));
        handleB.addEventListener("mousedown", (e) => onMouseDown(e, 'b'));
        handleBR.addEventListener("mousedown", (e) => onMouseDown(e, 'br'));

        function onMouseMove(e) {
            if (!isResizing) return;
            
            const deltaX = e.screenX - startX;
            const deltaY = e.screenY - startY;
            
            let newWidth = startWidth;
            let newHeight = startHeight;
            
            if (activeHandle === 'r' || activeHandle === 'br') {
                newWidth = startWidth + deltaX;
            }
            if (activeHandle === 'b' || activeHandle === 'br') {
                newHeight = startHeight + deltaY;
            }

            // Enforce minimum dimension boundary
            newWidth = Math.max(900, newWidth);
            newHeight = Math.max(600, newHeight);

            // Throttle resize requests using RequestAnimationFrame (60fps)
            if (resizeRAF) cancelAnimationFrame(resizeRAF);
            resizeRAF = requestAnimationFrame(() => {
                if (window.pywebview && window.pywebview.api && window.pywebview.api.resize_window) {
                    window.pywebview.api.resize_window(newWidth, newHeight);
                }
            });
        }

        function onMouseUp() {
            isResizing = false;
            activeHandle = null;
            document.removeEventListener("mousemove", onMouseMove);
            document.removeEventListener("mouseup", onMouseUp);
        }
    }
    ```
- [ ] **Step 2: Commit**
  ```bash
  git add gui/app.js
  git commit -m "feat(ui): implement throttled custom window resizing logic in app.js"
  ```

---

### Task 4: Fix Workspace Split Container Overflow Heights

**Files:**
- Modify: `gui/style.css`

- [ ] **Step 1: Fix Workspace Heights**
  In `gui/style.css`, modify the height parameters of `.workspace-split-container` (around line 1194):
  ```css
  .workspace-split-container {
      display: grid;
      grid-template-columns: 1fr 1.15fr;
      gap: 24px;
      flex-grow: 1;
      height: calc(100vh - 200px); /* Adjusted to fit main content padding + title bar height without overflows */
      min-height: 0; /* Allows shrinking below 550px on resize */
      align-items: stretch;
  }
  ```
- [ ] **Step 2: Commit**
  ```bash
  git add gui/style.css
  git commit -m "fix(ui): adjust split container heights to prevent bottom overflows on window resize"
  ```

---

### Task 5: Compile Standalone Portable Executable & Validate

**Files:**
- None (Build verification)

- [ ] **Step 1: Trigger clean compilation**
  Run PyInstaller compiler to verify build is successful:
  ```powershell
  .venv/Scripts/pyinstaller.exe main.spec --clean -y
  ```
- [ ] **Step 2: Verify `dist/tawreed.exe` starts and behaves correctly**
  Verify that:
  - Startup splash screen shows the dark matching background (no transparency red background).
  - Frameless window can be resized by dragging edges (right, bottom, bottom-right).
  - No scroll overflows exist on workspace panel grid content.
