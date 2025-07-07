import React, { useState } from 'react';

function App() {
  // Change this if your FastAPI is not on localhost:8000
  const API_BASE = 'http://localhost:8000';

  // state hooks
  const [rootMessage, setRootMessage] = useState('');
  const [pingResponse, setPingResponse] = useState('');
  const [transcriptResponse, settranscriptResponse] = useState('');
  const [echoText, setEchoText] = useState('');
  const [echoResponse, setEchoResponse] = useState('');

  // call GET /
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

  // call GET /ping
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

  // call GET /transcribe_macbeth
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

  // call GET /echo/{text}
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
    <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <h1>FastAPI ↔️ React</h1>

      {/* GET / */}
      <div style={{ marginBottom: '20px' }}>
        <button onClick={fetchRoot} style={{ padding: '8px 16px' }}>
          Get “/”
        </button>
        {rootMessage && (
          <p>
            <strong>Response:</strong> {rootMessage}
          </p>
        )}
      </div>

      {/* GET /ping */}
      <div style={{ marginBottom: '20px' }}>
        <button onClick={fetchPing} style={{ padding: '8px 16px' }}>
          Get /ping
        </button>
        {pingResponse && (
          <p>
            <strong>Response:</strong> {pingResponse}
          </p>
        )}
      </div>

      {/* GET /transcribe */}
      <div style={{ marginBottom: '20px' }}>
        <button onClick={fetchTranscribe} style={{ padding: '8px 16px' }}>
          Get /transcription
        </button>
        {transcriptResponse && (
          <p>
            <strong>Response:</strong> {transcriptResponse}
          </p>
        )}
      </div>

      {/* GET /echo/{text} */}
      <div>
        <input
          type="text"
          value={echoText}
          onChange={(e) => setEchoText(e.target.value)}
          placeholder="Type something to echo"
          style={{
            padding: '8px',
            width: '200px',
            marginRight: '8px',
          }}
        />
        <button onClick={fetchEcho} style={{ padding: '8px 16px' }}>
          Get /echo
        </button>
        {echoResponse && (
          <p>
            <strong>Response:</strong> {echoResponse}
          </p>
        )}
      </div>
    </div>
  );
}

export default App;
