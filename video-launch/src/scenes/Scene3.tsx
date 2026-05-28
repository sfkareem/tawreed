import { useCurrentFrame, interpolate, spring, useVideoConfig, Img, staticFile } from "remotion";

export const Scene3 = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Scene transition
  const opacity = interpolate(frame, [0, 15, 300, 315], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const blur = interpolate(frame, [0, 15, 300, 315], [12, 0, 0, 12], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const scale = interpolate(frame, [0, 15, 300, 315], [0.97, 1, 1, 1.03], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  // Logo reveal with rotation spin
  const logoSpring = spring({ frame: frame - 15, fps, config: { damping: 12 } });
  const logoScale = interpolate(logoSpring, [0, 1], [0, 1]);
  const logoRotation = interpolate(logoSpring, [0, 1], [-180, 0]);

  // Beam sweep
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
