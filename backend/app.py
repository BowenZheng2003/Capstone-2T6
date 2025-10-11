# in your FastAPI code (e.g. main.py)
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import tempfile
import asyncio
from pathlib import Path

from whisper_functions import transcribe_audio
from final_report_generation.end_to_end_pipeline import process_video_file

app = FastAPI()

origins = [
    "http://localhost:3000",                        # for local React dev
    "http://localhost:5173",                        # for Vite dev server
    "https://capstone-backend-test.onrender.com", # if you deploy frontend to Render
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Store processing status
processing_status = {}

@app.get("/")
async def root():
    return JSONResponse({"message": "Presentation Analysis API is running!"})

@app.get("/ping")
async def ping() -> str:
    return "pong"

@app.get("/echo/{text}")
async def echo(text: str) -> JSONResponse:
    return JSONResponse({"echo": text})

@app.get("/transcribe_macbeth")
async def transcribe() -> str:
    transcription = transcribe_audio("MacBeth_Voiceover.mp3")
    return transcription

@app.post("/upload-video")
async def upload_video(file: UploadFile = File(...)):
    """
    Upload a video file and process it through the complete analysis pipeline.
    """
    if not file.content_type.startswith('video/'):
        raise HTTPException(status_code=400, detail="File must be a video")
    
    # Create a unique processing ID
    import uuid
    processing_id = str(uuid.uuid4())
    
    # Save uploaded file temporarily
    temp_dir = Path(tempfile.mkdtemp())
    video_path = temp_dir / f"{processing_id}_{file.filename}"
    
    try:
        # Save the uploaded file
        with open(video_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Initialize processing status
        processing_status[processing_id] = {
            "status": "uploaded",
            "filename": file.filename,
            "video_path": str(video_path),
            "progress": 0
        }
        
        return JSONResponse({
            "message": "Video uploaded successfully",
            "processing_id": processing_id,
            "filename": file.filename
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload video: {str(e)}")

@app.post("/process-video/{processing_id}")
async def process_video(processing_id: str):
    """
    Process the uploaded video through the complete analysis pipeline.
    """
    if processing_id not in processing_status:
        raise HTTPException(status_code=404, detail="Processing ID not found")
    
    status = processing_status[processing_id]
    if status["status"] != "uploaded":
        raise HTTPException(status_code=400, detail="Video not ready for processing")
    
    try:
        # Update status to processing
        processing_status[processing_id]["status"] = "processing"
        processing_status[processing_id]["progress"] = 10
        
        # Run the pipeline in a background task
        asyncio.create_task(run_pipeline_async(processing_id))
        
        return JSONResponse({
            "message": "Processing started",
            "processing_id": processing_id
        })
        
    except Exception as e:
        processing_status[processing_id]["status"] = "failed"
        processing_status[processing_id]["error"] = str(e)
        raise HTTPException(status_code=500, detail=f"Failed to start processing: {str(e)}")

async def run_pipeline_async(processing_id: str):
    """
    Run the analysis pipeline asynchronously.
    """
    try:
        status = processing_status[processing_id]
        video_path = status["video_path"]
        
        # Update progress
        processing_status[processing_id]["progress"] = 20
        
        # Run the pipeline
        results = process_video_file(video_path)
        
        # Update status with results
        processing_status[processing_id].update({
            "status": results["status"],
            "progress": 100,
            "results": results,
            "completed_at": str(Path().cwd())  # Simple timestamp placeholder
        })
        
    except Exception as e:
        processing_status[processing_id].update({
            "status": "failed",
            "error": str(e),
            "progress": 0
        })

@app.get("/status/{processing_id}")
async def get_processing_status(processing_id: str):
    """
    Get the current processing status for a video.
    """
    if processing_id not in processing_status:
        raise HTTPException(status_code=404, detail="Processing ID not found")
    
    return JSONResponse(processing_status[processing_id])

@app.get("/results/{processing_id}")
async def get_results(processing_id: str):
    """
    Get the analysis results for a processed video.
    """
    if processing_id not in processing_status:
        raise HTTPException(status_code=404, detail="Processing ID not found")
    
    status = processing_status[processing_id]
    if status["status"] not in ["completed", "partial"]:
        raise HTTPException(status_code=400, detail="Processing not complete")
    
    if "results" not in status:
        raise HTTPException(status_code=404, detail="Results not available")
    
    return JSONResponse(status["results"])
