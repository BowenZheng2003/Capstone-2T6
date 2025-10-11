import { useState, useRef } from 'react'
import './App.css'

const API_BASE_URL = 'http://localhost:8000'

function App() {
  const [selectedFile, setSelectedFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [processing, setProcessing] = useState(false)
  const [processingId, setProcessingId] = useState(null)
  const [status, setStatus] = useState(null)
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)
  const [currentStep, setCurrentStep] = useState('')
  const [progress, setProgress] = useState(0)
  const fileInputRef = useRef(null)
  const statusIntervalRef = useRef(null)

  const handleFileSelect = (event) => {
    const file = event.target.files[0]
    if (file && file.type.startsWith('video/')) {
      setSelectedFile(file)
      setError(null)
    } else {
      setError('Please select a valid video file')
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) return

    setUploading(true)
    setError(null)

    try {
      // Mock backend response - simulate network delay
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      // Generate a mock processing ID
      const mockProcessingId = `mock_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
      
      setProcessingId(mockProcessingId)
      setStatus('uploaded')
      
    } catch (err) {
      setError(`Upload failed: ${err.message}`)
    } finally {
      setUploading(false)
    }
  }

  const handleProcess = async () => {
    if (!processingId) return

    setProcessing(true)
    setError(null)
    setProgress(0)
    setCurrentStep('')

    try {
      // Set status to processing to show the loading panel
      setStatus('processing')
      
      // Mock processing simulation with real-time updates
      console.log('Starting mock processing...')
      
      // Simulate processing steps with progress updates
      const steps = [
        { step: 'Extracting audio...', progress: 20, delay: 2000 },
        { step: 'Generating transcription...', progress: 40, delay: 3000 },
        { step: 'Analyzing audio features...', progress: 60, delay: 2500 },
        { step: 'Processing video frames...', progress: 80, delay: 2000 },
        { step: 'Generating report...', progress: 100, delay: 1500 }
      ]

      for (const { step, progress, delay } of steps) {
        setCurrentStep(step)
        setProgress(progress)
        console.log(step)
        await new Promise(resolve => setTimeout(resolve, delay))
      }

      // Mock successful completion
      setStatus('completed')
      setProcessing(false)
      setCurrentStep('Analysis complete!')
      
      // Generate mock results
      const mockResults = {
        status: "completed",
        video_path: selectedFile?.name || "test_video.mp4",
        steps_completed: [
          "audio_extraction",
          "transcription", 
          "audio_analysis",
          "video_analysis",
          "data_combination",
          "report_generation"
        ],
        results: {
          transcription: [
            {
              timestamp: "0:00 - 0:05",
              transcription: "Hello everyone, welcome to my presentation about artificial intelligence and machine learning applications in modern technology."
            },
            {
              timestamp: "0:05 - 0:10", 
              transcription: "Today I'll be covering three main topics: the fundamentals of AI, real-world applications, and future trends."
            }
          ],
          audio_analysis: [
            {
              timestamp: "0:00 - 0:05",
              confidence: "High Confidence (Expressive)",
              emotion: "Enthusiastic",
              analysis: "Strong vocal delivery with good energy and engagement"
            },
            {
              timestamp: "0:05 - 0:10",
              confidence: "Moderate Confidence", 
              emotion: "Neutral",
              analysis: "Clear speech with steady pace and good articulation"
            }
          ],
          video_analysis: [
            {
              timestamp: "0:00 - 0:05",
              smile_intensity: 0.7,
              eye_contact_ratio: 0.8,
              posture_score: 0.9,
              gesture_frequency: 0.6,
              clusters: {
                "authentic_smile": 0.7,
                "eyebrow_engagement": 0.8
              }
            },
            {
              timestamp: "0:05 - 0:10",
              smile_intensity: 0.4,
              eye_contact_ratio: 0.9,
              posture_score: 0.8,
              gesture_frequency: 0.5,
              clusters: {
                "focused_thinking": 0.6,
                "eyebrow_engagement": 0.7
              }
            }
          ],
          report: {
            overall_score: 8.5,
            strengths: [
              "Excellent eye contact and engagement",
              "Clear and confident vocal delivery", 
              "Good use of gestures and body language",
              "Well-structured content presentation"
            ],
            areas_for_improvement: [
              "Consider varying your speaking pace for emphasis",
              "Add more facial expressions to enhance engagement",
              "Include more interactive elements with the audience"
            ],
            recommendations: [
              "Practice with different audience sizes to build confidence",
              "Record yourself presenting to identify areas for improvement",
              "Consider using visual aids to support your key points"
            ]
          }
        }
      }
      
      setResults(mockResults)
      
    } catch (err) {
      setError(`Processing failed: ${err.message}`)
      setProcessing(false)
    }
  }

  const handleReset = () => {
    setSelectedFile(null)
    setProcessingId(null)
    setStatus(null)
    setResults(null)
    setError(null)
    setUploading(false)
    setProcessing(false)
    setCurrentStep('')
    setProgress(0)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
    if (statusIntervalRef.current) {
      clearInterval(statusIntervalRef.current)
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>Presentation Analysis Tool</h1>
        <p>{results ? 'Analysis Complete - Review your results below' : 'Upload a video to analyze your presentation skills'}</p>
      </header>

      <main className={`app-main ${results ? 'results-view' : ''}`}>
        {!results ? (
          <div className="upload-section">
            <div className="file-input-container">
              <input
                ref={fileInputRef}
                type="file"
                accept="video/*"
                onChange={handleFileSelect}
                className="file-input"
                id="video-upload"
              />
              <label htmlFor="video-upload" className="file-input-label">
                {selectedFile ? selectedFile.name : 'Choose Video File'}
              </label>
            </div>

            {selectedFile && (
              <div className="file-info">
                <p><strong>Selected:</strong> {selectedFile.name}</p>
                <p><strong>Size:</strong> {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB</p>
                <p><strong>Type:</strong> {selectedFile.type}</p>
              </div>
            )}

            <div className="button-group">
              {!processingId ? (
                <button
                  onClick={handleUpload}
                  disabled={!selectedFile || uploading}
                  className="upload-button"
                >
                  {uploading ? 'Uploading...' : 'Upload Video'}
                </button>
              ) : status === 'uploaded' ? (
                <button
                  onClick={handleProcess}
                  disabled={processing}
                  className="process-button"
                >
                  {processing ? 'Processing...' : 'Start Analysis'}
                </button>
              ) : status === 'processing' ? (
                <div className="processing-status">
                  <h3>Processing your video...</h3>
                  {currentStep && (
                    <div className="current-step">
                      <p>{currentStep}</p>
                    </div>
                  )}
                  <div className="progress-container">
                    <div className="progress-bar">
                      <div 
                        className="progress-fill" 
                        style={{ width: `${progress}%` }}
                      ></div>
                    </div>
                    <span className="progress-text">{progress}%</span>
                  </div>
                  <div className="spinner"></div>
                </div>
              ) : null}

              <button onClick={handleReset} className="reset-button">
                Reset
              </button>
            </div>

            {error && (
              <div className="error-message">
                <p>{error}</p>
              </div>
            )}
          </div>
        ) : (
          <div className="results-section">
            <h2>Analysis Results</h2>
            
            {results?.results?.report && (
              <div className="report-summary">
                <h3>Overall Score: {results.results.report.overall_score}/10</h3>
                
                <div className="report-section">
                  <h4>Strengths</h4>
                  <ul>
                    {results.results.report.strengths.map((strength, index) => (
                      <li key={index}>{strength}</li>
                    ))}
                  </ul>
                </div>
                
                <div className="report-section">
                  <h4>Areas for Improvement</h4>
                  <ul>
                    {results.results.report.areas_for_improvement.map((area, index) => (
                      <li key={index}>{area}</li>
                    ))}
                  </ul>
                </div>
                
                <div className="report-section">
                  <h4>Recommendations</h4>
                  <ul>
                    {results.results.report.recommendations.map((rec, index) => (
                      <li key={index}>{rec}</li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
            
            <div className="detailed-results">
              <h3>Detailed Analysis</h3>
              <div className="results-content">
                <pre>{JSON.stringify(results, null, 2)}</pre>
              </div>
      </div>
            
            <button onClick={handleReset} className="reset-button">
              Analyze Another Video
        </button>
          </div>
        )}
      </main>
      </div>
  )
}

export default App
