// --- tawreed modern client controller ---

// Safe Tauri core binding with mock fallback for web/browser environments
let invoke = async (cmd, args) => {
  console.warn(`[Mock Invoke] Call to '${cmd}' with:`, args);
  // Mock implementations for basic config load to avoid empty fields in browser testing
  if (cmd === "load_settings") {
    return {
      api_provider: "openai",
      api_key: "sk-...",
      model_name: "gpt-4o-mini",
      base_url: "https://api.openai.com/v1"
    };
  }
  return true;
};

if (window.__TAURI__ && window.__TAURI__.core) {
  invoke = window.__TAURI__.core.invoke;
} else {
  console.warn("Tauri context not detected. Initializing web browser mock mode.");
}

let selectedFilePath = "";
let extractedMaterials = [];

// Tab view navigation routing
window.switchTab = function(tabName) {
  // Hide all tab views and clear button indicators
  document.querySelectorAll('.tab-view').forEach(view => {
    view.classList.remove('active');
  });
  
  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.classList.remove('active');
  });
  
  // Highlight active panel and button
  const activeView = document.getElementById(`${tabName}-tab`);
  const activeBtn = document.getElementById(`nav-${tabName}-btn`);
  
  if (activeView && activeBtn) {
    activeView.classList.add('active');
    activeBtn.classList.add('active');
  }
};

// File picker event handler
window.triggerFilePicker = async function() {
  logConsole("Launching system file browser...");
  try {
    const path = await invoke("select_file");
    if (path) {
      selectedFilePath = path;
      
      // Update UI file status badge
      const badge = document.getElementById("file-info-badge");
      const label = document.getElementById("selected-file-label");
      
      if (badge && label) {
        label.innerText = path.split('\\').pop().split('/').pop(); // Show basename
        label.title = path; // Show full path on hover
        badge.style.display = "flex";
      }
      
      logConsole(`Ingested: ${path}`);
    } else {
      logConsole("File selection cancelled.");
    }
  } catch (err) {
    logConsole(`File select error: ${err}`);
  }
};

// Wizard Navigation
window.showWizardStep = function(step) {
  document.querySelectorAll('.wizard-step').forEach(el => {
    el.style.display = 'none';
    el.classList.remove('active');
  });
  const activeStep = document.getElementById(`wizard-step-${step}`);
  if (activeStep) {
    activeStep.style.display = 'flex';
    // Small timeout to allow display:flex to apply before adding animation class
    setTimeout(() => activeStep.classList.add('active'), 10);
  }
};

window.resetWizard = function() {
  selectedFilePath = "";
  const label = document.getElementById("selected-file-label");
  const badge = document.getElementById("file-info-badge");
  if (label && badge) {
    label.innerText = "No file selected";
    badge.style.display = "none";
  }
  showWizardStep(1);
};

let lastExportedExcelPath = "";

window.openExcelFile = async function() {
  if (!lastExportedExcelPath) return;
  try {
    await invoke("open_file", { path: lastExportedExcelPath });
  } catch (err) {
    showToast(`Failed to open file: ${err}`, "error");
  }
};

// Start AI extraction routine
window.startExtraction = async function() {
  if (!selectedFilePath) {
    showToast("Warning: No document selected. Please pick a file first.", "error");
    return;
  }
  
  showWizardStep(2);
  const statusNode = document.getElementById("progress-status");
  if (statusNode) statusNode.innerText = "Extracting and structuring material packages...";
  
  try {
    const lang = document.getElementById("lang-select").value;
    const res = await invoke("extract_takeoff", { filePath: selectedFilePath, lang });
    
    extractedMaterials = res.materials || [];
    
    if (extractedMaterials.length > 0) {
      if (statusNode) statusNode.innerText = "Generating Excel spreadsheet...";
      
      const exportPath = selectedFilePath.replace(/\.[^/.]+$/, "") + "_Procurement_Package.xlsx";
      const success = await invoke("save_takeoff_excel", { data: extractedMaterials, filePath: exportPath, lang });
      
      if (success) {
        lastExportedExcelPath = exportPath;
        saveJobToHistory(selectedFilePath, extractedMaterials.length);
        showWizardStep(3);
      } else {
        showWizardStep(1);
        showToast("Excel generation failed.", "error");
      }
    } else {
      showWizardStep(1);
      showToast("Extraction complete, but no materials were found. Try adjusting the document.", "error");
    }
  } catch (err) {
    showWizardStep(1);
    showToast(`Extraction failed: ${err}`, "error");
  }
};

