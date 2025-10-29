// src/App.jsx
import { useEffect, useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

function App() {
  const [count, setCount] = useState(0);
  const [message, setMessage] = useState("");
  const [transcription, setTranscription] = useState("");

  // Fetch a message from the backend on load
  useEffect(() => {
    fetch(`${API_BASE}/ping`)
      .then((res) => res.text())
      .then((data) => setMessage(data))
      .catch((err) => console.error("Error fetching ping:", err));
  }, []);

  const handleTranscribe = async () => {
    try {
      const res = await fetch(`${API_BASE}/transcribe_macbeth`);
      const text = await res.text();
      setTranscription(text);
    } catch (error) {
      console.error("Error during transcription:", error);
    }
  };

  return (
    <>
      <div>
        <a href="https://vite.dev" target="_blank">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>Vite + React</h1>
      <div className="card">
        <button onClick={() => setCount((count) => count + 1)}>
          count is {count}
        </button>
        <p>Backend says: <strong>{message}</strong></p>
        <button onClick={handleTranscribe}>
          Transcribe Macbeth
        </button>
        <pre style={{ whiteSpace: 'pre-wrap', marginTop: '1em' }}>{transcription}</pre>
      </div>
      <p className="read-the-docs">
        Click on the Vite and React logos to learn more
      </p>
    </>
  );
}

export default App;
