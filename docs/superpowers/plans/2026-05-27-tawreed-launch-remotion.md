# Tawreed Launch Video Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the Tawreed launch video using the Remotion React video-editing framework, preserving the high-end dark slate and rust-orange visual aesthetic and syncing it perfectly to the voiceover narration.

**Architecture:** A central Remotion composition `TawreedLaunch` manages the global timeline, audio tracks, and caption overlays. Each of the 8 scenes is implemented as a modular React component in `src/scenes/` placed on the timeline via `<Sequence>` tags.

**Tech Stack:** React, Remotion (`remotion`, `@remotion/media`), `@remotion/google-fonts`, Vanilla CSS.

---

### Task 1: Project Initialization & Asset Relocation

**Files:**
- Create/Modify: `video-launch/package.json`
- Create/Modify: `video-launch/src/Root.tsx`
- Delete: `video-launch/index.html`, `video-launch/style.css`

- [ ] **Step 1: Backup and move assets to `public/assets`**
  Move `video-launch/assets/` to a temporary location, clean up the `video-launch/` folder, then create a new `public/assets/` folder and place the assets there.
  Run:
  ```powershell
  mkdir temp_assets
  Move-Item video-launch/assets/* temp_assets/
  Remove-Item video-launch/* -Recurse -Exclude temp_assets
  mkdir video-launch/public/assets
  Move-Item temp_assets/* video-launch/public/assets/
  Remove-Item temp_assets -Recurse
  ```
  Expected: Folder `video-launch` is cleared, and assets are now under `video-launch/public/assets/`.

- [ ] **Step 2: Scaffold a blank Remotion project**
  Run the `create-video` tool to scaffold a blank, non-Tailwind Remotion project inside `video-launch`.
  Run:
  ```powershell
  npx create-video@latest --yes --blank --no-tailwind video-launch
  ```
  Expected: Scaffolding finishes successfully, generating new files like `video-launch/package.json` and a clean `src/` directory.

- [ ] **Step 3: Install necessary Remotion Google Fonts packages**
  Run npm installs for the Google Fonts adapter.
  Run:
  ```powershell
  cd video-launch
  npm install @remotion/google-fonts
  ```
  Expected: `@remotion/google-fonts` is added to `package.json` dependencies.

- [ ] **Step 4: Commit the initial setup**
  Run:
  ```bash
  git add video-launch/package.json video-launch/public/
  git commit -m "chore: scaffold blank remotion project and migrate audio/image assets"
  ```
  Expected: Commit completes successfully.

---

### Task 2: Core configuration and Font loaders

**Files:**
- Create: `video-launch/src/index.css`
- Create: `video-launch/src/Root.tsx`
- Create: `video-launch/src/TawreedLaunch.tsx`

- [ ] **Step 1: Create global stylesheet `src/index.css`**
  Write the standard design system CSS tokens and rules to `video-launch/src/index.css`.
  Code:
  ```css
  :root {
    --bg-base: #0f0f15;
    --bg-surface: rgba(26, 26, 38, 0.75);
    --brand-primary: #d35400;
    --brand-hover: #e67e22;
    --brand-accent: #f39c12;
    --brand-glow: rgba(211, 84, 0, 0.25);
    --text-primary: #f5f6fa;
    --text-secondary: #a0a5c1;
    --text-muted: #676b85;
    --success: #2ecc71;
    --danger: #e74c3c;
    --warning: #f1c40f;
  }

  body {
    background-color: var(--bg-base);
    color: var(--text-primary);
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Plus Jakarta Sans', sans-serif;
    -webkit-font-smoothing: antialiased;
  }

  .scene {
    position: absolute;
    width: 1920px;
    height: 1080px;
    overflow: hidden;
    background-color: var(--bg-base);
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .scene-content {
    position: relative;
    width: 100%;
    height: 100%;
    overflow: hidden;
  }

  /* Shared decoratives styles */
  .deco-glow {
    position: absolute;
    border-radius: 50%;
    filter: blur(100px);
    pointer-events: none;
    z-index: 1;
  }

  .deco-ghost {
    position: absolute;
    font-family: 'Cairo', sans-serif;
    font-weight: 900;
    font-size: 280px;
    color: rgba(255, 255, 255, 0.02);
    pointer-events: none;
    user-select: none;
    z-index: 1;
  }

  .deco-line {
    position: absolute;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--brand-primary), transparent);
    z-index: 2;
  }

  .scene-label {
    position: absolute;
    top: 60px;
    left: 80px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 18px;
    font-weight: 700;
    color: var(--text-muted);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    z-index: 10;
  }
  ```

- [ ] **Step 2: Create Root wrapper with Font Loaders**
  Write the composition definitions and Google Font loader logic inside `video-launch/src/Root.tsx`.
  Code:
  ```tsx
  import { Composition, continueRender, delayRender } from "remotion";
  import { loadFont as loadCairo } from "@remotion/google-fonts/Cairo";
  import { loadFont as loadPlusJakarta } from "@remotion/google-fonts/PlusJakartaSans";
  import { loadFont as loadJetBrains } from "@remotion/google-fonts/JetBrainsMono";
  import { TawreedLaunch } from "./TawreedLaunch";
  import "./index.css";

  // Delay render until fonts are loaded
  const waitForCairo = delayRender();
  loadCairo({ weights: ["900"] }).then(() => continueRender(waitForCairo));

  const waitForPlusJakarta = delayRender();
  loadPlusJakarta({ weights: ["500", "800"] }).then(() => continueRender(waitForPlusJakarta));

  const waitForJetBrains = delayRender();
  loadJetBrains({ weights: ["600", "700"] }).then(() => continueRender(waitForJetBrains));

  export const RemotionRoot = () => {
    return (
      <Composition
        id="TawreedLaunch"
        component={TawreedLaunch}
        durationInFrames={2700} // 90 seconds @ 30 fps
        fps={30}
        width={1920}
        height={1080}
      />
    );
  };
  ```

