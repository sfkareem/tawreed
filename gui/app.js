// Global State Variables
let currentFile = null;
let currentOutputDir = null;
let appSettings = {};
let activeJobId = null;
let activeJobDiagnostics = null;
let currentDiagTab = "serialized_input";

// Default configuration presets for providers
const PROVIDER_PRESETS = {
    gemini: {
        url: "https://generativelanguage.googleapis.com",
        model: "gemini-1.5-flash"
    },
    openai: {
        url: "https://api.openai.com",
        model: "gpt-4o-mini"
    },
    anthropic: {
        url: "https://api.anthropic.com",
        model: "claude-3-5-haiku-20241022"
    },
    custom: {
        url: "http://localhost:11434",
        model: "llama3"
    }
};

// Initialize Application on DOM Content Loaded
document.addEventListener("DOMContentLoaded", () => {
    // Wait until pywebview is ready
    window.addEventListener('pywebviewready', () => {
        initApp();
    });
});

// App Initialization
async function initApp() {
    setupNavigation();
    setupDropzone();
    setupSettingsEvents();
    setupWorkspaceEvents();
    setupDiagnosticsEvents();
    
    // Load config from backend
    await loadConfig();
    await refreshJobHistory();
}

// Sidebar View Navigation
function setupNavigation() {
    const navItems = document.querySelectorAll(".nav-item");
    const viewPanels = document.querySelectorAll(".view-panel");

    navItems.forEach(item => {
        item.addEventListener("click", () => {
            const targetView = item.getAttribute("data-view");
            
            navItems.forEach(nav => nav.classList.remove("active"));
            item.classList.add("active");

            viewPanels.forEach(panel => {
                panel.classList.remove("active");
                if (panel.id === `${targetView}-view`) {
                    panel.classList.add("active");
                }
            });

            // Trigger view specific reloads
            if (targetView === "history") {
                refreshJobHistory();
            }
        });
    });
}

// Configuration & Settings Panel Logic
async function loadConfig() {
    try {
        appSettings = await pywebview.api.load_settings();
        
        // Populate inputs
        document.getElementById("api-provider").value = appSettings.api_provider || "gemini";
        document.getElementById("base-url").value = appSettings.base_url || "";
        document.getElementById("api-key").value = appSettings.api_key || "";
        document.getElementById("model-name").value = appSettings.model_name || "";
        document.getElementById("max-file-size").value = appSettings.max_file_size_mb || 15;
        document.getElementById("max-chars").value = appSettings.max_content_length_chars || 80000;
        document.getElementById("preferred-language").value = appSettings.preferred_language || "bilingual";
        
        updateWarningBanner();
    } catch (e) {
        showToast("Failed to load settings.", "error");
    }
}

function updateWarningBanner() {
    const warningBanner = document.getElementById("api-status-warning");
    const generateBtn = document.getElementById("generate-btn");
    
    if (!appSettings.api_key) {
        warningBanner.style.display = "flex";
        warningBanner.querySelector("div").innerHTML = "To run extraction, ensure your AI Key is configured. Edit credentials in the <strong>AI Settings</strong> tab.";
        generateBtn.disabled = true;
    } else {
        warningBanner.style.display = "none";
        if (currentFile) {
            generateBtn.disabled = false;
        }
    }
}

