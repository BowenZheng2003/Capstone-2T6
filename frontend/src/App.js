import React, { useState } from "react";
import LandingPage from "./components/LandingPage";
import ReviewPage from "./components/ReviewPage";
import AnalyzingPage from "./components/AnalyzingPage";
import FeedbackDisplay from "./components/FeedbackDisplay";

const API_BASE = "http://localhost:8000";

export default function App() {
  const [page, setPage] = useState("landing"); // 'landing' | 'review' | 'analyzing' | 'feedback'
  const [file, setFile] = useState(null);
  const [context, setContext] = useState("");
  const [result, setResult] = useState(null);

  const handleFileReady = (f) => {
    setFile(f);
    setPage("review");
  };

  const handleReviewSubmit = (ctx) => {
    setContext(ctx);
    setPage("analyzing");
  };

  const handleDone = (json) => {
    setResult(json);
    setPage("feedback");
  };

  const handleBack = () => {
    setPage("landing");
    setFile(null);
    setContext("");
    setResult(null);
  };

  if (page === "review") {
    return (
      <div key="review" className="page-transition">
        <ReviewPage
          file={file}
          onSubmit={handleReviewSubmit}
          onBack={handleBack}
        />
      </div>
    );
  }

  if (page === "analyzing") {
    return (
      <div key="analyzing" className="page-transition">
        <AnalyzingPage
          file={file}
          context={context}
          apiBase={API_BASE}
          onCancel={handleBack}
          onDone={handleDone}
        />
      </div>
    );
  }

  if (page === "feedback") {
    return (
      <div key="feedback" className="page-transition">
        <FeedbackDisplay
          report={result?.report}
          raw={result}
          onBack={handleBack}
        />
      </div>
    );
  }

  return (
    <div key="landing" className="page-transition">
      <LandingPage onFileReady={handleFileReady} />
    </div>
  );
}
