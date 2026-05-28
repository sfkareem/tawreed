# Spec: Tawreed Teaser Marketing Video

Build a 60-second teaser marketing video for Tawreed using HyperFrames. The video will be styled with Tawreed's brand identity, powered by an AI-generated voiceover, and will include word-level synchronized subtitles.

---

## 1. Composition Settings & Architecture

*   **Aspect Ratio**: Landscape (`16:9`, `1920x1080` resolution).
*   **Duration**: Exactly `60 seconds` (`1800 frames` at `30 FPS`).
*   **Directory Structure**: All video files will be created in a new dedicated directory `video-teaser/`:
    ```
    video-teaser/
      ├── index.html            # Main HyperFrames markup
      ├── style.css             # Main styling, layout grids, and visual theme
      ├── script.js             # GSAP animation timeline logic
      ├── package.json          # Node script commands
      ├── assets/
      │     ├── icon.png        # Copy of Tawreed app icon
      │     └── voiceover.wav   # Generated Kokoro TTS voiceover audio
      └── transcript.json       # Whisper auto-transcribed word timestamps
    ```

---

## 2. Visual Theme & Brand Standards

*   **Base Theme**: Dark mode only. Base canvas background color is `#0f0f15`.
*   **Ambient Glow Elements**: Soft radial gradient backing circles:
    *   Primary: HSL Rust Orange (`hsla(22, 100%, 41%, 0.12)`)
    *   Accent: HSL Sun Yellow (`hsla(37, 90%, 50%, 0.08)`)
*   **UI Components**: Glassmorphism cards with `background: rgba(26, 26, 38, 0.7)`, `backdrop-filter: blur(12px)`, and borders in `rgba(255, 255, 255, 0.08)`.
*   **Typography**:
    *   Titles/Headings: `Outfit` (sans-serif, weights `500`/`700`/`800`).
    *   Body text & UI elements: `Inter` (sans-serif, weights `400`/`500`/`600`).
*   **Tawreed Signature Theme Excel Mockup**:
    *   Table Headers: Rust Orange `#d35400` with white text.
    *   Bilingual column titles: English / Arabic text (e.g., `Material Name (EN) / اسم المادة`).
    *   Price Cells: Soft blue text (`#0000ff`) for user pricing inputs.
    *   Auto-wrapped cells with double bottom total borders.

---

## 3. Video Script & Narrative Timeline

### Scene 1: The Pain (0s – 10s / Frames 0 – 300)
*   **Visuals**: A cluttered client BOQ spreadsheet mockup titled `client_boq_v3_draft.xlsx` floating in the center. Highlight three warning badges showing formula errors (`#REF!`, `#VALUE!`, `#DIV/0!`) that pop up one by one.
*   **Voiceover**: *"Struggling with messy, unformatted client Bills of Quantities? Scattered text, inconsistent layouts, and broken formulas make cost estimation a slow, manual nightmare."*
*   **Transitions**:
    *   **0.0s – 1.0s**: Fades in.
    *   **2.0s**: `#REF!` error badge pops up.
    *   **4.5s**: `#VALUE!` error badge pops up.
    *   **7.0s**: `#DIV/0!` error badge pops up.

### Scene 2: Simple Ingestion (10s – 23s / Frames 300 – 690)
*   **Visuals**: Scene 1 slides up. The Tawreed app shell enters. A virtual mouse cursor moves, selects a file, drags it to the dropzone, and clicks **Start Extraction**. A progress bar fills from 0% to 100% while a step-by-step checklist ticks off (Read file, Query AI, Validate, Format).
*   **Voiceover**: *"Enter Tawreed. Just drag and drop any BOQ, PDF, or scanned sheet. Our AI engine instantly reads, extracts, and organizes materials into structured packages in seconds."*
*   **Transitions**:
    *   **10.0s**: App shell enters.
    *   **12.0s**: Mouse cursor selects and drops `sample_boq.xlsx`.
    *   **15.0s**: Mouse clicks "Start Extraction Job".
    *   **15.5s – 21.0s**: Progress bar fills.
    *   **21.0s – 23.0s**: Extraction success card triggers.

