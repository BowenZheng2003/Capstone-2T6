// src/components/Recorder.jsx
import React, { useEffect, useRef, useState } from 'react';

export default function Recorder({ apiBase = 'http://localhost:8000', onUploaded, onClose }) {
  const liveRef = useRef(null);
  const recRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const streamRef = useRef(null);
  const chunksRef = useRef([]);

  const [recording, setRecording] = useState(false);
  const [previewURL, setPreviewURL] = useState(null); // blob URL once stopped
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  // Request camera/mic on mount
  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        if (!mounted) return;
        streamRef.current = stream;
        if (liveRef.current) {
          liveRef.current.srcObject = stream;
          await liveRef.current.play().catch(() => {});
        }
      } catch (e) {
        setError('Could not access camera/microphone.');
      }
    })();
    return () => {
      mounted = false;
      stopStream();
      URL.revokeObjectURL(previewURL || '');
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const stopStream = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(t => t.stop());
      streamRef.current = null;
    }
  };

  const startRecording = () => {
    setError('');
    chunksRef.current = [];
    if (!streamRef.current) {
      setError('No media stream available.');
      return;
    }
    const mr = new MediaRecorder(streamRef.current, { mimeType: 'video/webm;codecs=vp9,opus' });
    mediaRecorderRef.current = mr;
    mr.ondataavailable = (ev) => {
      if (ev.data && ev.data.size > 0) chunksRef.current.push(ev.data);
    };
    mr.onstop = () => {
      const blob = new Blob(chunksRef.current, { type: 'video/webm' });
      const url = URL.createObjectURL(blob);
      setPreviewURL(prev => {
        if (prev) URL.revokeObjectURL(prev);
        return url;
      });
    };
    mr.start();
    setRecording(true);
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
    setRecording(false);
    // hide live video after stopping (preview will show)
    if (liveRef.current) liveRef.current.srcObject = null;
  };

  const reRecord = async () => {
    // cleanup previous preview
    if (previewURL) URL.revokeObjectURL(previewURL);
    setPreviewURL(null);
    setError('');
    // re-request the stream and show live again
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
      streamRef.current = stream;
      if (liveRef.current) {
        liveRef.current.srcObject = stream;
        await liveRef.current.play().catch(() => {});
      }
      setRecording(false);
    } catch (e) {
      setError('Could not reinitialize camera/microphone.');
    }
  };

  const upload = async () => {
    if (!previewURL || busy) return;
    setBusy(true);
    setError('');
    try {
      const blob = await fetch(previewURL).then(r => r.blob());
      const file = new File([blob], 'recording.webm', { type: blob.type || 'video/webm' });

      const formData = new FormData();
      formData.append('file', file);

      const res = await fetch(`${apiBase}/process_video`, { method: 'POST', body: formData });
      if (!res.ok) throw new Error(`Upload failed: ${await res.text()}`);
      const json = await res.json();
      onUploaded?.(json);
    } catch (e) {
      setError(e?.message || 'Upload failed.');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div style={styles.backdrop}>
      <div style={styles.modal}>
        {/* Always-visible close button */}
        <button
          type="button"
          onClick={onClose}
          aria-label="Close"
          style={styles.closeBtn}
        >
          ×
        </button>

        <h2 style={{ margin: '0 0 12px' }}>Record your presentation</h2>
        <p style={{ margin: '0 0 16px', color: '#6b7280', fontSize: 14 }}>
          Start recording, then stop to preview and upload. You can re-record before uploading.
        </p>

        {/* Video area (kept inside the viewport) */}
        <div style={styles.videoShell}>
          {/* LIVE feed only when not previewing and we have a stream */}
          {!previewURL && (
            <video
              ref={liveRef}
              playsInline
              muted
              style={styles.video}
            />
          )}

          {/* PREVIEW only after stop */}
          {previewURL && (
            <video
              ref={recRef}
              src={previewURL}
              controls
              playsInline
              style={styles.video}
            />
          )}
        </div>

        {/* Controls */}
        <div style={styles.controls}>
          {!recording && !previewURL && (
            <button style={styles.primary} onClick={startRecording}>
              ⏺ Start
            </button>
          )}

          {recording && (
            <button style={styles.warn} onClick={stopRecording}>
              ⏹ Stop
            </button>
          )}

          {!recording && previewURL && (
            <>
              <button style={styles.secondary} onClick={reRecord} disabled={busy}>
                🔁 Re-record
              </button>
              <button style={styles.primary} onClick={upload} disabled={busy}>
                ⬆ Upload
              </button>
            </>
          )}
        </div>

        {error && (
          <div style={styles.errorBox}>
            {error}
          </div>
        )}
      </div>
    </div>
  );
}

const styles = {
  backdrop: {
    position: 'fixed',
    inset: 0,
    background: 'rgba(0,0,0,0.55)',
    display: 'grid',
    placeItems: 'center',
    zIndex: 1000,
    padding: 16,
  },
  modal: {
    position: 'relative',
    width: 'min(860px, 94vw)',
    maxHeight: '90vh',
    background: '#fff',
    borderRadius: 14,
    boxShadow: '0 20px 60px rgba(0,0,0,0.25)',
    padding: 20,
    overflow: 'hidden',
    display: 'flex',
    flexDirection: 'column',
  },
  closeBtn: {
    position: 'absolute',
    top: 8,
    right: 10,
    width: 36,
    height: 36,
    borderRadius: 18,
    border: '1px solid #e5e7eb',
    background: '#111827',
    color: '#fff',
    fontSize: 22,
    lineHeight: '32px',
    textAlign: 'center',
    cursor: 'pointer',
    zIndex: 1001,
  },
  videoShell: {
    flex: '1 1 auto',
    display: 'grid',
    placeItems: 'center',
    overflow: 'auto',
    borderRadius: 12,
    border: '1px solid #eef',
    background: '#f9fafb',
    marginBottom: 12,
    maxHeight: '60vh', // keep in viewport
  },
  video: {
    maxWidth: '100%',
    maxHeight: '58vh',
    borderRadius: 10,
    background: '#000',
  },
  controls: {
    display: 'flex',
    gap: 10,
    justifyContent: 'flex-end',
    flexWrap: 'wrap',
  },
  primary: {
    background: '#4F46E5',
    color: '#fff',
    border: 'none',
    borderRadius: 10,
    padding: '10px 14px',
    fontWeight: 600,
    cursor: 'pointer',
  },
  secondary: {
    background: '#EEF2FF',
    color: '#4338CA',
    border: '1px solid #E0E7FF',
    borderRadius: 10,
    padding: '10px 14px',
    fontWeight: 600,
    cursor: 'pointer',
  },
  warn: {
    background: '#FEE2E2',
    color: '#B91C1C',
    border: '1px solid #FCA5A5',
    borderRadius: 10,
    padding: '10px 14px',
    fontWeight: 700,
    cursor: 'pointer',
  },
  errorBox: {
    marginTop: 10,
    border: '1px solid #FECACA',
    background: '#FEF2F2',
    color: '#991B1B',
    borderRadius: 10,
    padding: 10,
    fontSize: 13,
  },
};
