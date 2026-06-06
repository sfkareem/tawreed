# Real-time Extraction Feedback & Persistent State Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prevent BOQ processing from stopping or losing state when navigating between tabs, and display real-time progress logs and LLM thinking in the frontend UI.

**Architecture:** 
1. **State Preservation**: Lift the workspace extraction state (status, logs, thinking, paths) and the settings state to the parent `App` component in `page.tsx` so it persists when screens are unmounted.
2. **Backend SSE Streaming**: Enable `"stream": true` in `processor.rs`. Read the response chunk-by-chunk using `resp.chunk()`. Parse the SSE stream and emit `"boq-token"` events with `token` and `is_thought` boolean.
3. **Frontend Event Listeners**: Listen to `"boq-progress"` and `"boq-token"` in the parent `App` component on mount, updating the shared extraction state.
4. **Interactive UI**: Render a live-updating progress terminal, a pulsing collapsible "LLM Thinking Process" card, and status indicators in `Workspace`.

**Tech Stack:** Rust, reqwest (json, stream features), Tauri event system, React, Next.js, Framer Motion, Lucide Icons

---

### Task 1: Rust backend streaming support

**Files:**
- Modify: `src-tauri/Cargo.toml`
- Modify: `src-tauri/src/processor.rs`

- [ ] **Step 1: Add reqwest stream feature and futures-util to Cargo.toml**
  Update `reqwest` dependency in `Cargo.toml`:
  ```toml
  reqwest = { version = "0.13.4", features = ["json", "stream"] }
  ```

- [ ] **Step 2: Define StreamPayload in processor.rs**
  Add the serializable payload struct at the top of `processor.rs`:
  ```rust
  #[derive(serde::Serialize, Clone)]
  struct StreamPayload {
      token: String,
      is_thought: bool,
  }
  ```

- [ ] **Step 3: Modify extract_work_packages to use streaming**
  Replace the blocking LLM request in `processor.rs` (lines 96 to 170) with chunk-by-chunk SSE streaming:
  ```rust
      let client = reqwest::Client::new();
      let req_body = json!({
          "model": model,
          "messages": [
              {"role": "system", "content": "You output ONLY a raw JSON dictionary mapping IDs to categories. Absolutely no markdown blocks, no intro text."},
              {"role": "user", "content": prompt}
          ],
          "temperature": 0.0,
          "stream": true
      });

      let _ = app.emit("boq-progress", "Contacting LLM for category mapping...");

      let resp = client
          .post(format!("{}/chat/completions", base_url.trim_end_matches('/')))
          .header("Authorization", format!("Bearer {}", api_key))
          .json(&req_body)
          .send()
          .await
          .map_err(|e| format!("Request failed: {}", e))?;

      if !resp.status().is_success() {
          let error_text = resp.text().await.unwrap_or_default();
          return Err(format!("LLM Error: {}", error_text));
      }

      let _ = app.emit("boq-progress", "Extracting categories from stream...");

      let mut full_response = String::new();
      let mut reasoning_response = String::new();
      let mut stream_buf = String::new();
      let mut reader = resp;

      while let Some(chunk) = reader.chunk().await.map_err(|e| e.to_string())? {
          let chunk_str = String::from_utf8_lossy(&chunk);
          stream_buf.push_str(&chunk_str);

          while let Some(pos) = stream_buf.find('\n') {
              let line = stream_buf[..pos].to_string();
              stream_buf = stream_buf[pos + 1..].to_string();

              let trimmed = line.trim();
              if trimmed.is_empty() {
                  continue;
              }
              if trimmed.starts_with("data: ") {
                  let data = &trimmed[6..];
                  if data == "[DONE]" {
                      break;
                  }
                  if let Ok(val) = serde_json::from_str::<Value>(data) {
                      if let Some(choices) = val["choices"].as_array() {
                          if let Some(choice) = choices.get(0) {
                              let content_tok = choice["delta"]["content"].as_str().unwrap_or("");
                              let reasoning_tok = choice["delta"]["reasoning_content"].as_str().unwrap_or("");

                              if !content_tok.is_empty() {
                                  full_response.push_str(content_tok);
                                  
                                  // Determine if token is a thought based on tags
                                  let has_start = full_response.contains("<think>");
                                  let has_end = full_response.contains("</think>");
                                  let is_thought = has_start && !has_end;

                                  let _ = app.emit("boq-token", StreamPayload {
                                      token: content_tok.to_string(),
                                      is_thought,
                                  });
                              }

                              if !reasoning_tok.is_empty() {
                                  reasoning_response.push_str(reasoning_tok);
                                  let _ = app.emit("boq-token", StreamPayload {
                                      token: reasoning_tok.to_string(),
                                      is_thought: true,
                                  });
                              }
                          }
                      }
                  }
              }
          }
      }

      let _ = app.emit("boq-progress", "Tawreed Extractor received full response. Verifying semantic mapping...");

      // The remaining logic for JSON parsing remains the same.
      // Use clean_msg constructed from full_response
      let clean_msg = full_response.trim();
  ```

