// src/pages/AnalyzingPage.jsx
import { useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

import '../components/LandingPage.css';
import top_left from '../assets/Group 1.svg';
import bottom_left from '../assets/Group 3.svg';
import right from '../assets/Group 2.svg';

const BG_LIGHT = '#FDF2EC';
const BG_DARK  = '#12112C';
const ACCENT   = '#9089FC';
const PULSE_SECONDS = 14;

const FALLBACK_MESSAGES = [
  'Waiting for the job to start…',
  'Preparing analysis pipeline…',
  'Standing by…',
];

const MSG_ROTATE_MS = 3500;
const POLL_MS = 1200;

export default function AnalyzingPage({ apiBase = 'http://localhost:8000' }) {
  const [params] = useSearchParams();
  const jobId = params.get('jobId') || '';
  const clientMode = params.get('client') === '1'; // ← NEW
  const navigate = useNavigate();

  const [messageIndex, setMessageIndex] = useState(0);
  const [progress, setProgress] = useState(0);
  const [phase, setPhase] = useState('');
  const [error, setError] = useState(null);

  useEffect(() => {
    const t = setInterval(() => setMessageIndex(i => (i + 1) % FALLBACK_MESSAGES.length), MSG_ROTATE_MS);
    return () => clearInterval(t);
  }, []);

  const currentMessage = useMemo(() => phase || FALLBACK_MESSAGES[messageIndex], [phase, messageIndex]);

  const timerRef = useRef(null);

  // ----- Client mode: watch localStorage flags set by LandingPage -----
  useEffect(() => {
    if (!clientMode) return;

    let canceled = false;

    // gentle auto-progress
    const tick = () => setProgress(p => Math.min(99, p + Math.random() * 7));

    const watch = () => {
      if (canceled) return;

      const ready = localStorage.getItem('latestReportReady') === '1';
      const err = localStorage.getItem('uploadError');
      const inProgress = localStorage.getItem('uploadInProgress') === '1';

      if (err) {
        setError(err);
        clearInterval(timerRef.current);
        timerRef.current = null;
        setProgress(0);
        return;
      }

      if (ready) {
        clearInterval(timerRef.current);
        timerRef.current = null;

        const reportText = localStorage.getItem('latestReportText') || '';
        const meta = (() => { try { return JSON.parse(localStorage.getItem('latestReportMeta') || '{}'); } catch { return {}; } })();

        navigate('/results', { state: { reportText, meta }, replace: true });
        return;
      }

      if (inProgress) tick();
    };

    timerRef.current = setInterval(watch, POLL_MS);
    return () => { canceled = true; if (timerRef.current) clearInterval(timerRef.current); };
  }, [clientMode, navigate]);

  // ----- Server mode: real polling by jobId -----
  useEffect(() => {
    if (clientMode || !jobId) return;

    let canceled = false;

    const poll = async () => {
      try {
        const res = await fetch(`${apiBase}/api/jobs/${encodeURIComponent(jobId)}/status`, { cache: 'no-store' });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const s = await res.json();
        if (canceled) return;

        if (typeof s.progress === 'number') setProgress(Math.max(0, Math.min(100, Math.round(s.progress))));
        if (s.phase || s.message) setPhase(s.phase || s.message);

        if (s.status === 'failed') { setError('The job failed. Please try again.'); stop(); }
        if (s.status === 'done')   {
          stop();
          navigate(`/report/${encodeURIComponent(s.reportId || jobId)}`, { replace: true });
        }
      } catch (e) {
        setError(e?.message || 'Failed to fetch');
      }
    };

    const start = () => { poll(); timerRef.current = setInterval(poll, POLL_MS); };
    const stop  = () => { if (timerRef.current) { clearInterval(timerRef.current); timerRef.current = null; } };

    start();
    return () => { canceled = true; stop(); };
  }, [apiBase, clientMode, jobId, navigate]);

  return (
    <div style={{ minHeight: '100svh', position: 'relative' }}>
      <div aria-hidden style={{ position: 'fixed', inset: 0, zIndex: 0, animation: `bgPulse ${PULSE_SECONDS}s ease-in-out infinite alternate` }} />
      <img src={top_left} alt="" className="top-left-svg" />
      <img src={bottom_left} alt="" className="bottom-left-svg" />
      <img src={right} alt="" className="right-svg" />

      <div style={{ minHeight: '100svh', display: 'grid', placeItems: 'center', padding: 24, fontFamily: 'Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif', position: 'relative', zIndex: 1 }}>
        <div style={{ width: 620, maxWidth: '92%', background: '#FFFFFF', borderRadius: 16, padding: 28, boxShadow: '0 12px 40px rgba(124, 58, 237, 0.08)' }}>
          <header style={{ textAlign: 'center', marginBottom: 18 }}>
            <h1 style={{ margin: 0, fontSize: 22, color: '#6C63FF', fontWeight: 700 }}>
              Analyzing your video
            </h1>
            <p style={{ marginTop: 8, color: '#6B7280', fontSize: 14 }}>
              {currentMessage}
            </p>
          </header>

          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, color: '#6b7280', marginBottom: 6 }}>
            <span>Progress</span><span>{progress}%</span>
          </div>
          <div style={{ height: 10, width: '100%', background: '#EEEAFB', borderRadius: 999, overflow: 'hidden' }}>
            <div style={{ height: '100%', width: `${progress}%`, background: ACCENT, transition: 'width .35s ease' }} />
          </div>

          {error && (
            <div style={{ marginTop: 14, border: '1px solid #FECACA', background: '#FEF2F2', color: '#B91C1C', borderRadius: 10, padding: 12, fontSize: 13 }}>
              <strong>Something went wrong</strong>
              <div style={{ fontSize: 12 }}>{error}</div>
            </div>
          )}
        </div>
      </div>

      <style>{`
        @keyframes bgPulse { 0% { background-color: ${BG_LIGHT}; } 100% { background-color: ${BG_DARK}; } }
      `}</style>
    </div>
  );
}
