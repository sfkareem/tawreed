import { useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";

export const Scene4 = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const opacity = interpolate(frame, [0, 15, 360, 375], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const blur = interpolate(frame, [0, 15, 360, 375], [12, 0, 0, 12], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const scale = interpolate(frame, [0, 15, 360, 375], [0.97, 1, 1, 1.03], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

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
        <span style={{ fontSize: 20, fontWeight: 600, color: "#f5f6fa", fontFamily: "Plus Jakarta Sans" }}>{text}</span>
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
          <h3 style={{ fontSize: 28, fontWeight: 800, margin: 0, fontFamily: "Cairo", color: "#f5f6fa" }}>Drop Any File</h3>
          <p style={{ color: "#a0a5c1", fontSize: 18, marginTop: 10, fontFamily: "Plus Jakarta Sans" }}>Tawreed handles the rest automatically</p>
        </div>
      </div>
    </div>
  );
};
