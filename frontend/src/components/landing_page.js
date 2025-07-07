import React from 'react';
import './LandingPage.css'; // optional if using CSS
import top_left from '../assets/Group 1.svg';
import bottom_left from '../assets/Group 3.svg';

import right from '../assets/Group 2.svg';

function LandingPage() {
    const handleGetStarted = async () => {
    try {
      const res = await fetch('http://localhost:8000/sodapop'); // Replace with your actual endpoint
      const data = await res.text(); // or res.json() if the response is JSON
      console.log('API Response:', data);
      alert(`Response: ${data}`);
    } catch (error) {
      console.error('API call failed:', error);
      alert('Error making API call');
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