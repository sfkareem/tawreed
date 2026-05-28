# Design Spec: Tawreed Launch Video in Remotion

## Overview
This document specifies the migration and rebuilding of the Tawreed launch video from a HyperFrames HTML composition to a native React-based Remotion video. The design preserves the premium, dark-themed, rust-orange construction-tech aesthetic of Tawreed.

## Metadata & Composition Config
- **Composition ID**: `TawreedLaunch`
- **Output Video Resolution**: 1920x1080 (Widescreen 16:9)
- **FPS (Frames Per Second)**: 30
- **Duration**: 90 seconds (2,700 frames)
- **Primary Accent**: `#d35400` (Rust Orange)
- **Background Color**: `#0f0f15` (Deep Slate/Near-Black)
- **Surface Color**: `#1a1a26` (Glass Card background at 75% opacity)

## Architecture & Components

```
video-launch/
├── public/                 # Remotion static assets folder
│   ├── icon.png            # Tawreed app icon (reused)
│   ├── music.mp3           # Background music track (reused)
│   └── narration.wav       # Audio voiceover track (reused)
├── src/
│   ├── scenes/             # Individual scene components
│   │   ├── Scene1.tsx      # The Hook (0s – 8s / frames 0 - 240)
│   │   ├── Scene2.tsx      # The Chaos (8s – 20s / frames 240 - 600)
│   │   ├── Scene3.tsx      # The Reveal (20s – 30s / frames 600 - 900)
│   │   ├── Scene4.tsx      # Ingestion (30s – 42s / frames 900 - 1260)
│   │   ├── Scene5.tsx      # Diagnostics (42s – 55s / frames 1260 - 1650)
│   │   ├── Scene6.tsx      # Excel Output (55s – 68s / frames 1650 - 2040)
│   │   ├── Scene7.tsx      # Impact Stats (68s – 78s / frames 2040 - 2340)
│   │   └── Scene8.tsx      # CTA (78s – 90s / frames 2340 - 2700)
│   ├── components/
│   │   └── Captions.tsx    # Dynamic subtitle rendering layer
│   ├── Root.tsx            # Font loaders and Composition registrations
│   ├── TawreedLaunch.tsx   # Parent coordinator, Audio mixing, Sequence timing
│   └── index.css           # Global typography & design system tokens
├── package.json
└── tailwind.config.js      # (Not used, using Vanilla CSS + React inline styles)
```

## Typography & Fonts
We load three Google Fonts programmatically inside `src/Root.tsx`:
1. **Cairo** (900): Headline typography
2. **Plus Jakarta Sans** (500, 800): Subheadings, labels, and body paragraphs
3. **JetBrains Mono** (600, 700): Code outputs, statistics numbers, and console logs

## Transitions & Animations
We simulate a **Blur Crossfade** by overlapping adjacent scenes by 15 frames (0.5s) on the timeline, and interpolating CSS filters and opacities during the overlapping segments:
- **Entry**: Opacity $0 \to 1$, Blur $12\text{px} \to 0\text{px}$, Scale $0.97 \to 1.0$ (duration: 15 frames)
- **Exit**: Opacity $1 \to 0$, Blur $0\text{px} \to 12\text{px}$, Scale $1.0 \to 1.03$ (duration: 15 frames)

### Animations per Scene:
1. **Scene 1 (Hook)**:
   - Counter counts up from `0` to `8+` over 45 frames (from frame 60 to 105) using `interpolate()`.
2. **Scene 2 (Chaos)**:
   - 5 file cards crash onto the canvas staggered by 9 frames.
   - Snappy elastic feel implemented using Remotion's `spring()` on scale/position.
   - Cards float using low-frequency cosine waves (`Math.cos(frame / 10)`).
3. **Scene 5 (Console)**:
   - Diagnostics typing lines simulated using frame conditions.
   - Progress bar width interpolates from `0%` to `100%`.
4. **Scene 7 (Stats)**:
   - Counts up metric values (10x, 0, 6+) using linear and eased interpolations.

## Audio Mixing
- Narration track: `assets/narration.wav` (starts at 0s, duration 80s, volume 1.0).
- Background music: `assets/music.mp3` (starts at 0s, duration 90s, volume 0.15).

## Verification Plan
1. **Remotion Studio**: Launch with `npx remotion studio` and verify layout, fonts, and animation flows across all scenes.
2. **Sanity Still Render**: Generate a still image of Scene 5 (console diagnostics progress) at frame 1500:
   `npx remotion still TawreedLaunch --frame=1500 --scale=0.5`
3. **Production Video Render**: Run full compile to generate the MP4 launch video:
   `npx remotion render TawreedLaunch out.mp4`
