import React, { useEffect, useRef, useState } from "react";

export default function Recorder({ onDone, onClose }) {
  const liveRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const streamRef = useRef(null);
  const chunksRef = useRef([]);

  const [recording, setRecording] = useState(false);
  const [previewURL, setPreviewURL] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let mounted = true;

    (async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        if (!mounted) return;

        streamRef.current = stream;
        if (liveRef.current) {
          liveRef.current.srcObject = stream;
          await liveRef.current.play().catch(() => {});
        }
      } catch (e) {
        setError("Could not access camera/microphone. Check browser permissions.");
      }
    })();

    return () => {
      mounted = false;
      stopStream();
      if (previewURL) URL.revokeObjectURL(previewURL);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const stopStream = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
  };

  const pickMimeType = () => {
    const candidates = [
      "video/webm;codecs=vp9,opus",
      "video/webm;codecs=vp8,opus",
      "video/webm",
    ];
    for (const t of candidates) {
      if (window.MediaRecorder?.isTypeSupported?.(t)) return t;
    }
    return "";
  };

  const startRecording = () => {
    setError("");
    chunksRef.current = [];

    if (!streamRef.current) {
      setError("No media stream available.");
      return;
    }

    const mimeType = pickMimeType();
    let mr;
    try {
      mr = mimeType
        ? new MediaRecorder(streamRef.current, { mimeType })
        : new MediaRecorder(streamRef.current);
    } catch (e) {
      setError("MediaRecorder could not start (unsupported browser/codecs). Try Chrome/Edge.");
      return;
    }

    mediaRecorderRef.current = mr;

    mr.ondataavailable = (ev) => {
      if (ev.data && ev.data.size > 0) chunksRef.current.push(ev.data);
    };

    mr.onstop = () => {
      const blob = new Blob(chunksRef.current, { type: mimeType || "video/webm" });
      const url = URL.createObjectURL(blob);
      setPreviewURL((prev) => {
        if (prev) URL.revokeObjectURL(prev);
        return url;
      });
    };

    mr.start(250);
    setRecording(true);
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
      mediaRecorderRef.current.stop();
    }
    setRecording(false);
    if (liveRef.current) liveRef.current.srcObject = null;
    stopStream(); // turn camera off after stop
  };

  const reRecord = async () => {
    if (previewURL) URL.revokeObjectURL(previewURL);
    setPreviewURL(null);
    setError("");

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
      streamRef.current = stream;
      if (liveRef.current) {
        liveRef.current.srcObject = stream;
        await liveRef.current.play().catch(() => {});
      }
      setRecording(false);
    } catch (e) {
      setError("Could not reinitialize camera/microphone.");
    }
  };

  const useRecording = async () => {
    if (!previewURL) return;
    try {
      const blob = await fetch(previewURL).then((r) => r.blob());
      const file = new File([blob], "recording.webm", { type: blob.type || "video/webm" });
      onDone?.(file);
    } catch (e) {
      setError("Could not convert recording to file.");
    }
  };

  return (
    <div style={styles.backdrop}>
      <div style={styles.modal}>
        <button type="button" onClick={onClose} aria-label="Close" style={styles.closeBtn}>
          ×
        </button>

        <h2 style={{ margin: "0 0 12px" }}>Record your presentation</h2>
        <p style={{ margin: "0 0 16px", color: "#6b7280", fontSize: 14 }}>
          Start recording, stop to preview, then use it.
        </p>

        <div style={styles.videoShell}>
          {!previewURL && <video ref={liveRef} playsInline muted style={styles.video} />}
          {previewURL && <video src={previewURL} controls playsInline style={styles.video} />}
        </div>

        <div style={styles.controls}>
          {!recording && !previewURL && (
            <button style={styles.primary} onClick={startRecording}>
              ⏺ Start
            </button>
          )}

          {recording && (
            <button style={styles.warn} onClick={stopRecording}>
              ⏹ Stop
            </button>
          )}

          {!recording && previewURL && (
            <>
              <button style={styles.secondary} onClick={reRecord}>
                🔁 Re-record
              </button>
              <button style={styles.primary} onClick={useRecording}>
                ✅ Use this recording
              </button>
            </>
          )}
        </div>

        {error && <div style={styles.errorBox}>{error}</div>}
      </div>
    </div>
  );
}

const styles = {
  backdrop: {
    position: "fixed",
    inset: 0,
    background: "rgba(0,0,0,0.55)",
    display: "grid",
    placeItems: "center",
    zIndex: 1000,
    padding: 16,
  },
  modal: {
    position: "relative",
    width: "min(860px, 94vw)",
    maxHeight: "90vh",
    background: "#fff",
    borderRadius: 14,
    boxShadow: "0 20px 60px rgba(0,0,0,0.25)",
    padding: 20,
    overflow: "hidden",
    display: "flex",
    flexDirection: "column",
  },
  closeBtn: {
    position: "absolute",
    top: 8,
    right: 10,
    width: 36,
    height: 36,
    borderRadius: 18,
    border: "1px solid #e5e7eb",
    background: "#111827",
    color: "#fff",
    fontSize: 22,
    lineHeight: "32px",
    textAlign: "center",
    cursor: "pointer",
    zIndex: 1001,
  },
  videoShell: {
    flex: "1 1 auto",
    display: "grid",
    placeItems: "center",
    overflow: "auto",
    borderRadius: 12,
    border: "1px solid #eef",
    background: "#f9fafb",
    marginBottom: 12,
    maxHeight: "60vh",
  },
  video: {
    maxWidth: "100%",
    maxHeight: "58vh",
    borderRadius: 10,
    background: "#000",
  },
  controls: {
    display: "flex",
    gap: 10,
    justifyContent: "flex-end",
    flexWrap: "wrap",
  },
  primary: {
    background: "#4F46E5",
    color: "#fff",
    border: "none",
    borderRadius: 10,
    padding: "10px 14px",
    fontWeight: 600,
    cursor: "pointer",
  },
  secondary: {
    background: "#EEF2FF",
    color: "#4338CA",
    border: "1px solid #E0E7FF",
    borderRadius: 10,
    padding: "10px 14px",
    fontWeight: 600,
    cursor: "pointer",
  },
  warn: {
    background: "#FEE2E2",
    color: "#B91C1C",
    border: "1px solid #FCA5A5",
    borderRadius: 10,
    padding: "10px 14px",
    fontWeight: 700,
    cursor: "pointer",
  },
  errorBox: {
    marginTop: 10,
    border: "1px solid #FECACA",
    background: "#FEF2F2",
    color: "#991B1B",
    borderRadius: 10,
    padding: 10,
    fontSize: 13,
  },
};
