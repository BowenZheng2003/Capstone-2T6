import React, { useRef } from 'react';

import './LandingPage.css'; // optional if using CSS
import top_left from '../assets/Group 1.svg';
import bottom_left from '../assets/Group 3.svg';

import right from '../assets/Group 2.svg';

function LandingPage() {
    const fileInputRef = useRef(null);

  const handleGetStarted = () => {
    // Trigger the hidden file input
    fileInputRef.current.click();
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
        <button onClick={handleGetStarted}>Get Started</button>
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          style={{ display: 'none' }}
        />
      </header>

      <section className="features">
        <h2>What We Do</h2>
        <p>Some description from your Figma copy</p>
      </section>

      {/* Add more sections based on your Figma design */}
    </div>
  );
}

export default LandingPage;