- [ ] **Step 3: Create coordinator component `src/TawreedLaunch.tsx`**
  Write the parent composition containing audio components and empty placeholder scene sequences.
  Code:
  ```tsx
  import { AbsoluteFill, Audio, staticFile } from "remotion";

  export const TawreedLaunch = () => {
    return (
      <AbsoluteFill style={{ backgroundColor: "#0f0f15", overflow: "hidden" }}>
        {/* Audio Mixing */}
        <Audio src={staticFile("assets/narration.wav")} volume={1.0} />
        <Audio src={staticFile("assets/music.mp3")} volume={0.15} />

        {/* Temporary Placeholder scene display */}
        <AbsoluteFill style={{ display: "flex", justifyContent: "center", alignItems: "center" }}>
          <h1 style={{ fontFamily: "Cairo", fontSize: 48, color: "#d35400" }}>Tawreed Launch Video Placeholder</h1>
        </AbsoluteFill>
      </AbsoluteFill>
    );
  };
  ```

- [ ] **Step 4: Commit Core setup**
  Run:
  ```bash
  git add video-launch/src/
  git commit -m "feat: implement global CSS, Google Font loader, and Root composition setup"
  ```

---

### Task 3: Shared Captions Component

**Files:**
- Create: `video-launch/src/components/Captions.tsx`
- Modify: `video-launch/src/TawreedLaunch.tsx`

- [ ] **Step 1: Write Captions Component**
  Create a dynamic captions overlay that tracks current frames and displays formatted text with orange highlights.
  Code:
  ```tsx
  import { useCurrentFrame } from "remotion";

  interface Caption {
    text: string;
    startFrame: number;
    endFrame: number;
    highlight: string;
  }

  const captionsData: Caption[] = [
    { text: "How many hours do you waste manually processing Bills of Quantities?", startFrame: 9, endFrame: 135, highlight: "Bills of Quantities" },
    { text: "Eight hours or more... for a single file.", startFrame: 138, endFrame: 225, highlight: "Eight hours" },
    { text: "Complex documents in different formats...", startFrame: 255, endFrame: 345, highlight: "different formats" },
    { text: "PDFs, Excel sheets, Word files, and even scanned images.", startFrame: 348, endFrame: 450, highlight: "scanned images" },
    { text: "Costly human errors every single time.", startFrame: 453, endFrame: 555, highlight: "human errors" },
    { text: "But now... Tawreed changes the equation completely.", startFrame: 624, endFrame: 735, highlight: "Tawreed" },
    { text: "Tawreed is an intelligent desktop app for QS & Procurement.", startFrame: 738, endFrame: 870, highlight: "QS & Procurement" },
    { text: "Upload any document in any format.", startFrame: 915, endFrame: 1035, highlight: "any document" },
    { text: "The system handles everything automatically.", startFrame: 1038, endFrame: 1140, highlight: "everything automatically" },
    { text: "Extracts materials, quantities, and specifications.", startFrame: 1290, endFrame: 1425, highlight: "specifications" },
    { text: "Detects errors and repairs them automatically.", startFrame: 1428, endFrame: 1560, highlight: "repairs them automatically" },
    { text: "Choose your AI: Gemini, GPT, or Claude.", startFrame: 1575, endFrame: 1680, highlight: "Gemini" },
    { text: "A professional bilingual takeoff workbook.", startFrame: 1695, endFrame: 1860, highlight: "bilingual takeoff" },
    { text: "Ready to export instantly.", startFrame: 1875, endFrame: 1980, highlight: "Ready to export" },
    { text: "10x faster. Zero errors. 6+ formats.", startFrame: 2055, endFrame: 2220, highlight: "10x" },
    { text: "Download Tawreed now.", startFrame: 2355, endFrame: 2520, highlight: "Tawreed" },
  ];

  export const Captions = () => {
    const frame = useCurrentFrame();
    const active = captionsData.find((c) => frame >= c.startFrame && frame < c.endFrame);

    if (!active) return null;

    const renderText = (text: string, highlight: string) => {
      if (!highlight || !text.includes(highlight)) return text;
      const parts = text.split(highlight);
      return (
        <>
          {parts[0]}
          <span style={{ color: "#d35400", fontWeight: 800 }}>{highlight}</span>
          {parts[1]}
        </>
      );
    };

    return (
      <div style={{
        position: "absolute",
        bottom: 80,
        left: 0,
        right: 0,
        display: "flex",
        justifyContent: "center",
        zIndex: 100,
        pointerEvents: "none"
      }}>
        <div style={{
          background: "rgba(15, 15, 21, 0.85)",
          padding: "20px 40px",
          borderRadius: "40px",
          border: "1px solid rgba(255,255,255,0.08)",
          fontFamily: "Plus Jakarta Sans",
          fontSize: 36,
          fontWeight: 600,
          color: "#f5f6fa",
          textAlign: "center",
          maxWidth: "1200px",
          boxShadow: "0 20px 50px rgba(0,0,0,0.5)",
          backdropFilter: "blur(10px)"
        }}>
          {renderText(active.text, active.highlight)}
        </div>
      </div>
    );
  };
  ```

- [ ] **Step 2: Add Captions to the root layout**
  Update `video-launch/src/TawreedLaunch.tsx` to include the Captions component.
  Code:
  ```tsx
  import { AbsoluteFill, Audio, staticFile } from "remotion";
  import { Captions } from "./components/Captions";

  export const TawreedLaunch = () => {
    return (
      <AbsoluteFill style={{ backgroundColor: "#0f0f15", overflow: "hidden" }}>
        {/* Audio Mixing */}
        <Audio src={staticFile("assets/narration.wav")} volume={1.0} />
        <Audio src={staticFile("assets/music.mp3")} volume={0.15} />

        {/* Captions Overlay */}
        <Captions />
      </AbsoluteFill>
    );
  };
  ```