function setupSettingsEvents() {
    const providerSelect = document.getElementById("api-provider");
    const baseUrlInput = document.getElementById("base-url");
    const modelInput = document.getElementById("model-name");
    const toggleKeyBtn = document.getElementById("toggle-key-visibility");
    const apiKeyInput = document.getElementById("api-key");
    const saveBtn = document.getElementById("save-settings-btn");
    const testBtn = document.getElementById("test-connection-btn");

    // Provider auto-fill presets
    providerSelect.addEventListener("change", () => {
        const prov = providerSelect.value;
        if (PROVIDER_PRESETS[prov]) {
            baseUrlInput.value = PROVIDER_PRESETS[prov].url;
            modelInput.value = PROVIDER_PRESETS[prov].model;
        }
    });

    // Password visibility toggle
    toggleKeyBtn.addEventListener("click", () => {
        const type = apiKeyInput.getAttribute("type") === "password" ? "text" : "password";
        apiKeyInput.setAttribute("type", type);
    });

    // Save Settings
    saveBtn.addEventListener("click", async () => {
        const newSettings = {
            api_provider: providerSelect.value,
            base_url: baseUrlInput.value.trim(),
            api_key: apiKeyInput.value.trim(),
            model_name: modelInput.value.trim(),
            max_file_size_mb: parseInt(document.getElementById("max-file-size").value) || 15,
            max_content_length_chars: parseInt(document.getElementById("max-chars").value) || 80000,
            preferred_language: document.getElementById("preferred-language").value
        };

        const success = await pywebview.api.save_settings(newSettings);
        if (success) {
            appSettings = newSettings;
            updateWarningBanner();
            showToast("Settings saved successfully!", "success");
        } else {
            showToast("Failed to save settings.", "error");
        }
    });

    // Test Connection
    testBtn.addEventListener("click", async () => {
        testBtn.disabled = true;
        const origText = testBtn.innerHTML;
        testBtn.innerHTML = "Testing connection...";
        
        const tempSettings = {
            api_provider: providerSelect.value,
            base_url: baseUrlInput.value.trim(),
            api_key: apiKeyInput.value.trim(),
            model_name: modelInput.value.trim(),
            max_file_size_mb: 15,
            max_content_length_chars: 80000
        };

        try {
            const res = await pywebview.api.test_connection(tempSettings);
            if (res.status === "success") {
                showToast(res.message, "success");
            } else {
                showToast(res.message, "error");
            }
        } catch (e) {
            showToast(`Connection test failed: ${e.message}`, "error");
        } finally {
            testBtn.disabled = false;
            testBtn.innerHTML = origText;
        }
    });
}

// Workspace & File Input Logic
function setupDropzone() {
    const dropzone = document.getElementById("dropzone");
    const removeFileBtn = document.getElementById("remove-file-btn");
    
    // File selection dialog trigger
    dropzone.addEventListener("click", async () => {
        const filePath = await pywebview.api.select_file();
        if (filePath) {
            handleFileSelection(filePath);
        }
    });

    // Native Drag and Drop HTML5 events
    dropzone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropzone.classList.add("drag-over");
    });

    dropzone.addEventListener("dragleave", () => {
        dropzone.classList.remove("drag-over");
    });

    dropzone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropzone.classList.remove("drag-over");
        
        const files = e.dataTransfer.files;
        if (files && files.length > 0) {
            // Note: Since this is Webview, native files might not contain the full physical path 
            // directly in the standard JS File object due to security sandbox (or it may depending on engine).
            // Usually, pywebview file dialog is much safer, but if they drag and drop, we can attempt to get path:
            const path = files[0].path; 
            if (path) {
                handleFileSelection(path);
            } else {
                // If sandbox restricts path, notify user to use Click Selection
                showToast("Please click to select files on Windows to allow path access.", "warning");
            }
        }
    });

    // Remove File
    removeFileBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        resetFileSelection();
    });
}

function handleFileSelection(filePath) {
    currentFile = filePath;
    const fileName = filePath.split(/[\\/]/).pop();
    
    document.getElementById("selected-file-name").innerText = fileName;
    document.getElementById("selected-file-path").innerText = filePath;
    
    document.getElementById("dropzone").style.display = "none";
    document.getElementById("file-selected-box").style.display = "flex";
    
    // Check if settings allow generation
    const generateBtn = document.getElementById("generate-btn");
    if (appSettings.api_key) {
        generateBtn.disabled = false;
    }
}

function resetFileSelection() {
    currentFile = null;
    document.getElementById("dropzone").style.display = "flex";
    document.getElementById("file-selected-box").style.display = "none";
    document.getElementById("generate-btn").disabled = true;
    
    // Hide progress and success cards
    document.getElementById("progress-container").style.display = "none";
    document.getElementById("success-card").style.display = "none";
}