- [ ] **Step 4: Verify with cargo check**
  Run: `cargo check` in `src-tauri`
  Expected: Clean compilation.

---

### Task 2: Frontend State Lifting & Tauri Event Listening

**Files:**
- Modify: `src/app/page.tsx`

- [ ] **Step 1: Define ExtractionProgress interface**
  Add the interface at the top of `page.tsx`:
  ```typescript
  interface ExtractionProgress {
    status: 'idle' | 'processing' | 'success' | 'error';
    filePath: string;
    logs: string[];
    thinking: string;
    successFilePath: string;
    errorMessage: string;
  }
  ```
  Add `listen` to Tauri imports:
  ```typescript
  import { listen } from '@tauri-apps/api/event';
  ```

- [ ] **Step 2: Lift settings and extraction states to App component**
  Inside `App()` component:
  - Add state for `settings` and load it once on mount.
  - Add state for `extraction`.
  - Pass settings and extraction states as props to child components (`Workspace`, `SettingsScreen`, `HistoryScreen`).
  ```typescript
    const [settings, setSettings] = useState<SettingsConfig | null>(null);
    const [extraction, setExtraction] = useState<ExtractionProgress>({
      status: 'idle',
      filePath: '',
      logs: [],
      thinking: '',
      successFilePath: '',
      errorMessage: '',
    });

    useEffect(() => {
      invoke<SettingsConfig>('get_settings')
        .then((s) => setSettings(s))
        .catch(console.error);
    }, []);
  ```

- [ ] **Step 3: Listen to Tauri Events inside App component mount**
  Add a `useEffect` inside `App()` to manage Tauri progress and token events globally:
  ```typescript
    useEffect(() => {
      let unlistenProgress: (() => void) | null = null;
      let unlistenToken: (() => void) | null = null;

      const setup = async () => {
        unlistenProgress = await listen<string>('boq-progress', (event) => {
          setExtraction(prev => ({
            ...prev,
            logs: [...prev.logs, event.payload]
          }));
        });

        unlistenToken = await listen<{ token: string; is_thought: boolean }>('boq-token', (event) => {
          const { token, is_thought } = event.payload;
          
          setExtraction(prev => {
            // Strip structural think tags from the displayed thinking string
            let cleanToken = token;
            if (token.includes('<think>')) cleanToken = token.replace('<think>', '');
            if (token.includes('</think>')) cleanToken = token.replace('</think>', '');

            if (is_thought) {
              return {
                ...prev,
                thinking: prev.thinking + cleanToken
              };
            }
            return prev;
          });
        });
      };

      setup();

      return () => {
        if (unlistenProgress) unlistenProgress();
        if (unlistenToken) unlistenToken();
      };
    }, []);
  ```

