import React, { useRef, useState } from 'react';

import './LandingPage.css';
import top_left from '../assets/Group 1.svg';
import bottom_left from '../assets/Group 3.svg';
import right from '../assets/Group 2.svg';
import Recorder from './Recorder.jsx';

function LandingPage({ onFileReady }) {
  const fileInputRef = useRef(null);
  const [showRecorder, setShowRecorder] = useState(false);

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

  return (
    <div className="landing-container" style={{ position: 'relative' }}>
      <img src={top_left} alt="" className="top-left-svg" />
      <img src={bottom_left} alt="" className="bottom-left-svg" />
      <img src={right} alt="" className="right-svg" />

      <header>
        <h1>TEAM 2025167</h1>
        <p>Upload a video of your oral presentation</p>
        <p>Wait a minute or two for your personalized feedback!</p>

        <div className="action-buttons">
          <button
            onClick={handleUploadVideo}
            className="action-btn upload-btn"
          >
            Upload Video
          </button>
          <button onClick={handleRecordVideo} className="action-btn record-btn">
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
