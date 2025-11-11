import React from "react";
import { Routes, Route } from "react-router-dom";
import LandingPage from "./components/landing_page";
import UploadPage from "./pages/UploadPage";
import AnalyzingPage from "./pages/AnalyzingPage";
import ResultsPage from "./pages/ResultsPage";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/upload" element={<UploadPage />} />
      <Route path="/analyzing" element={<AnalyzingPage apiBase="http://localhost:8000" />} />
      <Route path="/results" element={<ResultsPage apiBase="http://localhost:8000" />} />
    </Routes>
  );
}