- [ ] **Step 4: Update Workspace component signature and functions**
  Modify `Workspace` to consume lifted props:
  ```typescript
  interface WorkspaceProps {
    settings: SettingsConfig | null;
    extraction: ExtractionProgress;
    setExtraction: React.Dispatch<React.SetStateAction<ExtractionProgress>>;
  }

  function Workspace({ settings, extraction, setExtraction }: WorkspaceProps) {
  ```
  Update `selectFile` and `processFile` to interact directly with the parent state instead of local hooks:
  ```typescript
    const selectFile = async () => {
      try {
        const selected = await open({
          multiple: false,
          filters: [{ name: 'Excel', extensions: ['xlsx', 'xls'] }]
        });
        if (selected && typeof selected === 'string') {
          setExtraction(prev => ({
            ...prev,
            filePath: selected,
            status: 'idle',
            logs: [],
            thinking: '',
            successFilePath: '',
            errorMessage: ''
          }));
        }
      } catch (err) {
        console.error(err);
      }
    };

    const processFile = async () => {
      if (!extraction.filePath || !settings) return;
      
      setExtraction(prev => ({
        ...prev,
        status: 'processing',
        logs: ['Initializing extractors...'],
        thinking: '',
        successFilePath: '',
        errorMessage: ''
      }));

      try {
        const res: string = await invoke('process_boq', {
          filePath: extraction.filePath,
          baseUrl: settings.base_url,
          model: settings.model_id,
          apiKey: settings.api_key
        });
        setExtraction(prev => ({
          ...prev,
          status: 'success',
          successFilePath: res,
          logs: [...prev.logs, 'Processing complete. File ready!']
        }));
      } catch (err: unknown) {
        const errMsg = err instanceof Error ? err.message : String(err);
        setExtraction(prev => ({
          ...prev,
          status: 'error',
          errorMessage: errMsg,
          logs: [...prev.logs, `Error: ${errMsg}`]
        }));
      }
    };
  ```

- [ ] **Step 5: Lift state updates to SettingsScreen and HistoryScreen**
  Propagate settings/history hooks cleanly without duplicate reads.

---

### Task 3: Interactive UI Elements (Real-time Console & LLM Thinking)

**Files:**
- Modify: `src/app/page.tsx`

- [ ] **Step 1: Implement Collapsible Thinking accordion in Workspace UI**
  Add a gorgeous, glassmorphic real-time LLM thinking display box above status cards:
  ```typescript
          {/* Real-time LLM Thinking Card */}
          {extraction.status === 'processing' && extraction.thinking && (
            <div className="mb-6 bg-blue-500/[0.03] border border-blue-500/10 rounded-2xl p-5 backdrop-blur-md">
              <div className="flex items-center gap-2 mb-3 text-blue-400 font-semibold text-sm">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
                </span>
                <span>LLM Thinking Process</span>
              </div>
              <div className="max-h-40 overflow-y-auto font-mono text-xs text-slate-400 whitespace-pre-wrap leading-relaxed custom-scrollbar">
                {extraction.thinking}
              </div>
            </div>
          )}
  ```

- [ ] **Step 2: Add Real-time logs terminal in Workspace UI**
  Under the upload box, render a terminal console containing the live progress logs:
  ```typescript
          {/* Real-time Progress Terminal */}
          {extraction.status === 'processing' && extraction.logs.length > 0 && (
            <div className="mb-6 bg-black/40 border border-white/5 rounded-2xl p-5 font-mono text-xs text-emerald-400/90 shadow-inner">
              <div className="flex items-center justify-between border-b border-white/5 pb-2 mb-3 text-slate-500 font-sans font-medium">
                <span>Console Logs</span>
                <span className="animate-pulse">Active</span>
              </div>
              <div className="max-h-32 overflow-y-auto space-y-1.5 custom-scrollbar">
                {extraction.logs.map((log, index) => (
                  <div key={index} className="flex gap-2 items-start">
                    <span className="text-slate-600 select-none">&gt;</span>
                    <span>{log}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
  ```

- [ ] **Step 3: Update success and error messages to use lifted state**
  Replace `message` with `extraction.logs[extraction.logs.length - 1]` or `extraction.errorMessage`.

- [ ] **Step 4: Verify Next.js compilation and build**
  Run: `npm run build` or `npx next build`
  Expected: Clean compilation.
