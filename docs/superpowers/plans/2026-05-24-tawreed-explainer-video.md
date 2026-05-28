# Tawreed Explainer Video Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a high-fidelity 65-second explainer video (`tawreed_explainer.mp4`) using HyperFrames, demonstrating what Tawreed is and how to use it, with an AI settings setup, drag-and-drop workspace flow, diagnostics view check, styled Excel takeoff output, and a professional male voiceover (`am_adam`).

**Architecture:** We will set up a new HyperFrames project in the `video-explainer` directory. We'll generate a unified voiceover using Kokoro TTS (`am_adam` voice), transcribe it with Whisper to obtain precise word-level timestamps (`transcript.json`), and build a beautiful HTML structure with CSS glassmorphism cards and GSAP timeline animations synced to the audio track.

**Tech Stack:** HyperFrames CLI, GSAP, Kokoro TTS, Whisper Transcription, HTML/CSS.

---

## File Structure

The project will live in `video-explainer/` with the following files:
- `video-explainer/package.json` [NEW]: Scaffolds dependencies and CLI run scripts.
- `video-explainer/script.txt` [NEW]: The narrative script for the voiceover narrator.
- `video-explainer/assets/music.mp3` [NEW]: Background music track.
- `video-explainer/assets/icon.png` [NEW]: App logo icon.
- `video-explainer/assets/gsap.min.js` [NEW]: GSAP animation library.
- `video-explainer/assets/voiceover.wav` [NEW]: Generated narration file from Kokoro.
- `video-explainer/assets/transcript.json` [NEW]: Timestamped transcript from Whisper.
- `video-explainer/index.html` [NEW]: The HTML structure, composition layout, scenes, and subtitles.
- `video-explainer/style.css` [NEW]: Signature dark glassmorphic styles and custom layout animations.
- `video-explainer/script.js` [NEW]: The animation controller registering GSAP timelines linked to HyperFrames seek events.

---

### Task 1: Scaffolding the Explainer Project

**Files:**
- Create: `video-explainer/package.json`
- Create: `video-explainer/script.txt`
- Copy: `video-explainer/assets/music.mp3` (from `video-teaser/assets/music.mp3`)
- Copy: `video-explainer/assets/icon.png` (from `video-teaser/assets/icon.png`)
- Copy: `video-explainer/assets/gsap.min.js` (from `video-teaser/assets/gsap.min.js`)

- [ ] **Step 1: Write `package.json`**
  Write package dependencies and preview/render/tts scripts.
- [ ] **Step 2: Write `script.txt`**
  Write the approved explainer narrative text.
- [ ] **Step 3: Copy assets**
  Copy `music.mp3`, `icon.png`, and `gsap.min.js` from `video-teaser` using standard commands.
- [ ] **Step 4: Commit**
  ```bash
  git add video-explainer/package.json video-explainer/script.txt
  git commit -m "chore: scaffold video-explainer project directory and scripts"
  ```

---

### Task 2: Audio & Transcription Preprocessing

**Files:**
- Create: `video-explainer/assets/voiceover.wav`
- Create: `video-explainer/assets/transcript.json`

- [ ] **Step 1: Generate voiceover using Kokoro TTS**
  Run: `npx hyperframes tts video-explainer/script.txt --voice am_adam --output video-explainer/assets/voiceover.wav`
  Verify that the `.wav` file is successfully generated.
- [ ] **Step 2: Transcribe voiceover using Whisper**
  Run: `npx hyperframes transcribe video-explainer/assets/voiceover.wav --model small.en`
  This generates `video-explainer/assets/transcript.json` (Whisper model cache path: `~/.cache/hyperframes/`).
- [ ] **Step 3: Commit**
  ```bash
  git add video-explainer/assets/voiceover.wav video-explainer/assets/transcript.json
  git commit -m "media: generate voiceover wav and transcribe transcript json"
  ```

---

### Task 3: HTML & CSS Structure (Layout & Glassmorphic Scenes)

**Files:**
- Create: `video-explainer/index.html`
- Create: `video-explainer/style.css`

- [ ] **Step 1: Create `style.css`**
  Implement the core design system (charcoal background, glassmorphism panel styles, orange text colors, and layouts).
- [ ] **Step 2: Create `index.html`**
  Write the core document layout: composition viewport, background layer, audio tracks (`voiceover.wav` and `music.mp3`), subtitles/caption tracks, and scenes/mockups.
- [ ] **Step 3: Verify structure with linter**
  Run `npx hyperframes lint` inside `video-explainer` directory to verify document validity.
- [ ] **Step 4: Commit**
  ```bash
  git add video-explainer/index.html video-explainer/style.css
  git commit -m "feat: design explainer views, glass cards, and layouts"
  ```

---

### Task 4: GSAP Animation Controller

**Files:**
- Create: `video-explainer/script.js`

- [ ] **Step 1: Write `script.js`**
  Write GSAP timelines registering on `window.__hfTimeline` for seek-driven frame processing.
- [ ] **Step 2: Animate Scenes**
  Coordinate slide transitions, dropdown selectors, upload dropzone ripples, terminal diagnostic lines, and Excel success stats reveals based on the timeline.
- [ ] **Step 3: Commit**
  ```bash
  git add video-explainer/script.js
  git commit -m "feat: implement GSAP animations and scene timeline controller"
  ```

---

### Task 5: Testing, Previewing, and Rendering

**Files:**
- Output: `video-explainer/tawreed_explainer.mp4`

- [ ] **Step 1: Preview the video**
  Run `npx hyperframes preview` inside `video-explainer` to inspect the visual rendering of the slides.
- [ ] **Step 2: Render final MP4**
  Run `npx hyperframes render --output tawreed_explainer.mp4 --quality high` inside the `video-explainer` folder.
- [ ] **Step 3: Commit**
  ```bash
  git add video-explainer/tawreed_explainer.mp4
  git commit -m "build: render final explainer MP4 video"
  ```
