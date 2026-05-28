# Design Spec: Tawreed Explainer Video

This document outlines the design, script, visual layouts, and rendering workflow for the Tawreed AI-powered BOQ extraction explainer video.

## Goal
Explain **what Tawreed is** and **how to use it** in a sleek, high-fidelity 65-second video created using HyperFrames, utilizing a professional male voiceover and matching the application's signature dark glassmorphic styling.

---

## Visual & Color Theme
- **Theme**: Sleek Dark Mode with Glassmorphism
- **Background Color**: Dark charcoal/black (`#0b0c10` / `#121212`)
- **Accent Color**: Tawreed Orange (`#d35400` / `#ff6b00`)
- **Text Primary**: White (`#ffffff`)
- **Text Secondary**: Muted Grey (`#a0aec0`)
- **Card Background**: Semi-transparent dark glass (`rgba(30, 30, 35, 0.4)`) with backdrop blur (`blur(16px)`) and subtle border (`1px solid rgba(255, 255, 255, 0.08)`)

---

## Audio Assets
1. **Voiceover**: Generated via Kokoro TTS using the clear American male narrator voice (`am_adam`).
2. **Background Music**: Loopable soft tech corporate track loaded from local assets.

---

## Scene Breakdown & Timings

### Scene 1: Intro (0:00 - 0:10)
- **Voiceover**: *"Dealing with messy, unstructured Bills of Quantities and procurement files? Meet Tawreed, a local-first desktop assistant designed to automate material takeoff using AI."*
- **Visuals**: Left side: Tilted messy BOQ scan with red highlights. Right side: Glowing logo and structured cards. Scanning laser line sweeps across.
- **Text Overlay**: "Tawreed (توريد)" / "AI-Powered Takeoff & Material Extraction"

### Scene 2: Setup (0:10 - 0:22)
- **Voiceover**: *"Getting started is simple. Navigate to AI Settings, choose your preferred LLM provider like Google Gemini, paste your API key, and hit save."*
- **Visuals**: A glassmorphic card representing the AI settings panel. Dropdown clicks, API key input fills with dots, and "Save Settings" button clicks with a green toast notification.

### Scene 3: Workspace & Ingestion (0:22 - 0:35)
- **Voiceover**: *"Next, head to the Workspace. Drag and drop any Excel, Word, PDF, or even a scanned sheet. Select your target language—like bilingual English and Arabic—and start the extraction."*
- **Visuals**: Workspace view with a dashed dropzone. A document icon drops in with a ripple. Language selector changes to "Bilingual", and the "Start Extraction Job" button clicks down.

### Scene 4: Diagnostics (0:35 - 0:48)
- **Voiceover**: *"Tawreed doesn't just parse text—its AI engine maps and groups materials, validates JSON output, and automatically repairs any formatting anomalies. You can inspect all system prompts and repair logs in the Diagnostics view."*
- **Visuals**: A progress bar completes. View switches to the Diagnostics screen, highlighting the "Clean JSON" and "Repair Logs" tabs with auto-repair terminal scrolling.

### Scene 5: Structured Excel Output (0:48 - 0:58)
- **Voiceover**: *"In seconds, your structured, bilingual Excel workbook is ready—fully formatted in Tawreed's signature theme and grouped into clean estimation packages."*
- **Visuals**: Success card with counting metrics. Behind it, a mock Excel spreadsheet with orange/dark headers and Arabic/English columns zooms in.

### Scene 6: Outro (0:58 - 1:05)
- **Voiceover**: *"Take control of your procurement workflows. Download Tawreed today and bid smarter."*
- **Visuals**: Center logo, Kareem Safwat signature, and "Download Tawreed" button pulsing.

---

## Spec Self-Review
- **Placeholder check**: No "TBD" or placeholders are present.
- **Consistency**: Timing sequences are continuous and total exactly 65 seconds.
- **Feasibility**: All visual UI items are standard HTML/CSS templates easily animatable with GSAP or CSS keyframes within HyperFrames.
