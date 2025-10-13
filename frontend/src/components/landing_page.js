import React, { useRef, useState } from 'react';

import './LandingPage.css'; // optional if using CSS
import top_left from '../assets/Group 1.svg';
import bottom_left from '../assets/Group 3.svg';

import right from '../assets/Group 2.svg';

function LandingPage() {
    const fileInputRef = useRef(null);
    
    // API state hooks
    const [rootMessage, setRootMessage] = useState('');
    const [pingResponse, setPingResponse] = useState('');
    const [transcriptResponse, settranscriptResponse] = useState('');
    const [echoText, setEchoText] = useState('');
    const [echoResponse, setEchoResponse] = useState('');
    const [showApiTesting, setShowApiTesting] = useState(false);

    const API_BASE = 'http://localhost:8000';

  const handleUploadVideo = () => {
    // Trigger the hidden file input
    fileInputRef.current.click();
  };

  const handleRecordVideo = () => {
    // Placeholder for record video functionality
    alert('Record Video functionality will be implemented soon!');
  };

  const handleFileChange = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file); // FastAPI should expect this as 'file'

    try {
      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      });

      const result = await response.text(); // Or .json() if you return JSON
      alert(`Response: You're all I can think of
            Every drop I drink up
            You're my soda pop
            My little soda pop (Yeah, yeah)
            Cool me down, you're so hot
            Pour me up, I won't stop (Oh, oh)
            You're my soda pop
            My little soda pop`);
    } catch (err) {
      console.error('File upload failed:', err);
      alert('File upload failed.');
    }
  };

  // API functions
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
      const res = await fetch(
        `${API_BASE}/echo/${encodeURIComponent(echoText)}`
      );
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
        <h1>SODA POP</h1>
        <p>Cool me down, you're so hot</p>
        <p>Pour me up, I won't stop</p>
          <p>You're my soda pop</p>
          <p>My little soda pop</p>
          <div className="action-buttons">
            <button onClick={handleUploadVideo} className="action-btn upload-btn">Upload Video</button>
            <button onClick={handleRecordVideo} className="action-btn record-btn">Record Video</button>
          </div>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            style={{ display: 'none' }}
          />
      </header>


      {/* API Testing Toggle Button */}
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
            {rootMessage && (
              <div className="response">
                <strong>Root Response:</strong> {rootMessage}
              </div>
            )}
            {pingResponse && (
              <div className="response">
                <strong>Ping Response:</strong> {pingResponse}
              </div>
            )}
            {transcriptResponse && (
              <div className="response">
                <strong>Transcribe Response:</strong> {transcriptResponse}
              </div>
            )}
            {echoResponse && (
              <div className="response">
                <strong>Echo Response:</strong> {echoResponse}
              </div>
            )}
          </div>
        </section>
      )}
    </div>
  );
}

export default LandingPage;