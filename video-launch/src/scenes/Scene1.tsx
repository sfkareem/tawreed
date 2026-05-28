import { useCurrentFrame, interpolate, Easing } from "remotion";

export const Scene1 = () => {
  const frame = useCurrentFrame();

  // Blur Transition
  const opacity = interpolate(frame, [0, 15, 240, 255], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const blur = interpolate(frame, [0, 15, 240, 255], [12, 0, 0, 12], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const scale = interpolate(frame, [0, 15, 240, 255], [0.97, 1, 1, 1.03], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  // Counter animation (0 to 8+)
  const counterVal = interpolate(frame, [60, 105], [0, 8], {
    extrapolateLeft: "clamp",
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