- [ ] **Step 3: Commit Captions**
  Run:
  ```bash
  git add video-launch/src/components/Captions.tsx video-launch/src/TawreedLaunch.tsx
  git commit -m "feat: implement dynamic synchronized captions component"
  ```

---

### Task 4: Implementing Scenes 1-3

**Files:**
- Create: `video-launch/src/scenes/Scene1.tsx`
- Create: `video-launch/src/scenes/Scene2.tsx`
- Create: `video-launch/src/scenes/Scene3.tsx`
- Modify: `video-launch/src/TawreedLaunch.tsx`

- [ ] **Step 1: Implement Scene 1 (Hook, frames 0 to 240)**
  Code:
  ```tsx
  import { useCurrentFrame, interpolate, Easing } from "remotion";

  export const Scene1 = () => {
    const frame = useCurrentFrame();

    // Blur Transition
    const opacity = interpolate(frame, [0, 15, 225, 240], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    const blur = interpolate(frame, [0, 15, 225, 240], [12, 0, 0, 12], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    const scale = interpolate(frame, [0, 15, 225, 240], [0.97, 1, 1, 1.03], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

    // Counter animation (0 to 8+)
    const counterVal = interpolate(frame, [60, 105], [0, 8], {
      extrapolateRight: "clamp",
      easing: Easing.out(Easing.quad)
    });

    return (
      <div className="scene" style={{ opacity, filter: `blur(${blur}px)`, transform: `scale(${scale})` }}>
        <div className="scene-content">
          <div className="deco-glow" style={{ width: 500, height: 500, background: "rgba(211,84,0,0.08)", top: "30%", left: "35%" }}></div>
          <div className="deco-ghost" style={{ top: "15%", left: "-5%", transform: "rotate(-5deg)" }}>BOQ</div>
          <div className="deco-line" style={{ top: 120, left: 200, width: 300 }}></div>
          <span className="scene-label">QS Workflow Analysis</span>

          <div style={{
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            alignItems: "center",
            height: "100%",
            textAlign: "center",
            padding: "0 200px"
          }}>
            <div style={{
              fontFamily: "JetBrains Mono",
              fontSize: 18,
              fontWeight: 700,
              color: "#d35400",
              textTransform: "uppercase",
              letterSpacing: "0.2em",
              marginBottom: 20
            }}>The Problem</div>
            <h1 style={{
              fontFamily: "Cairo",
              fontSize: 80,
              fontWeight: 900,
              margin: 0,
              lineHeight: 1.2
            }}>How many hours do you waste manually processing Bills of Quantities?</h1>
            <div style={{
              display: "flex",
              alignItems: "center",
              gap: 20,
              marginTop: 40
            }}>
              <span style={{
                fontFamily: "Cairo",
                fontSize: 120,
                fontWeight: 900,
                color: "#d35400",
                fontVariantNumeric: "tabular-nums"
              }}>{Math.round(counterVal)}+</span>
              <span style={{
                fontFamily: "Plus Jakarta Sans",
                fontSize: 36,
                fontWeight: 800,
                color: "#a0a5c1"
              }}>hours per file</span>
            </div>
          </div>
        </div>
      </div>
    );
  };
  ```

- [ ] **Step 2: Implement Scene 2 (Chaos, frames 240 to 600)**
  Code:
  ```tsx
  import { useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";

  export const Scene2 = () => {
    const frame = useCurrentFrame();
    const { fps } = useVideoConfig();

    const opacity = interpolate(frame, [0, 15, 345, 360], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    const blur = interpolate(frame, [0, 15, 345, 360], [12, 0, 0, 12], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    const scale = interpolate(frame, [0, 15, 345, 360], [0.97, 1, 1, 1.03], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

    // Floating animation
    const floatOffset = Math.sin(frame / 15) * 8;

    const renderCard = (title: string, format: string, error: string, style: React.CSSProperties, stagger: number) => {
      const cardSpring = spring({
        frame: frame - stagger,
        fps,
        config: { damping: 15, mass: 0.8 }
      });

      const cardOpacity = interpolate(cardSpring, [0, 1], [0, 1]);
      const cardScale = interpolate(cardSpring, [0, 1], [0.5, 1]);
      const cardZ = interpolate(cardSpring, [0, 1], [-800, 0]);

      return (
        <div style={{
          position: "absolute",
          width: 320,
          background: "rgba(26, 26, 38, 0.75)",
          borderRadius: 16,
          border: "1px solid rgba(231, 76, 60, 0.2)",
          padding: 24,
          boxShadow: "0 20px 40px rgba(0,0,0,0.5)",
          opacity: cardOpacity,
          transform: `scale(${cardScale}) translate3d(${style.left}px, ${Number(style.top) + floatOffset}px, ${cardZ}px) rotate(${style.transform})`,
          backdropFilter: "blur(20px)"
        }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
            <span style={{ fontSize: 16, fontWeight: 700, color: "#f5f6fa", fontFamily: "JetBrains Mono" }}>{title}</span>
            <span style={{ fontSize: 12, fontWeight: 700, background: "rgba(231,76,60,0.15)", color: "#e74c3c", padding: "4px 8px", borderRadius: 4 }}>{format}</span>
          </div>
          <div style={{ height: 60, display: "flex", flexDirection: "column", gap: 8, justifyContent: "center" }}>
            <div style={{ height: 8, background: "rgba(255,255,255,0.05)", borderRadius: 4 }} />
            <div style={{ height: 8, background: "rgba(255,255,255,0.05)", borderRadius: 4, width: "70%" }} />
          </div>
          <div style={{ marginTop: 12, background: "rgba(231, 76, 60, 0.1)", border: "1px solid rgba(231, 76, 60, 0.2)", color: "#e74c3c", fontSize: 12, fontWeight: 700, padding: "8px 12px", borderRadius: 8, textAlign: "center", fontFamily: "JetBrains Mono" }}>
            {error}
          </div>
        </div>
      );
    };

    return (
      <div className="scene" style={{ opacity, filter: `blur(${blur}px)`, transform: `scale(${scale})` }}>
        <div className="scene-content">
          <div className="deco-glow" style={{ width: 600, height: 600, background: "rgba(231,76,60,0.06)", top: "25%", left: "30%" }}></div>
          <div className="deco-ghost" style={{ top: "5%", right: "-10%", transform: "rotate(8deg)" }}>ERROR</div>
          <span className="scene-label">Document Chaos</span>

          <div style={{
            position: "absolute",
            top: 200,
            left: 0,
            right: 0,
            bottom: 0
          }}>
            {renderCard("Schedule_P1.pdf", "PDF", "#VALUE! Error", { left: 150, top: 40, transform: "-8deg" }, 9)}
            {renderCard("BOQ_Main.xlsx", "XLSX", "Missing Units", { left: 550, top: 120, transform: "5deg" }, 18)}
            {renderCard("Specs_Rev3.docx", "DOCX", "Format Error", { left: 950, top: 20, transform: "-3deg" }, 27)}
            {renderCard("scan_page_04.png", "IMG", "Unreadable ⚠", { left: 1350, top: 160, transform: "10deg" }, 36)}
            {renderCard("materials.csv", "CSV", "Broken Table", { left: 350, top: 380, transform: "-12deg" }, 45)}
          </div>
        </div>
      </div>
    );
  };
  ```