### Scene 3: Deep Diagnostics (23s – 38s / Frames 690 – 1140)
*   **Visuals**: Navigation active line slides from "Workspace" to "Diagnostics". The virtual mouse clicks through tabs: **System Prompt**, **Clean JSON** (scrolls JSON data), and **Repair Logs** (shows processing checkmarks).
*   **Voiceover**: *"Get complete transparency under the hood. Review the system instructions, inspect the validated clean JSON, and track real-time repair logs to ensure 100% data integrity."*
*   **Transitions**:
    *   **23.0s**: Active nav tab changes. Diagnostics view opens.
    *   **25.0s**: Clicks "System Prompt".
    *   **29.0s**: Clicks "Clean JSON" (triggers automatic pre-tag scrolling).
    *   **34.0s**: Clicks "Repair Logs".

### Scene 4: The Signature Takeoff (38s – 50s / Frames 1140 – 1500)
*   **Visuals**: Diagnostics view fades out, showing the Workspace success card. Mouse clicks **Open Excel File**, and a pristine Excel sheet titled `Tawreed_Takeoff_BOQ_Final.xlsx` flies up from the bottom. It features the Rust Orange header, bilingual content, and blue rate inputs. The cursor clicks the bottom sheet tab "Fit-out BOQ" to show the detailed items list.
*   **Voiceover**: *"The result? A professional, client-ready takeoff workbook. Formatted in Tawreed's signature theme with bilingual columns and clean quantities, ready for your estimating team."*
*   **Transitions**:
    *   **38.0s**: Success card returns.
    *   **40.0s**: Clicks "Open Excel File".
    *   **41.0s**: Excel sheet mockup flies in overlaying the app canvas.
    *   **46.0s**: Clicks "Fit-out BOQ" sheet tab.

### Scene 5: Outro & Call to Action (50s – 60s / Frames 1500 – 1800)
*   **Visuals**: Excel sheet slides down. Large glowing Tawreed package icon scales up with a pulsing orange aura. Tagline *"Build Faster, Bid Smarter"* and CTA link fade/slide in.
*   **Voiceover**: *"Stop wasting hours on manual takeoff entries. Build faster, bid smarter. Get started with Tawreed today."*
*   **Transitions**:
    *   **50.0s**: Excel slides down. Logo scales and fades in.
    *   **52.0s**: Tagline slides up.
    *   **54.0s**: CTA button and URL fade in.
    *   **58.0s – 60.0s**: Canvas fades to black.

---

## 4. Subtitles & Synced Captioning

*   Subtitles will be rendered as a floating, glassmorphic bottom overlay.
*   Word-level synchronization is driven by generating the audio file `voiceover.wav` and running `hyperframes transcribe` to output `transcript.json`.
*   We will import and parse `transcript.json` to dynamically toggle active word markers (underlining or color-sweeps) inside the subtitle block.

---

## 5. Technical Implementation Checklist

1.  **TTS Generation**: Create `script.txt` with the voiceover text and run `npx hyperframes tts script.txt --voice af_nova --output video-teaser/assets/voiceover.wav`.
2.  **Transcription**: Run `npx hyperframes transcribe video-teaser/assets/voiceover.wav` to create `video-teaser/transcript.json`.
3.  **HTML Layout**: Write static HTML representing each visual state in `video-teaser/index.html`.
4.  **CSS Styling**: Add design system styles, layouts, card metrics, and fonts in `video-teaser/style.css`.
5.  **GSAP Timeline**: Construct the full sequential animation timeline inside `video-teaser/script.js`, registering `window.__timelines["tawreed-teaser"]`.
6.  **Verification**: Run `npx hyperframes lint` and `npx hyperframes validate` to verify timing compatibility and contrast compliance.

---

## 6. Verification Plan

### Automated Checks
*   `npx hyperframes lint`: Enforces HTML, CSS, and timing format validations.
*   `npx hyperframes validate`: Audits the layout at sample intervals for WCAG contrast compliance.
*   `npx hyperframes inspect`: Headless Chrome render inspection to catch overlay collisions or text overflow.

### Manual Verification
*   `npx hyperframes preview`: Local browser preview validation.
*   `npx hyperframes render`: Build the final `.mp4` file and review transitions, audio/video alignment, and overall pacing.
