import React, { useEffect, useRef, useState } from "react";
import "./AnalyzingPage.css";
import topLeft from "../assets/Group 1.svg";
import bottomLeft from "../assets/Group 3.svg";
import rightImg from "../assets/Group 2.svg";

const STAGES = [
  { label: "Upload",     at: 0 },
  { label: "Audio",      at: 10 },
  { label: "Transcribe", at: 25 },
  { label: "Visuals",    at: 45 },
  { label: "Report",     at: 80 },
  { label: "Done",       at: 100 },
];

export default function AnalyzingPage({ file, context, apiBase, onCancel, onDone }) {
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState("Uploading your video…");
  const [error, setError] = useState("");

  const controllerRef = useRef(null);

  useEffect(() => {
    if (!file) return;

    controllerRef.current = new AbortController();
    setProgress(0);
    setMessage("Uploading your video…");
    setError("");

    (async () => {
      try {
        const formData = new FormData();
        formData.append("file", file);
        formData.append("context", context || "General presentation");

        const res = await fetch(`${apiBase}/process_video_stream`, {
          method: "POST",
          body: formData,
          signal: controllerRef.current.signal,
        });

        if (!res.ok) {
          const txt = await res.text();
          throw new Error(txt || `HTTP ${res.status}`);
        }

        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          buffer = lines.pop(); // hold incomplete line for next chunk

          for (const line of lines) {
            if (!line.startsWith("data: ")) continue;
            try {
              const event = JSON.parse(line.slice(6));
              if (event.step === "done") {
                setProgress(100);
                onDone?.(event);
                return;
              } else if (event.step === "error") {
                setError(event.error || "Processing failed.");
                return;
              } else {
                setProgress(event.progress);
                setMessage(event.message);
              }
            } catch {
              // skip malformed line
            }
          }
        }
      } catch (e) {
        if (e?.name === "AbortError") return;
        setError(e?.message || "Processing failed.");
      }
    })();

    return () => {
      controllerRef.current?.abort?.();
    };
  }, [apiBase, file, onDone]);

  return (
    <div className="analyzing-bg">
      <img src={topLeft} alt="" className="analyzing-top-left" />
      <img src={bottomLeft} alt="" className="analyzing-bottom-left" />
      <img src={rightImg} alt="" className="analyzing-right" />
      <div style={{ position: "relative", zIndex: 1, width: 620, maxWidth: "92%", background: "#fff", borderRadius: 16, padding: 28, boxShadow: "0 12px 40px rgba(0,0,0,0.08)" }}>
        <h1 style={{ margin: 0, fontSize: 22, fontWeight: 700 }}>Analyzing your video</h1>
        <p style={{ marginTop: 8, color: "#6B7280", fontSize: 14 }}>{message}</p>

        <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, color: "#6b7280", marginBottom: 6 }}>
          <span>Progress</span>
          <span>{progress}%</span>
        </div>

        <div style={{ height: 10, width: "100%", background: "#EEEAFB", borderRadius: 999, overflow: "hidden" }}>
          <div style={{ height: "100%", width: `${progress}%`, background: "#9089FC", transition: "width .35s ease" }} />
        </div>

        {/* Stage labels */}
        <div style={{ display: "flex", justifyContent: "space-between", marginTop: 10 }}>
          {STAGES.map((stage) => {
            const active = progress >= stage.at;
            return (
              <div key={stage.label} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 4 }}>
                <div style={{
                  width: 10, height: 10, borderRadius: "50%",
                  background: active ? "#9089FC" : "#EEEAFB",
                  border: `2px solid ${active ? "#9089FC" : "#C4BBF7"}`,
                  transition: "background .35s ease, border-color .35s ease",
                }} />
                <span style={{
                  fontSize: 10,
                  color: active ? "#6F6FDA" : "#B0AACF",
                  fontWeight: active ? 600 : 400,
                  transition: "color .35s ease",
                }}>
                  {stage.label}
                </span>
              </div>
            );
          })}
        </div>

        <div style={{ marginTop: 14, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <button
            onClick={() => {
              controllerRef.current?.abort?.();
              onCancel?.();
            }}
            style={{ border: "1px solid #E7E7F3", background: "#ECE9FF", color: "#4C46CF", borderRadius: 10, padding: "8px 12px", fontWeight: 600 }}
          >
            Cancel & return
          </button>
        </div>

        {error && (
          <div style={{ marginTop: 14, border: "1px solid #FECACA", background: "#FEF2F2", color: "#B91C1C", borderRadius: 10, padding: 12, fontSize: 13 }}>
            <strong>Something went wrong</strong>
            <div style={{ fontSize: 12, marginTop: 6, whiteSpace: "pre-wrap" }}>{error}</div>
          </div>
        )}
      </div>
    </div>
  );
}