function setupWorkspaceEvents() {
    const generateBtn = document.getElementById("generate-btn");
    const selectFolderBtn = document.getElementById("select-output-folder-btn");
    const folderInput = document.getElementById("output-directory-input");
    const openExcelBtn = document.getElementById("open-excel-btn");
    const openCsvBtn = document.getElementById("open-csv-btn");
    const openFolderBtn = document.getElementById("open-folder-btn");

    // Output Directory selector
    selectFolderBtn.addEventListener("click", async () => {
        const folderPath = await pywebview.api.select_output_folder();
        if (folderPath) {
            currentOutputDir = folderPath;
            folderInput.value = folderPath;
        }
    });

    // Main Run Trigger
    generateBtn.addEventListener("click", async () => {
        if (!currentFile) return;

        // Reset UI
        generateBtn.disabled = true;
        document.getElementById("success-card").style.display = "none";
        document.getElementById("progress-container").style.display = "flex";
        
        const steps = {
            parse: document.getElementById("step-parse"),
            ai: document.getElementById("step-ai"),
            repair: document.getElementById("step-repair"),
            excel: document.getElementById("step-excel")
        };

        // Reset Steps UI
        Object.keys(steps).forEach(k => {
            steps[k].className = "step-item";
            steps[k].querySelector(".step-icon-pending").style.display = "block";
            steps[k].querySelector(".step-icon-check").style.display = "none";
        });

        // Set Step 1 Active
        steps.parse.classList.add("active");
        updateProgressBar(10, "Parsing project document...");

        // Start faking transitions during blocking call
        let progressVal = 10;
        const progressInterval = setInterval(() => {
            if (progressVal < 90) {
                progressVal += 1;
                // Transition steps based on faked timings
                if (progressVal === 30) {
                    steps.parse.className = "step-item completed";
                    steps.parse.querySelector(".step-icon-pending").style.display = "none";
                    steps.parse.querySelector(".step-icon-check").style.display = "block";
                    
                    steps.ai.classList.add("active");
                    updateProgressBar(30, "Structuring query & extracting materials (this takes a moment)...");
                } else if (progressVal === 80) {
                    steps.ai.className = "step-item completed";
                    steps.ai.querySelector(".step-icon-pending").style.display = "none";
                    steps.ai.querySelector(".step-icon-check").style.display = "block";
                    
                    steps.repair.classList.add("active");
                    updateProgressBar(80, "Checking response JSON structure...");
                }
                document.getElementById("progress-percentage").innerText = `${progressVal}%`;
                document.getElementById("progress-bar-fill").style.width = `${progressVal}%`;
            }
        }, 150);

        try {
            const lang = document.getElementById("preferred-language").value;
            const res = await pywebview.api.generate(currentFile, currentOutputDir || "", lang);
            
            clearInterval(progressInterval);

            if (res.status === "success") {
                // Complete all steps
                Object.keys(steps).forEach(k => {
                    steps[k].className = "step-item completed";
                    steps[k].querySelector(".step-icon-pending").style.display = "none";
                    steps[k].querySelector(".step-icon-check").style.display = "block";
                });
                
                updateProgressBar(100, "Done!");
                
                // Show Success Metrics
                const manifest = res.data;
                document.getElementById("badge-materials").innerText = manifest.summary.total_materials_extracted || 0;
                document.getElementById("badge-packages").innerText = manifest.summary.packages_detected ? manifest.summary.packages_detected.length : 0;
                document.getElementById("badge-flags").innerText = manifest.flags_count || 0;
                document.getElementById("badge-warnings").innerText = manifest.warnings_count || 0;
                
                activeJobId = manifest.job_id;
                
                // Bind buttons to paths
                openExcelBtn.onclick = () => {
                    pywebview.api.open_folder(manifest.output_file); // Passing file path to startfile opens the file!
                };
                
                openCsvBtn.onclick = () => {
                    pywebview.api.open_folder(manifest.output_csv); // Opens CSV report
                };
                
                openFolderBtn.onclick = () => {
                    pywebview.api.open_folder(manifest.output_dir);
                };

                // Show success card and hide progress after delay
                setTimeout(() => {
                    document.getElementById("progress-container").style.display = "none";
                    document.getElementById("success-card").style.display = "flex";
                }, 500);
                
                showToast("Materials extracted successfully!", "success");
            } else {
                showToast(res.message, "error");
                document.getElementById("progress-container").style.display = "none";
            }
        } catch (e) {
            clearInterval(progressInterval);
            showToast(`Execution Error: ${e.message}`, "error");
            document.getElementById("progress-container").style.display = "none";
        } finally {
            generateBtn.disabled = false;
        }
    });
}

