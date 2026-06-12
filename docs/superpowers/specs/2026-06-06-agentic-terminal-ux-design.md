# Slab Agent UX & Robust JSON Architecture

## Architecture Overview
The system will implement a real-time event pipeline between the Rust backend and React frontend to provide deep visibility into the BOQ processing state, utilizing agentic terminology. Additionally, the backend JSON parser will be hardened to survive hallucinated markdown blocks or conversational text from the LLM.

## Rust Backend
1. **Tauri Event Emitter:** 
   - `AppHandle` will be passed into `process_boq` and `processor::slice_boq`.
   - `app.emit("boq-progress", "message")` will be used to stream state updates.
2. **Robust JSON Extraction:**
   - The LLM response will be scanned for the first `{` and the last `}`.
   - Only the substring bounded by these brackets will be parsed by `serde_json`, entirely stripping out any hallucinated markdown (like ````json`) or conversational filler.

## React Frontend
1. **Event Listener:**
   - `listen('boq-progress')` from `@tauri-apps/api/event` will append logs to a state array.
2. **Terminal UI:**
   - A minimalist, Framer Motion-animated console box will appear below the CTA button during execution.
   - Logs will be displayed in real-time, scrolling automatically.

## Terminology
All logs will use highly skilled agentic phrasing:
- "Initializing Slab Agent..."
- "Slab Agent extracting context from workbook..."
- "Slab Agent reasoning over categorization..."
- "Slab Agent verifying semantic mapping..."
