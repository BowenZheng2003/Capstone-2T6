// src/components/FeedbackDisplay.jsx
import { useState } from 'react';
import './FeedbackDisplay.css';

const TABS = ['Overview', 'Strengths', 'Improvements'];

function ScoreRing({ score }) {
  const r = 50;
  const stroke = 8;
  const nr = r - stroke / 2;
  const circ = 2 * Math.PI * nr;
  const offset = circ - (Math.min(score, 10) / 10) * circ;
  return (
    <svg width={r * 2} height={r * 2} className="fd-score-ring-svg">
      <defs>
        <linearGradient id="sg" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#8D8DE9" />
          <stop offset="100%" stopColor="#6F6FDA" />
        </linearGradient>
      </defs>
      <circle cx={r} cy={r} r={nr} fill="none" stroke="#EEEAFB" strokeWidth={stroke} />
      <circle
        cx={r} cy={r} r={nr} fill="none"
        stroke="url(#sg)" strokeWidth={stroke}
        strokeDasharray={circ} strokeDashoffset={offset}
        strokeLinecap="round"
        transform={`rotate(-90 ${r} ${r})`}
        style={{ transition: 'stroke-dashoffset 1s ease' }}
      />
    </svg>
  );
}

function FeedbackDisplay({ data, report: reportProp, raw, onBack }) {
  const report = reportProp || data?.report || raw?.report;
  const [activeTab, setActiveTab] = useState('Overview');

  if (!report) return null;

  const formatTimestamp = (seconds) => {
    if (typeof seconds === 'string') return seconds;
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  };

  const rawScore = typeof report.score === 'number' ? report.score : Number(report.score);
  const displayScore = Number.isFinite(rawScore)
    ? (rawScore > 10 ? Math.round(rawScore / 10) : Math.round(rawScore * 10) / 10)
    : '–';

  const strengths = report.strengths || [];
  const problems = report.problems || [];

  const handleSavePDF = () => window.print();

  return (
    <div className="fd-page">

      {/* ── Sticky top bar ── */}
      <div className="fd-topbar no-print">
        <button onClick={onBack} className="fd-btn-back">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="15 18 9 12 15 6"/></svg>
          Back
        </button>
        <span className="fd-topbar-title">Presentation Feedback</span>
        <button onClick={handleSavePDF} className="fd-btn-pdf">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
          Save PDF
        </button>
      </div>

      {/* ── Tab bar ── */}
      <div className="fd-tabbar no-print">
        {TABS.map((tab) => (
          <button
            key={tab}
            className={`fd-tab${activeTab === tab ? ' fd-tab--active' : ''}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab}
            {tab === 'Strengths' && strengths.length > 0 && (
              <span className="fd-tab-badge fd-tab-badge--green">{strengths.length}</span>
            )}
            {tab === 'Improvements' && problems.length > 0 && (
              <span className="fd-tab-badge fd-tab-badge--red">{problems.length}</span>
            )}
          </button>
        ))}
      </div>

      {/* ── Tab content ── */}
      <div className="fd-content">

        {/* OVERVIEW */}
        {activeTab === 'Overview' && (
          <div className="fd-tab-panel" key="overview">
            <div className="fd-score-card">
              <div className="fd-score-ring-wrap">
                <ScoreRing score={displayScore} />
                <div className="fd-score-inner">
                  <div className="fd-score-nums">
                    <span className="fd-score-num">{displayScore}</span>
                    <span className="fd-score-sep">/</span>
                    <span className="fd-score-denom">10</span>
                  </div>
                </div>
              </div>
              <div className="fd-score-info">
                <div className="fd-score-label">Overall Score</div>
                {report.context && (
                  <div className="fd-context-pill">{report.context}</div>
                )}
              </div>
            </div>

            <div className="fd-section-card fd-summary-card">
              <h3 className="fd-section-title">Summary</h3>
              <p className="fd-section-body">{report.summary}</p>
            </div>

            <div className="fd-stats-row">
              <button
                className="fd-stat fd-stat--green fd-stat-btn"
                onClick={() => setActiveTab('Strengths')}
              >
                <span className="fd-stat-num">{strengths.length}</span>
                <span className="fd-stat-label">Strengths →</span>
              </button>
              <button
                className="fd-stat fd-stat--red fd-stat-btn"
                onClick={() => setActiveTab('Improvements')}
              >
                <span className="fd-stat-num">{problems.length}</span>
                <span className="fd-stat-label">Areas to Improve →</span>
              </button>
            </div>
          </div>
        )}

        {/* STRENGTHS */}
        {activeTab === 'Strengths' && (
          <div className="fd-tab-panel" key="strengths">
            {strengths.length === 0 ? (
              <p className="fd-empty">No strengths recorded.</p>
            ) : strengths.map((s, idx) => (
              <div key={idx} className="fd-item fd-item--green">
                <div className="fd-item-num">{idx + 1}</div>
                <div className="fd-item-body">
                  <p className="fd-item-desc">{s.description}</p>
                  {s.evidence && s.evidence.length > 0 && (
                    <div className="fd-timestamps">
                      {s.evidence.map((ev, i) => (
                        <span key={i} className="fd-ts-badge fd-ts-badge--green">
                          🕐 {formatTimestamp(ev.ts_start)} – {formatTimestamp(ev.ts_end)}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* IMPROVEMENTS */}
        {activeTab === 'Improvements' && (
          <div className="fd-tab-panel" key="improvements">
            {problems.length === 0 ? (
              <p className="fd-empty">No issues found — great job!</p>
            ) : problems.map((p, idx) => (
              <div key={idx} className="fd-item fd-item--red">
                <div className="fd-item-num fd-item-num--red">{idx + 1}</div>
                <div className="fd-item-body">
                  <p className="fd-item-desc">{p.description}</p>
                  {p.evidence && p.evidence.length > 0 && (
                    <div className="fd-evidence-list">
                      {p.evidence.map((ev, i) => (
                        <div key={i} className="fd-evidence-block">
                          <span className="fd-ts-badge fd-ts-badge--red">
                            🕐 {formatTimestamp(ev.ts_start)} – {formatTimestamp(ev.ts_end)}
                          </span>
                          {ev.suggestion && (
                            <div className="fd-suggestion">
                              💡 <strong>Suggestion:</strong> {ev.suggestion}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ── Print-only: all sections visible ── */}
      <div className="fd-print-only">
        <h1>Presentation Feedback</h1>
        <p><strong>Context:</strong> {report.context}</p>
        <p><strong>Score:</strong> {displayScore}/10</p>
        <h2>Summary</h2>
        <p>{report.summary}</p>
        <h2>Strengths</h2>
        {strengths.map((s, i) => (
          <div key={i} style={{ marginBottom: '1rem' }}>
            <p><strong>{i + 1}.</strong> {s.description}</p>
            {s.evidence?.map((ev, j) => (
              <p key={j} style={{ marginLeft: '1rem', color: '#555', fontSize: '0.9rem' }}>
                🕐 {formatTimestamp(ev.ts_start)} – {formatTimestamp(ev.ts_end)}
              </p>
            ))}
          </div>
        ))}
        <h2>Areas for Improvement</h2>
        {problems.map((p, i) => (
          <div key={i} style={{ marginBottom: '1rem' }}>
            <p><strong>{i + 1}.</strong> {p.description}</p>
            {p.evidence?.map((ev, j) => (
              <div key={j} style={{ marginLeft: '1rem', marginBottom: '0.5rem' }}>
                <p style={{ color: '#555', fontSize: '0.9rem' }}>
                  🕐 {formatTimestamp(ev.ts_start)} – {formatTimestamp(ev.ts_end)}
                </p>
                {ev.suggestion && <p style={{ fontSize: '0.9rem' }}>💡 {ev.suggestion}</p>}
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

export default FeedbackDisplay;
