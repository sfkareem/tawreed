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
