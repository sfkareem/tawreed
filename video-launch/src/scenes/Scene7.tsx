import { useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";

export const Scene7 = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const opacity = interpolate(frame, [0, 15, 300, 315], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const blur = interpolate(frame, [0, 15, 300, 315], [12, 0, 0, 12], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const scale = interpolate(frame, [0, 15, 300, 315], [0.97, 1, 1, 1.03], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  // Animating number counters
  const counter1 = interpolate(frame, [30, 80], [0, 10], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const counter3 = interpolate(frame, [120, 170], [0, 6], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

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
