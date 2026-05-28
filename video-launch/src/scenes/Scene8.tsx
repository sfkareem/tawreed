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
