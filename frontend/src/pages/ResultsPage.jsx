// ResultsPage.jsx
import { useLocation, Link } from "react-router-dom";
import { useMemo } from "react";

export default function ResultsPage() {
  const { state } = useLocation() || {};

  const reportText = useMemo(() => {
    if (state?.reportText) return state.reportText;
    const fromLS = localStorage.getItem("latestReportText");
    return fromLS || "";
  }, [state]);

  const meta = useMemo(() => {
    if (state?.meta) return state.meta;
    try { return JSON.parse(localStorage.getItem("latestReportMeta") || "null"); }
    catch { return null; }
  }, [state]);

  if (!reportText) {
    return (
      <main style={{ padding: 24 }}>
        <h1>Results</h1>
        <p>No report found. Try uploading again.</p>
        <p><Link to="/">Analyze another video</Link></p>
      </main>
    );
  }

  return (
    <main style={{ padding: 24, maxWidth: 900, margin: "0 auto", lineHeight: 1.6 }}>
      <h1>Results</h1>
      <pre style={{ whiteSpace: "pre-wrap" }}>{reportText}</pre>
      {meta && (
        <>
          <h3>Raw response (debug)</h3>
          <pre style={{ overflowX: "auto" }}>{JSON.stringify(meta, null, 2)}</pre>
        </>
      )}
      <p><Link to="/">Analyze another video</Link></p>
    </main>
  );
}
