# Tawreed Launch Video Design

## Goal
Create a story-driven promotional video to launch the Tawreed product, focusing on the pain points of QS engineers and how Tawreed's AI automation solves them. 

## Approach
**"Data Chaos to Clarity"**
Visualizing the messy data (PDFs, disorganized text) transforming dynamically into clean, glassmorphic UI cards powered by Tawreed. The video will feature a professional Arabic voiceover.

## Structure and Script

### Scene 1: The Problem (Chaos)
- **Visuals:** Dark background with red/orange accents. Disorganized floating icons (PDF, Excel, Word) and messy text blocks overlapping, simulating a chaotic desktop.
- **Audio (VO):** "مهندس التسعير، كم ساعة تضيع في تفريغ جداول الكميات؟"
  *(Estimation engineer, how many hours are wasted extracting BOQs?)*
- **Timing:** ~0.0s - 4.0s

### Scene 2: The Escalation
- **Visuals:** The documents stack up and shake slightly, increasing in density. The screen feels overwhelming.
- **Audio (VO):** "ملفات معقدة، صيغ مختلفة، وأخطاء بشرية مكلفة."
  *(Complex files, different formats, and costly human errors.)*
- **Timing:** ~4.0s - 8.0s

### Scene 3: The Solution (Tawreed)
- **Visuals:** A glowing sweep (shader or light effect) cleans the screen. A sleek, glassmorphic Tawreed UI card appears smoothly with a blue/teal accent.
- **Audio (VO):** "توريد يغير قواعد اللعبة. بالذكاء الاصطناعي، نحول الفوضى إلى بيانات منظمة في ثوانٍ."
  *(Tawreed changes the game. With AI, we turn chaos into structured data in seconds.)*
- **Timing:** ~8.0s - 14.0s

### Scene 4: The Features
- **Visuals:** Clean, glowing text rows slide perfectly into a structured Excel grid.
- **Audio (VO):** "دقة متناهية، واجهة عصرية، وتكامل تام مع سير عملك."
  *(Ultimate accuracy, a modern interface, and perfect integration with your workflow.)*
- **Timing:** ~14.0s - 19.0s

### Scene 5: Call to Action
- **Visuals:** Tawreed Logo, verified icon, and "ابدأ الآن" (Start Now) in bold typography.
- **Audio (VO):** "وفر وقتك، ضاعف إنتاجيتك. حمل توريد الآن."
  *(Save your time, double your productivity. Download Tawreed now.)*
- **Timing:** ~19.0s - 23.0s

## Technical Details
- **Technology:** HyperFrames HTML composition
- **Voiceover:** Kokoro TTS (Arabic, professional tone, via hyperframes-media `tts` command)
- **Transcription/Captions:** Whisper transcription to generate precise timing (via hyperframes-media `transcribe` command)
- **Typography:** Arabic fonts (e.g. Cairo, Tajawal, or user's preference)
- **Styling:** Vanilla CSS, glassmorphism, dark theme with blue/teal highlights for the solution, red/orange for the problem.
- **Animation:** GSAP for UI motions, possibly WebGL for the sweep transition.

## Validation
- Ensure no visual overflow via `npx hyperframes inspect`
- Validate contrast ratios with `npx hyperframes validate`
- Produce deterministic animations with `Math.random()` forbidden.
