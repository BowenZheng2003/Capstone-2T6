// src/components/landing_page.js
import React, { useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Recorder from './Recorder';

import './LandingPage.css';
import top_left from '../assets/Group 1.svg';
import bottom_left from '../assets/Group 3.svg';
import right from '../assets/Group 2.svg';

const API_BASE = 'http://localhost:8000';
const pick = (obj, keys) => keys.reduce((v, k) => (v ?? obj?.[k]), undefined);

function LandingPage() {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  const [showRecorder, setShowRecorder] = useState(false);

  const handleUploadVideo = () => fileInputRef.current?.click();

  // Open the recording modal
  const handleRecordVideo = () => setShowRecorder(true);

  // When the Recorder finishes uploading, route like the file-upload path
  const handleRecorderUploaded = (result) => {
    if (result?.job_id || result?.jobId) {
      const jobId = result.job_id || result.jobId;
      navigate(`/analyzing?jobId=${encodeURIComponent(jobId)}`);
    } else {
      const reportText =
        result.report_text || result.report || result.output || result.message || '';
      navigate('/results', { state: { reportText, meta: result } });
    }
    setShowRecorder(false);
  };

  // File picker -> upload -> navigate
  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // 1) Clear previous run markers
    localStorage.removeItem('latestReportText');
    localStorage.removeItem('latestReportMeta');
    localStorage.removeItem('latestReportReady');
    localStorage.removeItem('uploadError');

    // 2) Immediately show waiting page
    localStorage.setItem('uploadInProgress', '1');
    navigate('/analyzing?client=1'); // <- you should see Analyzing now

    // 3) Kick off the upload in the background (next tick)
    setTimeout(async () => {
      try {
        const formData = new FormData();
        formData.append('file', file);

        const res = await fetch(`${API_BASE}/process_video`, { method: 'POST', body: formData });
        if (!res.ok) throw new Error(`Upload failed: ${await res.text()}`);
        const data = await res.json();

        // Optional future: if your backend returns a job id
        const jobId = data.job_id || data.jobId;
        if (jobId) {
          navigate(`/analyzing?jobId=${encodeURIComponent(jobId)}`, { replace: true });
          return;
        }

        // Synchronous case: stash and go to results
        const reportText =
          data.report_text || data.report || data.output || data.evaluation || data.message || '';

        localStorage.setItem('latestReportText', reportText);
        localStorage.setItem('latestReportMeta', JSON.stringify(data));
        localStorage.setItem('latestReportReady', '1');
        localStorage.setItem('uploadInProgress', '0');

        navigate('/results', { state: { reportText, meta: data }, replace: true });
      } catch (err) {
        console.error(err);
        localStorage.setItem('uploadError', err.message || 'Upload failed');
        localStorage.setItem('uploadInProgress', '0');
        // Analyzing page will show the error banner
      } finally {
        e.target.value = ''; // allow re-selecting the same file
      }
    }, 0);
  };

  return (
    <div className="landing-container" style={{ position: 'relative' }}>
      <img src={top_left} alt="" className="top-left-svg" />
      <img src={bottom_left} alt="" className="bottom-left-svg" />
      <img src={right} alt="" className="right-svg" />

      <header>
        <h1>BEYOND WORDS</h1>
        <p>Multi-Modal AI-Driven Presentation Evaluator</p>
        <p>What you say, how you sound, and how you look—measured together.</p>

        <div className="action-buttons">
          <button onClick={handleUploadVideo} className="action-btn upload-btn">Upload Video</button>
          <button onClick={handleRecordVideo} className="action-btn record-btn">Record Video</button>
        </div>

        {/* hidden file input */}
        <input type="file" ref={fileInputRef} onChange={handleFileChange} style={{ display: 'none' }} />
      </header>

      {showRecorder && (
        <Recorder
          apiBase={API_BASE}
          onUploaded={handleRecorderUploaded}
          onClose={() => setShowRecorder(false)}
        />
      )}
    </div>
  );
}

export default LandingPage;
