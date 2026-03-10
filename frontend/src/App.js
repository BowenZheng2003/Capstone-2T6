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
      <ReviewPage
        file={file}
        onSubmit={handleReviewSubmit}
        onBack={handleBack}
      />
    );
  }

  if (page === "analyzing") {
    return (
      <AnalyzingPage
        file={file}
        context={context}
        apiBase={API_BASE}
        onCancel={handleBack}
        onDone={handleDone}
      />
    );
  }

  if (page === "feedback") {
    return (
      <FeedbackDisplay
        report={result?.report}
        raw={result}
        onBack={handleBack}
      />
    );
  }

  return <LandingPage onFileReady={handleFileReady} />;
}
