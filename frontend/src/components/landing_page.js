import React, { useRef, useState } from 'react';

import './LandingPage.css';
import top_left from '../assets/Group 1.svg';
import bottom_left from '../assets/Group 3.svg';
import right from '../assets/Group 2.svg';
import FeedbackDisplay from './FeedbackDisplay'; 

function LandingPage() {
  const fileInputRef = useRef(null);

  // API state hooks
  const [rootMessage, setRootMessage] = useState('');
  const [pingResponse, setPingResponse] = useState('');
  const [transcriptResponse, settranscriptResponse] = useState('');
  const [echoText, setEchoText] = useState('');
  const [echoResponse, setEchoResponse] = useState('');
  const [showApiTesting, setShowApiTesting] = useState(false);
  const [uploadResponse, setUploadResponse] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const API_BASE = 'http://localhost:8000';

  const handleUploadVideo = () => {
    fileInputRef.current.click();
  };

  const handleRecordVideo = () => {
    alert('Record Video functionality will be implemented soon!');
  };

  const handleFileChange = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    setIsProcessing(true); // Show loading
    try {
      const response = await fetch(`${API_BASE}/process_video`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Upload failed: ${errorText}`);
      }

      const result = await response.json();
      console.log('✅ Server Response:', result);

      setUploadResponse(result);
    } catch (err) {
      console.error('File upload failed:', err);
      alert('❌ File upload failed. See console for details.');
    } finally {
      setIsProcessing(false); // Hide loading
    }
  };

  // --- API testing functions ---
  const fetchRoot = async () => {
    try {
      const res = await fetch(`${API_BASE}/`);
      const data = await res.json();
      setRootMessage(data.message);
    } catch (err) {
      console.error(err);
      setRootMessage('Error fetching /');
    }
  };

  const fetchPing = async () => {
    try {
      const res = await fetch(`${API_BASE}/ping`);
      const text = await res.text();
      setPingResponse(text);
    } catch (err) {
      console.error(err);
      setPingResponse('Error fetching /ping');
    }
  };

  const fetchTranscribe = async () => {
    try {
      const res = await fetch(`${API_BASE}/transcribe_macbeth`);
      const text = await res.text();
      settranscriptResponse(text);
    } catch (err) {
      console.error(err);
      settranscriptResponse('Error fetching /transcribe_macbeth');
    }
  };

  const fetchEcho = async () => {
    if (!echoText.trim()) return;
    try {
      const res = await fetch(`${API_BASE}/echo/${encodeURIComponent(echoText)}`);
      const data = await res.json();
      setEchoResponse(data.echo);
    } catch (err) {
      console.error(err);
      setEchoResponse('Error fetching /echo');
    }
  };

  return (
    <div className="landing-container" style={{ position: 'relative' }}>
      <img src={top_left} alt="My Icon" className="top-left-svg" />
      <img src={bottom_left} alt="My Icon" className="bottom-left-svg" />
      <img src={right} alt="My Icon" className="right-svg" />

      <header>
        <h1>TEAM 2025167</h1>
        <p>Upload a video of your oral presentation</p>
        <p>Wait a minute or two for your personalized feedback!</p>

        <div className="action-buttons">
          <button 
            onClick={handleUploadVideo} 
            className="action-btn upload-btn"
            disabled={isProcessing}
          >
            {isProcessing ? '⏳ Processing...' : 'Upload Video'}
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

      {/* Display upload JSON result */}
      {isProcessing && (
        <div className="processing-indicator">
          <div className="spinner"></div>
          <p>Analyzing your presentation...</p>
        </div>
      )}

      <FeedbackDisplay data={uploadResponse} />

      {/* API Testing Toggle */}
      <div className="api-toggle-section">
        <button 
          onClick={() => setShowApiTesting(!showApiTesting)}
          className="api-toggle-btn"
        >
          {showApiTesting ? '🔽 Hide API Testing' : '🔧 Show API Testing'}
        </button>
      </div>

      {/* Collapsible API Testing Section */}
      {showApiTesting && (
        <section className="api-testing">
          <h3>API Testing</h3>
          <div className="api-buttons">
            <button onClick={fetchRoot} className="api-btn">Test Root</button>
            <button onClick={fetchPing} className="api-btn">Test Ping</button>
            <button onClick={fetchTranscribe} className="api-btn">Test Transcribe</button>
          </div>
          
          <div className="echo-section">
            <input
              type="text"
              value={echoText}
              onChange={(e) => setEchoText(e.target.value)}
              placeholder="Type something to echo"
              className="echo-input"
            />
            <button onClick={fetchEcho} className="api-btn">Test Echo</button>
          </div>

          {/* API Responses */}
          <div className="api-responses">
            {rootMessage && <div><strong>Root:</strong> {rootMessage}</div>}
            {pingResponse && <div><strong>Ping:</strong> {pingResponse}</div>}
            {transcriptResponse && <div><strong>Transcribe:</strong> {transcriptResponse}</div>}
            {echoResponse && <div><strong>Echo:</strong> {echoResponse}</div>}
          </div>
        </section>
      )}
    </div>
  );
}

export default LandingPage;