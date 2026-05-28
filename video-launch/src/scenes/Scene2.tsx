import { useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";

export const Scene2 = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const opacity = interpolate(frame, [0, 15, 360, 375], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const blur = interpolate(frame, [0, 15, 360, 375], [12, 0, 0, 12], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const scale = interpolate(frame, [0, 15, 360, 375], [0.97, 1, 1, 1.03], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

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
