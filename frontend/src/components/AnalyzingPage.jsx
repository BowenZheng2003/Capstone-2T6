import React, { useEffect, useMemo, useRef, useState } from "react";

const FALLBACK_MESSAGES = [
  "Uploading your video…",
  "Extracting audio…",
  "Transcribing speech…",
  "Extracting features…",
  "Calling the LLM…",
  "Generating final report…",
];

export default function AnalyzingPage({ file, apiBase, onCancel, onDone }) {
  const [progress, setProgress] = useState(0);
  const [phaseIndex, setPhaseIndex] = useState(0);
  const [error, setError] = useState("");

  const controllerRef = useRef(null);

  const message = useMemo(
    () => FALLBACK_MESSAGES[phaseIndex] || "Analyzing…",
    [phaseIndex]
  );

  useEffect(() => {
    if (!file) return;

    controllerRef.current = new AbortController();
    setProgress(0);
    setPhaseIndex(0);
    setError("");

    // simulated UI progress up to 90%
    const phaseTimer = setInterval(
      () => setPhaseIndex((i) => Math.min(i + 1, FALLBACK_MESSAGES.length - 1)),
      3500
    );

    const progTimer = setInterval(() => {
      setProgress((p) => {
        if (p >= 90) return p;
        return p + Math.max(1, Math.round((90 - p) / 15));
      });
    }, 700);

    (async () => {
      try {
        const formData = new FormData();
        formData.append("file", file);

        const res = await fetch(`${apiBase}/process_video`, {
          method: "POST",
          body: formData,
          signal: controllerRef.current.signal,
        });

        if (!res.ok) {
          const txt = await res.text();
          throw new Error(txt || `HTTP ${res.status}`);
        }

        const json = await res.json();
        setProgress(100);
        onDone?.(json);
      } catch (e) {
        if (e?.name === "AbortError") return;
        setError(e?.message || "Processing failed.");
      } finally {
        clearInterval(phaseTimer);
        clearInterval(progTimer);
      }
    })();

    return () => {
      controllerRef.current?.abort?.();
      clearInterval(phaseTimer);
      clearInterval(progTimer);
    };
  }, [apiBase, file, onDone]);

  return (
    <div style={{ minHeight: "100vh", display: "grid", placeItems: "center", padding: 24, fontFamily: "Inter, system-ui, Segoe UI, Arial" }}>
      <div style={{ width: 620, maxWidth: "92%", background: "#fff", borderRadius: 16, padding: 28, boxShadow: "0 12px 40px rgba(0,0,0,0.08)" }}>
        <h1 style={{ margin: 0, fontSize: 22, fontWeight: 700 }}>Analyzing your video</h1>
        <p style={{ marginTop: 8, color: "#6B7280", fontSize: 14 }}>{message}</p>

        <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, color: "#6b7280", marginBottom: 6 }}>
          <span>Progress</span>
          <span>{progress}%</span>
        </div>

        <div style={{ height: 10, width: "100%", background: "#EEEAFB", borderRadius: 999, overflow: "hidden" }}>
          <div style={{ height: "100%", width: `${progress}%`, background: "#9089FC", transition: "width .35s ease" }} />
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
