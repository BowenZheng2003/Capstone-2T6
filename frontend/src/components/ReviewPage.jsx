import React, { useMemo, useState } from "react";
import "./LandingPage.css";
import "./ReviewPage.css";
import topLeft from "../assets/Group 1.svg";
import bottomLeft from "../assets/Group 3.svg";
import rightImg from "../assets/Group 2.svg";

const EXAMPLE_CHIPS = [
  "Job interview at a tech company",
  "University lecture",
  "Sales pitch to investors",
  "Conference talk",
  "Product demo",
];

function formatBytes(bytes) {
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function ReviewPage({ file, onSubmit, onBack }) {
  const [context, setContext] = useState("");

  const isRecorded = file?.name === "recording.webm";
  const previewURL = useMemo(
    () => (isRecorded && file ? URL.createObjectURL(file) : null),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [file]
  );

  const handleSubmit = () => {
    const ctx = context.trim() || "General presentation";
    onSubmit(ctx);
  };

  return (
    <div className="landing-container" style={{ position: "relative" }}>
      <img src={topLeft} alt="" className="top-left-svg" />
      <img src={bottomLeft} alt="" className="bottom-left-svg" />
      <img src={rightImg} alt="" className="right-svg" />

      <div className="review-card">

        {/* File / Recording preview */}
        <div className="review-file-section">
          <h2 className="review-title">
            {isRecorded ? "Review your recording" : "Ready to analyze"}
          </h2>

          {isRecorded && previewURL ? (
            <video
              src={previewURL}
              controls
              className="review-video"
            />
          ) : (
            <div className="review-file-info">
              <span className="review-file-icon">🎬</span>
              <div>
                <div className="review-file-name">{file?.name}</div>
                <div className="review-file-size">{formatBytes(file?.size ?? 0)}</div>
              </div>
            </div>
          )}
        </div>

        {/* Context input */}
        <div className="review-context-section">
          <label className="review-label">
            What is your presentation about?
          </label>
          <p className="review-hint">
            This helps our AI give you more relevant and accurate feedback.
            Try to be specific — the more context, the better.
          </p>

          <div className="review-chips">
            {EXAMPLE_CHIPS.map((chip) => (
              <button
                key={chip}
                className={`review-chip ${context === chip ? "review-chip-active" : ""}`}
                onClick={() => setContext(context === chip ? "" : chip)}
                type="button"
              >
                {chip}
              </button>
            ))}
          </div>

          <textarea
            className="review-textarea"
            placeholder="e.g. A 5-minute sales pitch to Series A investors about our EdTech startup…"
            value={context}
            onChange={(e) => setContext(e.target.value)}
            rows={3}
          />
        </div>

        {/* Actions */}
        <div className="review-actions">
          <button className="review-btn-back" onClick={onBack} type="button">
            ← Back
          </button>
          <button className="review-btn-submit" onClick={handleSubmit} type="button">
            Analyze my presentation →
          </button>
        </div>

      </div>
    </div>
  );
}