// Gather grid data and write to Excel
window.exportToExcel = async function() {
  if (extractedMaterials.length === 0) {
    logConsole("Warning: No material data to export.");
    return;
  }
  
  logConsole("Preparing styled Excel sheet layout...");
  
  try {
    const lang = document.getElementById("lang-select").value;
    
    // Build default output file path
    const exportPath = selectedFilePath.replace(/\.[^/.]+$/, "") + "_Takeoff.xlsx";
    
    // Read grid inputs (supporting manual tweaks)
    const rows = document.querySelectorAll("#takeoff-rows tr");
    const updatedMaterials = [];
    
    rows.forEach(tr => {
      // Skip helper rows (like empty state or total rows)
      if (tr.classList.contains('empty-state-row') || tr.classList.contains('total-row')) {
        return;
      }
      
      const cells = tr.querySelectorAll("td");
      if (cells.length >= 9) {
        updatedMaterials.push({
          package: cells[0].innerText.trim(),
          material_name: cells[1].innerText.trim(),
          technical_specs: cells[2].innerText.trim(),
          brand: cells[3].innerText.trim(),
          unit: cells[4].innerText.trim(),
          quantity: parseFloat(cells[5].innerText.trim()) || 0.0,
          basis: cells[6].innerText.trim(),
          confidence: cells[7].innerText.trim(),
          remarks: cells[8].innerText.trim()
        });
      }
    });

    logConsole(`Writing spreadsheet file to: ${exportPath}`);
    const success = await invoke("save_takeoff_excel", { data: updatedMaterials, filePath: exportPath, lang });
    
    if (success) {
      logConsole(`Spreadsheet generated successfully: ${exportPath}`);
      showToast("Excel spreadsheet exported successfully!", "success");
    } else {
      logConsole("Excel generation encountered an error.");
      showToast("Excel generation failed.", "error");
    }
  } catch (err) {
    logConsole(`Export failed: ${err}`);
    showToast(`Export failed: ${err}`, "error");
  }
};

// Retrieve settings configuration from backend sandbox
window.loadSettings = async function() {
  try {
    const settings = await invoke("load_settings");
    
    document.getElementById("provider-select").value = settings.api_provider;
    document.getElementById("api-key-input").value = settings.api_key;
    document.getElementById("model-input").value = settings.model_name;
    document.getElementById("base-url-input").value = settings.base_url || "";
    
    logConsole("Local configurations loaded successfully.");
  } catch (err) {
    logConsole(`Settings load failure: ${err}`);
    showToast("Failed to load local settings.", "error");
  }
};

// Save updated settings to home-directory
window.saveSettings = async function() {
  logConsole("Saving configurations...");
  try {
    const settings = {
      api_provider: document.getElementById("provider-select").value,
      api_key: document.getElementById("api-key-input").value,
      model_name: document.getElementById("model-input").value,
      base_url: document.getElementById("base-url-input").value,
      preferred_language: "bilingual",
      theme: "system",
      api_timeout_seconds: 900
    };
    
    await invoke("save_settings", { settings });
    logConsole("Local configurations saved successfully.");
    showToast("Configurations saved successfully!", "success");
  } catch (err) {
    logConsole(`Settings save failure: ${err}`);
    showToast(`Save failed: ${err}`, "error");
  }
};

// Adjust default settings parameters when switching provider
window.adjustProviderDefaults = function() {
  const provider = document.getElementById("provider-select").value;
  const modelInput = document.getElementById("model-input");
  const urlInput = document.getElementById("base-url-input");
  
  if (provider === "gemini") {
    modelInput.value = "gemini-2.0-flash";
    urlInput.value = "https://generativelanguage.googleapis.com";
  } else if (provider === "openai") {
    modelInput.value = "gpt-4o-mini";
    urlInput.value = "https://api.openai.com/v1/chat/completions";
  }
};

