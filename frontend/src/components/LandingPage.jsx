import React, { useRef, useState } from 'react';

import './LandingPage.css';
import top_left from '../assets/Group 1.svg';
import bottom_left from '../assets/Group 3.svg';
import right from '../assets/Group 2.svg';
import Recorder from './Recorder.jsx';

function LandingPage({ onFileReady }) {
  const fileInputRef = useRef(null);
  const [showRecorder, setShowRecorder] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [dropError, setDropError] = useState("");
  const dragCounterRef = useRef(0);

  const handleUploadVideo = () => {
    fileInputRef.current.click();
  };

  const handleRecordVideo = () => {
    setShowRecorder(true);
  };

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (!file) return;
    onFileReady?.(file);
  };

  const handleRecordingDone = (file) => {
    setShowRecorder(false);
    onFileReady?.(file);
  };

  const handleDragEnter = (e) => {
    e.preventDefault();
    dragCounterRef.current += 1;
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    dragCounterRef.current -= 1;
    if (dragCounterRef.current === 0) setIsDragging(false);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    dragCounterRef.current = 0;
    setIsDragging(false);
    setDropError("");
    const file = e.dataTransfer.files[0];
    if (!file) return;
    if (!file.type.startsWith("video/")) {
      setDropError("Please drop a video file.");
      return;
    }
    onFileReady?.(file);
  };

  return (
    <div className="landing-container" style={{ position: 'relative' }}>
      <img src={top_left} alt="" className="top-left-svg" />
      <img src={bottom_left} alt="" className="bottom-left-svg" />
      <img src={right} alt="" className="right-svg" />

      <header>
        <h1>TEAM 2025167</h1>
        <p>Upload a video of your oral presentation</p>
        <p>Wait a minute or two for your personalized feedback!</p>

        <div
          className={`drop-zone${isDragging ? " drop-zone--active" : ""}`}
          onClick={handleUploadVideo}
          onDragEnter={handleDragEnter}
          onDragLeave={handleDragLeave}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
        >
          <div className="drop-zone-icon">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="17 8 12 3 7 8"/>
              <line x1="12" y1="3" x2="12" y2="15"/>
            </svg>
          </div>
          <p className="drop-zone-text">
            {isDragging ? "Drop to upload" : "Drag & drop your video here"}
          </p>
          <span className="drop-zone-or">or</span>
          <span className="drop-zone-browse">click to browse</span>
          {dropError && <p className="drop-zone-error">{dropError}</p>}
        </div>

        <div className="action-buttons">
          <button onClick={handleRecordVideo} className="action-btn record-btn">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{marginRight:'6px',verticalAlign:'middle'}}>
              <path d="M23 7l-7 5 7 5V7z"/><rect x="1" y="5" width="15" height="14" rx="2" ry="2"/>
            </svg>
            Record Video
          </button>
        </div>

        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept="video/*"
          style={{ display: 'none' }}
        />
      </header>

      {showRecorder && (
        <Recorder
          onDone={handleRecordingDone}
          onClose={() => setShowRecorder(false)}
        />
      )}
    </div>
  );
}

export default LandingPage;
