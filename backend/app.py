# in your FastAPI code (e.g. main.py)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi import FastAPI, File, Form, UploadFile, BackgroundTasks

from backend.whisper_testing import transcribe_audio
from backend.final_report_generation.end_to_end_pipeline import generate_full_report
import os
import uuid
import shutil
import asyncio
import threading
import json


UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return JSONResponse({"message": "Hi Divas!"})

@app.get("/ping")
async def ping() -> str:
    return "pong"

@app.get("/sodapop")
async def sodapop() -> str:
    return "You're all I can think of. Every drop I drink up. You're my soda pop. My little soda pop (Yeah, yeah). Cool me down, you're so hot. Pour me up, I won't stop (Oh, oh). You're my soda pop. My little soda pop"

@app.get("/echo/{text}")
async def echo(text: str) -> JSONResponse:
    return JSONResponse({"echo": text})

@app.get("/transcribe_macbeth")
async def transcribe() -> str:
    transcription = transcribe_audio("MacBeth_Voiceover.mp3")
    return transcription

@app.post("/process_video")
async def process_video(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    """
    Upload a video, save it temporarily, and run the end_to_end_pipeline.
    """
    try:
        file_ext = os.path.splitext(file.filename)[1]
        unique_name = f"{uuid.uuid4().hex}{file_ext}"
        temp_path = os.path.join(UPLOAD_DIR, unique_name)

        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        report = generate_full_report(temp_path)
        return {"message": "Processing complete.", "report": report}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/process_video_stream")
async def process_video_stream(file: UploadFile = File(...), context: str = Form("General presentation")):
    """
    Upload a video and stream real-time progress via Server-Sent Events.
    Each event is a JSON object: {step, progress, message}
    Final event: {step: "done", progress: 100, report: {...}}
    Error event: {step: "error", error: "..."}
    """
    file_ext = os.path.splitext(file.filename)[1]
    unique_name = f"{uuid.uuid4().hex}{file_ext}"
    temp_path = os.path.join(UPLOAD_DIR, unique_name)

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    queue = asyncio.Queue()
    loop = asyncio.get_running_loop()

    def on_progress(data: dict):
        asyncio.run_coroutine_threadsafe(queue.put(data), loop)

    def run_pipeline():
        try:
            report = generate_full_report(temp_path, on_progress=on_progress, context=context)
            asyncio.run_coroutine_threadsafe(
                queue.put({"step": "done", "progress": 100, "message": "Complete!", "report": report}),
                loop,
            )
        except Exception as e:
            asyncio.run_coroutine_threadsafe(
                queue.put({"step": "error", "error": str(e)}),
                loop,
            )

    thread = threading.Thread(target=run_pipeline, daemon=True)
    thread.start()

    async def event_generator():
        while True:
            data = await queue.get()
            yield f"data: {json.dumps(data)}\n\n"
            if data.get("step") in ("done", "error"):
                break

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
