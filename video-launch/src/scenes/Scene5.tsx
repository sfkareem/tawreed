import { useCurrentFrame, interpolate } from "remotion";

export const Scene5 = () => {
  const frame = useCurrentFrame();

  const opacity = interpolate(frame, [0, 15, 390, 405], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const blur = interpolate(frame, [0, 15, 390, 405], [12, 0, 0, 12], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const scale = interpolate(frame, [0, 15, 390, 405], [0.97, 1, 1, 1.03], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

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
              fontFamily: "JetBrains Mono",
              color: i === 0 ? "#fff" : "#a0a5c1"
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
