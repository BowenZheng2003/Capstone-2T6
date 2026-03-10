// src/components/FeedbackDisplay.jsx
import React from 'react';
import './FeedbackDisplay.css';

function FeedbackDisplay({ data, report: reportProp, raw, onBack }) {
  const report = reportProp || data?.report || raw?.report;
  if (!report) return null;

  const formatTimestamp = (seconds) => {
    if (typeof seconds === 'string') return seconds;
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const scoreValue = typeof report.score === 'number' ? report.score : Number(report.score);
  const displayScore =
    Number.isFinite(scoreValue)
      ? (scoreValue > 10 ? Math.round(scoreValue / 10) : scoreValue)
      : report.score;

  const handleSavePDF = () => {
    window.print();
  };

  return (
    <div className="feedback-container">
      <div className="feedback-header">
        <div>
          <h2>📊 Presentation Feedback</h2>
          <p className="context">{report.context}</p>
        </div>

        <div className="header-actions no-print">
          {typeof onBack === 'function' && (
            <button onClick={onBack} className="btn-back">
              ← Back
            </button>
          )}
          <button onClick={handleSavePDF} className="btn-save-pdf">
            ⬇ Save as PDF
          </button>
        </div>
      </div>

      <div className="score-card">
        <div className="score-value">{displayScore}/10</div>
        <div className="score-label">Overall Score</div>
      </div>

      <div className="summary-section">
        <h3>📝 Summary</h3>
        <p>{report.summary}</p>
      </div>

      {report.strengths && report.strengths.length > 0 && (
        <div className="strengths-section">
          <h3>✅ Strengths</h3>
          {report.strengths.map((strength, idx) => (
            <div key={idx} className="strength-item">
              <p className="description">{strength.description}</p>
              {strength.evidence && strength.evidence.length > 0 && (
                <div className="evidence-tags">
                  {strength.evidence.map((ev, i) => (
                    <span key={i} className="timestamp-tag strength-tag">
                      🕐 {formatTimestamp(ev.ts_start)} - {formatTimestamp(ev.ts_end)}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {report.problems && report.problems.length > 0 && (
        <div className="problems-section">
          <h3>⚠️ Areas for Improvement</h3>
          {report.problems.map((problem, idx) => (
            <div key={idx} className="problem-item">
              <p className="description">{problem.description}</p>
              {problem.evidence && problem.evidence.length > 0 && (
                <div className="evidence-container">
                  {problem.evidence.map((ev, i) => (
                    <div key={i} className="evidence-item">
                      <span className="timestamp-tag problem-tag">
                        🕐 {formatTimestamp(ev.ts_start)} - {formatTimestamp(ev.ts_end)}
                      </span>
                      {ev.suggestion && (
                        <div className="suggestion-box">
                          💡 <strong>Suggestion:</strong> {ev.suggestion}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default FeedbackDisplay;
