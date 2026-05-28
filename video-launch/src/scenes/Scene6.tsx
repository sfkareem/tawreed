import { useCurrentFrame, interpolate } from "remotion";

export const Scene6 = () => {
  const frame = useCurrentFrame();

  const opacity = interpolate(frame, [0, 15, 390, 405], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const blur = interpolate(frame, [0, 15, 390, 405], [12, 0, 0, 12], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const scale = interpolate(frame, [0, 15, 390, 405], [0.97, 1, 1, 1.03], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

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
            <span style={{ fontSize: 12, fontWeight: 700, background: "#d35400", padding: "4px 8px", borderRadius: 4, fontFamily: "Plus Jakarta Sans", color: "#fff" }}>Bilingual Takeoff</span>
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
                  color: "#f5f6fa",
                  fontFamily: "Plus Jakarta Sans"
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
