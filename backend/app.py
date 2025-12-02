# app.py
from fastapi import FastAPI, File, UploadFile, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os, uuid, shutil, tempfile, traceback, sys

from backend.whisper_testing import transcribe_audio
from backend.final_report_generation.end_to_end_pipeline import generate_full_report

# ---------- CORS ----------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # CRA dev
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Simple test endpoints (JSON) ----------
@app.get("/")
async def root():
    return {"ok": True, "service": "backend alive"}

@app.get("/ping")
async def ping():
    return {"pong": True}

@app.get("/echo/{text}")
async def echo(text: str):
    return {"echo": text}

@app.get("/transcribe_macbeth")
async def transcribe():
    return {"transcript": transcribe_audio("MacBeth_Voiceover.mp3")}

# ---------- Video processing ----------
@app.post("/process_video")
async def process_video(
    # accept either field name the frontend might use
    background_tasks: BackgroundTasks,
    video: UploadFile | None = File(default=None),
    file: UploadFile | None = File(default=None),
):
    """
    Upload a video, save it temporarily, run the end-to-end pipeline, return the report.
    Accepts `video` or `file` as the multipart field name.
    """
    try:
        upload = video or file
        if upload is None:
            raise HTTPException(status_code=400, detail="No file provided. Use form field 'file' or 'video'.")

        # Persist to a secure temp file
        ext = os.path.splitext(upload.filename or "")[1] or ".bin"
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            shutil.copyfileobj(upload.file, tmp)
            temp_path = tmp.name

        # Make sure the temp file is removed after processing
        
        background_tasks.add_task(_safe_unlink, temp_path)

        # Run your pipeline (this is where FFmpeg + Whisper already worked for you)
        report = generate_full_report(temp_path)

        return {"message": "Processing complete.", "report": report}

    except HTTPException:
        raise
    except Exception as e:
        # Print full traceback to server logs AND expose message to client to debug quickly
        traceback.print_exc(file=sys.stderr)
        return JSONResponse(status_code=500, content={"error": str(e)})

def _safe_unlink(path: str) -> None:
    try:
        if path and os.path.exists(path):
            os.unlink(path)
    except Exception:
        pass