- [ ] **Step 3: Implement Scene 3 (Reveal, frames 600 to 900)**
  Code:
  ```tsx
  import { useCurrentFrame, interpolate, spring, useVideoConfig, Img, staticFile } from "remotion";

  export const Scene3 = () => {
    const frame = useCurrentFrame();
    const { fps } = useVideoConfig();

    // Scene transition
    const opacity = interpolate(frame, [0, 15, 285, 300], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    const blur = interpolate(frame, [0, 15, 285, 300], [12, 0, 0, 12], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    const scale = interpolate(frame, [0, 15, 285, 300], [0.97, 1, 1, 1.03], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

    // Logo reveal with rotation spin
    const logoSpring = spring({ frame: frame - 15, fps, config: { damping: 12 } });
    const logoScale = interpolate(logoSpring, [0, 1], [0, 1]);
    const logoRotation = interpolate(logoSpring, [0, 1], [-180, 0]);

    // Beam sweep
    const beamX = interpolate(frame, [15, 51], [-600, 600], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    const beamOpacity = interpolate(frame, [15, 45, 51], [0, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

    return (
      <div className="scene" style={{ opacity, filter: `blur(${blur}px)`, transform: `scale(${scale})` }}>
        <div className="scene-content" style={{ display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center" }}>
          <div className="deco-glow" style={{ width: 700, height: 700, background: "rgba(211,84,0,0.12)", top: "20%", left: "32%" }}></div>
          <span className="scene-label">The Solution</span>

          <div style={{
            position: "absolute",
            width: "100%",
            height: "100%",
            background: `radial-gradient(ellipse at center, rgba(211,84,0,0.15) 0%, transparent 70%)`,
            opacity: beamOpacity,
            pointerEvents: "none"
          }} />

          {/* Logo container */}
          <div style={{
            transform: `scale(${logoScale}) rotate(${logoRotation}deg)`,
            marginBottom: 30
          }}>
            <Img src={staticFile("assets/icon.png")} style={{ width: 220, height: 220 }} />
          </div>

          <h2 style={{
            fontFamily: "Cairo",
            fontSize: 96,
            fontWeight: 900,
            color: "#f5f6fa",
            margin: 0,
            letterSpacing: 2
          }}>Tawreed</h2>

          <p style={{
            fontFamily: "Plus Jakarta Sans",
            fontSize: 36,
            fontWeight: 800,
            color: "#a0a5c1",
            marginTop: 10,
            letterSpacing: 1
          }}>AI-Powered Construction Procurement</p>
        </div>
      </div>
    );
  };
  ```

- [ ] **Step 4: Connect scenes in coordinator `src/TawreedLaunch.tsx`**
  Modify `TawreedLaunch.tsx` to display scenes inside Sequences.
  Code:
  ```tsx
  import { AbsoluteFill, Audio, staticFile, Sequence } from "remotion";
  import { Captions } from "./components/Captions";
  import { Scene1 } from "./scenes/Scene1";
  import { Scene2 } from "./scenes/Scene2";
  import { Scene3 } from "./scenes/Scene3";

  export const TawreedLaunch = () => {
    return (
      <AbsoluteFill style={{ backgroundColor: "#0f0f15", overflow: "hidden" }}>
        {/* Audio Mixing */}
        <Audio src={staticFile("assets/narration.wav")} volume={1.0} />
        <Audio src={staticFile("assets/music.mp3")} volume={0.15} />

        {/* Scene Sequences (overlapping by 15 frames for blur transitions) */}
        <Sequence from={0} durationInFrames={255}>
          <Scene1 />
        </Sequence>
        <Sequence from={240} durationInFrames={375}>
          <Scene2 />
        </Sequence>
        <Sequence from={600} durationInFrames={315}>
          <Scene3 />
        </Sequence>

        {/* Captions Overlay */}
        <Captions />
      </AbsoluteFill>
    );
  };
  ```

