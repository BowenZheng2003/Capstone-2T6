import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function UploadPage() {
  const [file, setFile] = useState(null);
  const [err, setErr] = useState("");
  const navigate = useNavigate();

  async function handleAnalyze() {
    if (!file) return;
    setErr("");
    navigate("/analyzing"); // show waiting screen immediately

    const form = new FormData();
    form.append("file", file); // key MUST be "file"

    try {
      const res = await fetch("/process_video", { method: "POST", body: form });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json(); // { message, report }
      navigate("/results", { state: { report: data.report } });
    } catch (e) {
      navigate("/results", { state: { error: String(e) } });
    }
  }

  return (
    <main style={{ maxWidth: 720, margin: "48px auto", padding: 24 }}>
      <h1>Presentation Analyzer</h1>
      <p>Select a video to analyze.</p>
      <input
        type="file"
        accept="video/*"
        onChange={(e) => setFile(e.target.files?.[0] ?? null)}
      />
      <div style={{ marginTop: 16 }}>
        <button onClick={handleAnalyze} disabled={!file}>Analyze</button>
      </div>
      {err && <p style={{ color: "crimson" }}>{err}</p>}
    </main>
  );
}