function updateProgressBar(percent, text) {
    document.getElementById("progress-percentage").innerText = `${percent}%`;
    document.getElementById("progress-bar-fill").style.width = `${percent}%`;
    document.getElementById("progress-status-text").innerText = text;
}

// Diagnostics & Job History Panel Logic
async function refreshJobHistory() {
    const listContainer = document.getElementById("jobs-list");
    listContainer.innerHTML = ""; // Clear
    
    try {
        const history = await pywebview.api.get_jobs_history();
        
        if (!history || history.length === 0) {
            listContainer.innerHTML = `
                <div class="empty-state">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                    <h4>No past jobs found</h4>
                    <p>Execute an extraction job first to generate diagnostic logs.</p>
                </div>
            `;
            document.getElementById("diagnostics-panel").style.display = "none";
            return;
        }

        history.forEach(job => {
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
                // Remove selection from others
                document.querySelectorAll(".job-item").forEach(j => j.classList.remove("selected"));
                item.classList.add("selected");
                loadJobDiagnostics(job.job_id);
            });
            
            listContainer.appendChild(item);
        });
    } catch (e) {
        showToast("Failed to load jobs history.", "error");
    }
}

async function loadJobDiagnostics(jobId) {
    try {
        const res = await pywebview.api.get_diagnostics(jobId);
        if (res.status === "success") {
            activeJobDiagnostics = res.diagnostics;
            
            document.getElementById("diagnostics-title").innerText = `Job Diagnostics: ${jobId}`;
            document.getElementById("diagnostics-panel").style.display = "block";
            
            // Set open folder button action
            document.getElementById("open-diagnostics-folder-btn").onclick = () => {
                // Config log folder path
                const logPath = `C:\\Users\\karee\\.tawreed\\logs\\${jobId}`;
                pywebview.api.open_folder(logPath);
            };

            // Load default tab content
            renderDiagTabContent();
        } else {
            showToast(res.message, "error");
        }
    } catch (e) {
        showToast("Error loading diagnostics.", "error");
    }
}

function setupDiagnosticsEvents() {
    const tabs = document.querySelectorAll(".tab-btn");
    tabs.forEach(tab => {
        tab.addEventListener("click", () => {
            tabs.forEach(t => t.classList.remove("active"));
            tab.classList.add("active");
            
            currentDiagTab = tab.getAttribute("data-tab");
            renderDiagTabContent();
        });
    });
}

function renderDiagTabContent() {
    if (!activeJobDiagnostics) return;
    
    const pre = document.getElementById("diagnostics-text");
    let content = activeJobDiagnostics[currentDiagTab] || "";
    
    if (!content.trim()) {
        pre.innerText = "[Empty Log / Not Applicable for this job]";
        return;
    }
    
    // Try to prettify JSON for specific tabs
    if (currentDiagTab === "extracted_data" || currentDiagTab === "manifest") {
        try {
            const parsed = JSON.parse(content);
            content = JSON.stringify(parsed, null, 4);
        } catch(e) {}
    }
    
    pre.innerText = content;
}

// Custom Toast Utility
function showToast(message, type = "success") {
    const toast = document.getElementById("toast");
    const toastMsg = document.getElementById("toast-message");
    const toastIcon = document.getElementById("toast-icon");
    
    toast.className = `toast ${type}`;
    toastMsg.innerText = message;
    
    // Render icon based on type
    if (type === "success") {
        toastIcon.innerHTML = `<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline>`;
    } else if (type === "error") {
        toastIcon.innerHTML = `<circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line>`;
    } else { // warning
        toastIcon.innerHTML = `<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line>`;
    }
    
    toast.style.display = "flex";
    
    setTimeout(() => {
        toast.style.display = "none";
    }, 4000);
}