- [ ] **Step 5: Commit Scenes 1-3**
  Run:
  ```bash
  git add video-launch/src/scenes/Scene1.tsx video-launch/src/scenes/Scene2.tsx video-launch/src/scenes/Scene3.tsx video-launch/src/TawreedLaunch.tsx
  git commit -m "feat: implement Scene 1 (Hook), Scene 2 (Chaos), and Scene 3 (Reveal)"
  ```

---

### Task 5: Implementing Scenes 4-6

**Files:**
- Create: `video-launch/src/scenes/Scene4.tsx`
- Create: `video-launch/src/scenes/Scene5.tsx`
- Create: `video-launch/src/scenes/Scene6.tsx`
- Modify: `video-launch/src/TawreedLaunch.tsx`

- [ ] **Step 1: Implement Scene 4 (Ingestion, frames 900 to 1260)**
  Code:
  ```tsx
  import { useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";

  export const Scene4 = () => {
    const frame = useCurrentFrame();
    const { fps } = useVideoConfig();

    const opacity = interpolate(frame, [0, 15, 345, 360], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    const blur = interpolate(frame, [0, 15, 345, 360], [12, 0, 0, 12], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    const scale = interpolate(frame, [0, 15, 345, 360], [0.97, 1, 1, 1.03], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

    const renderFormat = (text: string, ext: string, color: string, stagger: number) => {
      const fmtSpring = spring({ frame: frame - stagger, fps, config: { damping: 14 } });
      const x = interpolate(fmtSpring, [0, 1], [-100, 0]);
      const alpha = interpolate(fmtSpring, [0, 1], [0, 1]);

      return (
        <div style={{
          display: "flex",
          alignItems: "center",
          gap: 16,
          background: "rgba(26,26,38,0.4)",
          padding: "16px 24px",
          borderRadius: 12,
          border: "1px solid rgba(255,255,255,0.05)",
          transform: `translateX(${x}px)`,
          opacity: alpha
        }}>
          <div style={{
            fontSize: 16,
            fontWeight: 800,
            color: "#fff",
            background: color,
            padding: "8px 12px",
            borderRadius: 6,
            fontFamily: "JetBrains Mono"
          }}>{ext}</div>
          <span style={{ fontSize: 20, fontWeight: 600, color: "#f5f6fa" }}>{text}</span>
        </div>
      );
    };

    return (
      <div className="scene" style={{ opacity, filter: `blur(${blur}px)`, transform: `scale(${scale})` }}>
        <div className="scene-content" style={{ display: "flex", padding: "0 100px", justifyContent: "space-between", alignItems: "center", height: "100%" }}>
          <div className="deco-glow" style={{ width: 400, height: 400, background: "rgba(211,84,0,0.06)", top: "30%", left: "10%" }}></div>
          <span className="scene-label">Multi-Format Engine</span>

          {/* Left panel: Format items */}
          <div style={{ display: "flex", flexDirection: "column", gap: 16, width: 480 }}>
            {renderFormat("PDF Documents", "PDF", "#e74c3c", 9)}
            {renderFormat("Excel Sheets", "XLS", "#2ecc71", 15)}
            {renderFormat("Word Files", "DOC", "#2980b9", 21)}
            {renderFormat("CSV Data Sheets", "CSV", "#f1c40f", 27)}
            {renderFormat("Images & Photos", "IMG", "#8e44ad", 33)}
          </div>

          {/* Dropzone mockup */}
          <div style={{
            width: 520,
            height: 380,
            borderRadius: 24,
            border: "2px dashed rgba(211, 84, 0, 0.4)",
            background: "rgba(26,26,38,0.5)",
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            alignItems: "center",
            padding: 40,
            textAlign: "center"
          }}>
            <div style={{ fontSize: 72, marginBottom: 20 }}>📥</div>
            <h3 style={{ fontSize: 28, fontWeight: 800, margin: 0 }}>Drop Any File</h3>
            <p style={{ color: "#a0a5c1", fontSize: 18, marginTop: 10 }}>Tawreed handles the rest automatically</p>
          </div>
        </div>
      </div>
    );
  };
  ```

