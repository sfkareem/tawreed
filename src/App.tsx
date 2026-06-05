import { useState } from "react";
import { invoke } from "@tauri-apps/api/core";

export default function App() {
  const [baseUrl, setBaseUrl] = useState("https://api.openai.com/v1");
  const [model, setModel] = useState("gpt-4o-mini");
  const [apiKey, setApiKey] = useState("");
  const [status, setStatus] = useState("");

  async function handleProcess(filePath: string) {
    setStatus("Processing...");
    try {
      const res = await invoke("process_boq", { filePath, baseUrl, model, apiKey });
      setStatus(`Success: ${res}`);
    } catch (e) {
      setStatus(`Error: ${e}`);
    }
  }

  return (
    <div className="p-8 max-w-lg mx-auto font-sans">
      <h1 className="text-2xl font-bold mb-4">Slab BOQ Slicer</h1>
      <div className="space-y-4">
        <input className="border p-2 w-full" placeholder="Base URL" value={baseUrl} onChange={e => setBaseUrl(e.target.value)} />
        <input className="border p-2 w-full" placeholder="Model ID" value={model} onChange={e => setModel(e.target.value)} />
        <input className="border p-2 w-full" type="password" placeholder="API Key" value={apiKey} onChange={e => setApiKey(e.target.value)} />
        <button className="bg-blue-500 text-white p-2 rounded w-full" onClick={() => handleProcess("dummy/path.xlsx")}>
          Process BOQ
        </button>
        <p className="text-sm mt-4 text-gray-600">{status}</p>
      </div>
    </div>
  );
}