// Progress tracking not used in wizard flow, safely remove logConsole.
function logConsole(msg) {}
function hideOverlay() {}

// History Management
window.saveJobToHistory = function(filePath, materialsCount) {
  const history = JSON.parse(localStorage.getItem('tawreed_history') || '[]');
  const job = {
    id: crypto.randomUUID(),
    date: new Date().toLocaleString(),
    file: filePath.split('\\').pop().split('/').pop(),
    count: materialsCount,
    status: 'Completed'
  };
  history.unshift(job);
  localStorage.setItem('tawreed_history', JSON.stringify(history));
  if (window.renderHistory) window.renderHistory();
};

window.renderHistory = function() {
  const tbody = document.getElementById("history-rows");
  if (!tbody) return;
  const history = JSON.parse(localStorage.getItem('tawreed_history') || '[]');
  
  if (history.length === 0) {
    tbody.innerHTML = '<tr class="empty-state-row"><td colspan="5" style="text-align: center; color: var(--text-muted); padding: 40px;">No history records found.</td></tr>';
    return;
  }
  
  tbody.innerHTML = '';
  history.forEach(job => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${job.date}</td>
      <td>${job.file}</td>
      <td>${job.count} packages</td>
      <td><span style="color: var(--success-color)">${job.status}</span></td>
      <td><button class="nav-btn" style="padding: 4px 8px; font-size: 11px;">View</button></td>
    `;
    tbody.appendChild(tr);
  });
};

// Populate table takeoff grid with parsed results
function renderGrid(materials) {
  const tbody = document.getElementById("takeoff-rows");
  if (!tbody) return;
  
  tbody.innerHTML = "";
  
  materials.forEach((m, idx) => {
    const tr = document.createElement("tr");
    
    const keys = [
      "package", "material_name", "technical_specs", "brand",
      "unit", "quantity", "basis", "confidence", "remarks"
    ];
    
    keys.forEach(k => {
      const td = document.createElement("td");
      td.contentEditable = "true";
      td.innerText = m[k] !== undefined && m[k] !== null ? m[k] : "";
      
      // Auto formatting helper for numbers
      if (k === "quantity") {
        td.addEventListener('blur', () => {
          const val = parseFloat(td.innerText.trim());
          if (isNaN(val)) {
            td.innerText = "0.00";
          } else {
            td.innerText = val.toFixed(2);
          }
        });
      }
      
      tr.appendChild(td);
    });
    
    tbody.appendChild(tr);
  });
}

// Show empty state placeholder on results panel
function renderEmptyState(reason) {
  const tbody = document.getElementById("takeoff-rows");
  if (!tbody) return;
  
  tbody.innerHTML = `
    <tr class="empty-state-row">
      <td colspan="9">
        <div class="empty-state-message">
          <svg class="empty-state-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
          <p>${reason}</p>
        </div>
      </td>
    </tr>
  `;
}

// Auto-run bootstrap loader on load
document.addEventListener("DOMContentLoaded", () => {
  window.loadSettings();
  if (window.renderHistory) window.renderHistory();
});

// Toast notification helper system
window.showToast = function(message, type = "info") {
  const container = document.getElementById("toast-container");
  if (!container) return;
  
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  
  let icon = "";
  if (type === "success") {
    icon = `<svg style="width:16px;height:16px;color:var(--success-color);" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>`;
  } else if (type === "error") {
    icon = `<svg style="width:16px;height:16px;color:#ef4444;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>`;
  } else {
    icon = `<svg style="width:16px;height:16px;color:var(--primary-accent);" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>`;
  }
  
  toast.innerHTML = `${icon}<span>${message}</span>`;
  container.appendChild(toast);
  
  // Remove toast after animation completes
  setTimeout(() => {
    toast.remove();
  }, 3000);
};