- [ ] **Step 2: Implement Scene 5 (Diagnostics, frames 1260 to 1650)**
  Code:
  ```tsx
  import { useCurrentFrame, interpolate } from "remotion";

  export const Scene5 = () => {
    const frame = useCurrentFrame();

    const opacity = interpolate(frame, [0, 15, 375, 390], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    const blur = interpolate(frame, [0, 15, 375, 390], [12, 0, 0, 12], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    const scale = interpolate(frame, [0, 15, 375, 390], [0.97, 1, 1, 1.03], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

    // Console text logs
    const logs = [
      { text: "▸ Loading document: BOQ_Main.xlsx (2.4 MB)", color: "#a0a5c1" },
      { text: "✓ Parser detected: Excel / OpenPyXL", color: "#2ecc71" },
      { text: "▸ Sending to AI: Gemini 2.5 Flash", color: "#a0a5c1" },
      { text: "⚠ JSON malformed — initiating auto-repair", color: "#f1c40f" },
      { text: "✓ JSON repaired successfully via json_repair", color: "#2ecc71" },
      { text: "✓ Extracted 47 materials across 6 packages", color: "#2ecc71" },
      { text: "▸ Running QA iteration 1/3...", color: "#a0a5c1" },
      { text: "✓ QA passed — confidence: 94.2%", color: "#2ecc71" },
      { text: "✓ Export ready: Tawreed_Takeoff_Final.xlsx", color: "#2ecc71" }
    ];

    // Progress bar fill (interpolates from 0% to 100%)
    const progress = interpolate(frame, [30, 270], [0, 100], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

    return (
      <div className="scene" style={{ opacity, filter: `blur(${blur}px)`, transform: `scale(${scale})` }}>
        <div className="scene-content" style={{ display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center" }}>
          <span className="scene-label">AI Diagnostics Engine</span>

          {/* AI Badges */}
          <div style={{ display: "flex", gap: 16, marginBottom: 30 }}>
            {["Gemini", "GPT-4", "Claude"].map((prov, i) => (
              <span key={prov} style={{
                background: i === 0 ? "#d35400" : "rgba(26,26,38,0.8)",
                border: i === 0 ? "1px solid #d35400" : "1px solid rgba(255,255,255,0.05)",
                padding: "8px 20px",
                borderRadius: 20,
                fontSize: 16,
                fontWeight: 700,
                fontFamily: "JetBrains Mono"
              }}>{prov}</span>
            ))}
          </div>

          {/* Console layout */}
          <div style={{
            width: 900,
            background: "#12121a",
            borderRadius: 16,
            border: "1px solid rgba(255,255,255,0.08)",
            boxShadow: "0 20px 50px rgba(0,0,0,0.5)",
            overflow: "hidden"
          }}>
            {/* Header chrome */}
            <div style={{ background: "#1a1a26", padding: "12px 20px", display: "flex", alignItems: "center", gap: 8 }}>
              <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#e74c3c" }} />
              <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#f1c40f" }} />
              <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#2ecc71" }} />
              <span style={{ marginLeft: 20, fontSize: 14, fontFamily: "JetBrains Mono", color: "#676b85" }}>tawreed — ai_diagnostics_console</span>
            </div>

            {/* Terminal contents */}
            <div style={{ padding: 24, display: "flex", flexDirection: "column", gap: 12, fontFamily: "JetBrains Mono", fontSize: 16, textAlign: "left", minHeight: 320 }}>
              {logs.map((log, i) => {
                const show = frame > (30 + i * 27);
                return show ? (
                  <div key={i} style={{ color: log.color }}>{log.text}</div>
                ) : null;
              })}
            </div>
          </div>

          {/* Progress bar container */}
          <div style={{ width: 900, height: 6, background: "rgba(255,255,255,0.05)", borderRadius: 3, marginTop: 30, overflow: "hidden" }}>
            <div style={{ width: `${progress}%`, height: "100%", background: "#d35400", borderRadius: 3 }} />
          </div>
        </div>
      </div>
    );
  };
  ```

- [ ] **Step 3: Implement Scene 6 (Excel Output, frames 1650 to 2040)**
  Code:
  ```tsx
  import { useCurrentFrame, interpolate } from "remotion";

  export const Scene6 = () => {
    const frame = useCurrentFrame();

    const opacity = interpolate(frame, [0, 15, 375, 390], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    const blur = interpolate(frame, [0, 15, 375, 390], [12, 0, 0, 12], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    const scale = interpolate(frame, [0, 15, 375, 390], [0.97, 1, 1, 1.03], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

    const rows = [
      { mat: "Reinforcement Steel — حديد تسليح", unit: "Ton", qty: "245.00", spec: "Grade 60, Ø12-Ø32mm" },
      { mat: "Portland Cement — أسمنت بورتلاندي", unit: "Bag", qty: "1,200", spec: "Type I, 42.5N" },
      { mat: "Concrete C35 — خرسانة جاهزة", unit: "m³", qty: "580.50", spec: "Ready-mix, 35 MPa" },
      { mat: "Waterproofing — عزل مائي", unit: "m²", qty: "3,400", spec: "Bituminous membrane, 4mm" },
      { mat: "Aluminum Cladding — تكسيات ألمنيوم", unit: "m²", qty: "1,850", spec: "Composite panel, 4mm" }
    ];

    return (
      <div className="scene" style={{ opacity, filter: `blur(${blur}px)`, transform: `scale(${scale})` }}>
        <div className="scene-content" style={{ display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center" }}>
          <div className="deco-glow" style={{ width: 500, height: 500, background: "rgba(211,84,0,0.06)", top: "40%", left: "40%" }}></div>
          <span className="scene-label">Tawreed Takeoff Export</span>

          <div style={{
            width: 1000,
            background: "#1e1e2d",
            borderRadius: 12,
            border: "1px solid rgba(255,255,255,0.05)",
            boxShadow: "0 20px 40px rgba(0,0,0,0.5)",
            overflow: "hidden"
          }}>
            {/* Sheet Chrome */}
            <div style={{ background: "#252538", padding: "16px 24px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span style={{ fontFamily: "JetBrains Mono", fontSize: 16, color: "#f5f6fa", fontWeight: 700 }}>Tawreed_Takeoff_Final.xlsx</span>
              <span style={{ fontSize: 12, fontWeight: 700, background: "#d35400", padding: "4px 8px", borderRadius: 4 }}>Bilingual Takeoff</span>
            </div>

            {/* Excel Sheet Mockup Grid */}
            <div style={{ display: "flex", flexDirection: "column" }}>
              {/* Header row */}
              <div style={{
                display: "grid",
                gridTemplateColumns: "2.5fr 1fr 1fr 2fr",
                padding: "12px 24px",
                background: "rgba(255,255,255,0.02)",
                borderBottom: "1px solid rgba(255,255,255,0.05)",
                fontFamily: "Plus Jakarta Sans",
                fontSize: 14,
                fontWeight: 700,
                color: "#676b85"
              }}>
                <div>Material Name</div>
                <div>Unit</div>
                <div>Quantity</div>
                <div>Specification</div>
              </div>

              {/* Rows */}
              {rows.map((row, i) => {
                const show = frame > (30 + i * 9);
                return show ? (
                  <div key={i} style={{
                    display: "grid",
                    gridTemplateColumns: "2.5fr 1fr 1fr 2fr",
                    padding: "16px 24px",
                    borderBottom: "1px solid rgba(255,255,255,0.03)",
                    fontSize: 16,
                    color: "#f5f6fa"
                  }}>
                    <div style={{ fontWeight: 600 }}>{row.mat}</div>
                    <div style={{ fontFamily: "JetBrains Mono", color: "#a0a5c1" }}>{row.unit}</div>
                    <div style={{ fontFamily: "JetBrains Mono", color: "#d35400", fontWeight: 700 }}>{row.qty}</div>
                    <div style={{ color: "#a0a5c1", fontSize: 14 }}>{row.spec}</div>
                  </div>
                ) : null;
              })}
            </div>
          </div>
        </div>
      </div>
    );
  };
  ```

- [ ] **Step 4: Connect sequences in coordinator `src/TawreedLaunch.tsx`**
  Modify `TawreedLaunch.tsx` to add scenes 4, 5, and 6.
  Code:
  ```tsx
  import { AbsoluteFill, Audio, staticFile, Sequence } from "remotion";
  import { Captions } from "./components/Captions";
  import { Scene1 } from "./scenes/Scene1";
  import { Scene2 } from "./scenes/Scene2";
  import { Scene3 } from "./scenes/Scene3";
  import { Scene4 } from "./scenes/Scene4";
  import { Scene5 } from "./scenes/Scene5";
  import { Scene6 } from "./scenes/Scene6";

  export const TawreedLaunch = () => {
    return (
      <AbsoluteFill style={{ backgroundColor: "#0f0f15", overflow: "hidden" }}>
        {/* Audio Mixing */}
        <Audio src={staticFile("assets/narration.wav")} volume={1.0} />
        <Audio src={staticFile("assets/music.mp3")} volume={0.15} />

        {/* Scene Sequences */}
        <Sequence from={0} durationInFrames={255}>
          <Scene1 />
        </Sequence>
        <Sequence from={240} durationInFrames={375}>
          <Scene2 />
        </Sequence>
        <Sequence from={600} durationInFrames={315}>
          <Scene3 />
        </Sequence>
        <Sequence from={900} durationInFrames={375}>
          <Scene4 />
        </Sequence>
        <Sequence from={1260} durationInFrames={405}>
          <Scene5 />
        </Sequence>
        <Sequence from={1650} durationInFrames={405}>
          <Scene6 />
        </Sequence>

        {/* Captions Overlay */}
        <Captions />
      </AbsoluteFill>
    );
  };
  ```

- [ ] **Step 5: Commit Scenes 4-6**
  Run:
  ```bash
  git add video-launch/src/scenes/Scene4.tsx video-launch/src/scenes/Scene5.tsx video-launch/src/scenes/Scene6.tsx video-launch/src/TawreedLaunch.tsx
  git commit -m "feat: implement Scene 4 (Ingestion), Scene 5 (Diagnostics), and Scene 6 (Excel Output)"
  ```

---

### Task 6: Implementing Scenes 7-8

**Files:**
- Create: `video-launch/src/scenes/Scene7.tsx`
- Create: `video-launch/src/scenes/Scene8.tsx`
- Modify: `video-launch/src/TawreedLaunch.tsx`

- [ ] **Step 1: Implement Scene 7 (Impact Stats, frames 2040 to 2340)**
  Code:
  ```tsx
  import { useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";

  export const Scene7 = () => {
    const frame = useCurrentFrame();
    const { fps } = useVideoConfig();

    const opacity = interpolate(frame, [0, 15, 285, 300], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    const blur = interpolate(frame, [0, 15, 285, 300], [12, 0, 0, 12], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    const scale = interpolate(frame, [0, 15, 285, 300], [0.97, 1, 1, 1.03], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

    // Animating number counters
    const counter1 = interpolate(frame, [30, 80], [0, 10], { extrapolateRight: "clamp" });
    const counter3 = interpolate(frame, [120, 170], [0, 6], { extrapolateRight: "clamp" });

    const renderStatCard = (num: string, label: string, stagger: number) => {
      const cardSpring = spring({ frame: frame - stagger, fps, config: { damping: 12 } });
      const cardScale = interpolate(cardSpring, [0, 1], [0.6, 1]);
      const cardOpacity = interpolate(cardSpring, [0, 1], [0, 1]);

      return (
        <div style={{
          width: 320,
          background: "rgba(26,26,38,0.75)",
          borderRadius: 20,
          border: "1px solid rgba(255,255,255,0.05)",
          padding: "40px 20px",
          textAlign: "center",
          boxShadow: "0 20px 45px rgba(0,0,0,0.4)",
          transform: `scale(${cardScale})`,
          opacity: cardOpacity,
          backdropFilter: "blur(20px)"
        }}>
          <h2 style={{
            fontFamily: "Cairo",
            fontSize: 90,
            fontWeight: 900,
            color: "#d35400",
            margin: 0,
            fontVariantNumeric: "tabular-nums"
          }}>{num}</h2>
          <p style={{
            fontFamily: "Plus Jakarta Sans",
            fontSize: 22,
            fontWeight: 800,
            color: "#a0a5c1",
            marginTop: 10,
            margin: 0
          }}>{label}</p>
        </div>
      );
    };

    return (
      <div className="scene" style={{ opacity, filter: `blur(${blur}px)`, transform: `scale(${scale})` }}>
        <div className="scene-content" style={{ display: "flex", justifyContent: "center", alignItems: "center", gap: 50, height: "100%" }}>
          <span className="scene-label">Impact Metrics</span>

          {renderStatCard(`${Math.round(counter1)}x`, "Faster Processing", 15)}
          {renderStatCard("0", "Human Errors", 60)}
          {renderStatCard(`${Math.round(counter3)}+`, "Supported Formats", 105)}
        </div>
      </div>
    );
  };
  ```

- [ ] **Step 2: Implement Scene 8 (CTA, frames 2340 to 2700)**
  Code:
  ```tsx
  import { useCurrentFrame, interpolate, spring, useVideoConfig, Img, staticFile } from "remotion";

  export const Scene8 = () => {
    const frame = useCurrentFrame();
    const { fps } = useVideoConfig();

    const opacity = interpolate(frame, [0, 15, 345, 360], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    const blur = interpolate(frame, [0, 15, 345, 360], [12, 0, 0, 12], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    const scale = interpolate(frame, [0, 15, 345, 360], [0.97, 1, 1, 1.03], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

    // Logo bounce
    const logoSpring = spring({ frame: frame - 15, fps, config: { damping: 12 } });
    const logoScale = interpolate(logoSpring, [0, 1], [0, 1]);

    // Button hover pulse shadow simulation
    const pulseGlow = Math.sin(frame / 10) * 15 + 35;

    return (
      <div className="scene" style={{ opacity, filter: `blur(${blur}px)`, transform: `scale(${scale})` }}>
        <div className="scene-content" style={{ display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center" }}>
          <div className="deco-glow" style={{ width: 600, height: 600, background: "rgba(211,84,0,0.10)", top: "20%", left: "35%" }}></div>
          <div className="deco-line" style={{ top: 100, left: 300, width: 1320 }}></div>
          <div className="deco-line" style={{ bottom: 100, left: 300, width: 1320 }}></div>

          <div style={{ transform: `scale(${logoScale})`, marginBottom: 30 }}>
            <Img src={staticFile("assets/icon.png")} style={{ width: 180, height: 180 }} />
          </div>

          <h2 style={{ fontFamily: "Cairo", fontSize: 80, fontWeight: 900, color: "#f5f6fa", margin: 0 }}>Tawreed</h2>

          {/* Download button */}
          <div style={{
            background: "#d35400",
            padding: "20px 48px",
            borderRadius: 40,
            fontSize: 28,
            fontWeight: 800,
            color: "#fff",
            fontFamily: "Plus Jakarta Sans",
            marginTop: 40,
            boxShadow: `0 10px ${pulseGlow}px rgba(211, 84, 0, 0.4)`
          }}>
            Download Now — حمّل الآن
          </div>

          <p style={{
            fontFamily: "JetBrains Mono",
            fontSize: 24,
            fontWeight: 700,
            color: "#a0a5c1",
            marginTop: 30
          }}>kareemsafwat.com/ai#projects</p>
        </div>
      </div>
    );
  };
  ```

- [ ] **Step 3: Connect all sequences in coordinator `src/TawreedLaunch.tsx`**
  Add Scenes 7 and 8 to complete the coordinator timeline.
  Code:
  ```tsx
  import { AbsoluteFill, Audio, staticFile, Sequence } from "remotion";
  import { Captions } from "./components/Captions";
  import { Scene1 } from "./scenes/Scene1";
  import { Scene2 } from "./scenes/Scene2";
  import { Scene3 } from "./scenes/Scene3";
  import { Scene4 } from "./scenes/Scene4";
  import { Scene5 } from "./scenes/Scene5";
  import { Scene6 } from "./scenes/Scene6";
  import { Scene7 } from "./scenes/Scene7";
  import { Scene8 } from "./scenes/Scene8";

  export const TawreedLaunch = () => {
    return (
      <AbsoluteFill style={{ backgroundColor: "#0f0f15", overflow: "hidden" }}>
        {/* Audio Mixing */}
        <Audio src={staticFile("assets/narration.wav")} volume={1.0} />
        <Audio src={staticFile("assets/music.mp3")} volume={0.15} />

        {/* Scene Sequences */}
        <Sequence from={0} durationInFrames={255}>
          <Scene1 />
        </Sequence>
        <Sequence from={240} durationInFrames={375}>
          <Scene2 />
        </Sequence>
        <Sequence from={600} durationInFrames={315}>
          <Scene3 />
        </Sequence>
        <Sequence from={900} durationInFrames={375}>
          <Scene4 />
        </Sequence>
        <Sequence from={1260} durationInFrames={405}>
          <Scene5 />
        </Sequence>
        <Sequence from={1650} durationInFrames={405}>
          <Scene6 />
        </Sequence>
        <Sequence from={2040} durationInFrames={315}>
          <Scene7 />
        </Sequence>
        <Sequence from={2340} durationInFrames={360}>
          <Scene8 />
        </Sequence>

        {/* Captions Overlay */}
        <Captions />
      </AbsoluteFill>
    );
  };
  ```

- [ ] **Step 4: Commit Scenes 7-8**
  Run:
  ```bash
  git add video-launch/src/scenes/Scene7.tsx video-launch/src/scenes/Scene8.tsx video-launch/src/TawreedLaunch.tsx
  git commit -m "feat: implement Scene 7 (Impact Stats) and Scene 8 (CTA)"
  ```

---

### Task 7: Rendering and Verification

**Files:**
- Modify: `video-launch/package.json`

- [ ] **Step 1: Ensure render scripts are configured**
  Add clean NPM build/render scripts in `video-launch/package.json`.
  Modify: `video-launch/package.json` to have:
  ```json
  "scripts": {
    "start": "remotion studio",
    "build": "remotion render TawreedLaunch out.mp4",
    "still": "remotion still TawreedLaunch"
  }
  ```

- [ ] **Step 2: Test render a single frame**
  Run still render of Scene 5 console progression at frame 1500 to check look and feel.
  Run:
  ```powershell
  npx remotion still TawreedLaunch --frame=1500 --scale=0.5
  ```
  Expected: Command outputs `still.png` successfully without errors.

- [ ] **Step 3: Run production video render**
  Run a full render of the composition to build the final launch video output.
  Run:
  ```powershell
  npx remotion render TawreedLaunch out.mp4
  ```
  Expected: Output video `out.mp4` generated successfully.

- [ ] **Step 4: Commit the final scripts**
  Run:
  ```bash
  git add video-launch/package.json
  git commit -m "chore: configure npm build scripts and finalize project setup"
  ```
