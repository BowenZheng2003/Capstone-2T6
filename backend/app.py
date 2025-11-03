# in your FastAPI code (e.g. main.py)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import FastAPI, File, UploadFile, BackgroundTasks

from backend.whisper_testing import transcribe_audio
from backend.final_report_generation.end_to_end_pipeline import generate_full_report
import os
import uuid
import shutil


UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI()

origins = [
    "http://localhost:3001",                        # for local React dev
    #"https://capstone-backend-test.onrender.com", # if you deploy frontend to Render
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
async def ping() -> str:
    return "You're all I can think of. Every drop I drink up. You're my soda pop. My little soda pop (Yeah, yeah). Cool me down, you're so hot. Pour me up, I won't stop (Oh, oh). You're my soda pop. My little soda pop"

@app.get("/echo/{text}")
async def echo(text: str) -> JSONResponse:
    return JSONResponse({"echo": text})

@app.get("/transcribe_macbeth")
async def transcribe() -> str:
    transcription = transcribe_audio("MacBeth_Voiceover.mp3")
    return transcription

# @app.post("/upload")
# async def upload_file(file: UploadFile = File(...)):
#     contents = await file.read()
#     # Process the file here
#     return {"filename": file.filename, "size": len(contents)}

@app.post("/process_video")
async def process_video(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    """
    Upload a video, save it temporarily, and run the end_to_end_pipeline.
    """

    return {"message": "Processing complete.", "report": "MOCK RESPONSE"}  # Remove this line when enabling the function below
    # try:
    #     # Save uploaded file to disk
    #     file_ext = os.path.splitext(file.filename)[1]
    #     unique_name = f"{uuid.uuid4().hex}{file_ext}"
    #     temp_path = os.path.join(UPLOAD_DIR, unique_name)

    #     with open(temp_path, "wb") as buffer:
    #         shutil.copyfileobj(file.file, buffer)

    #     # Option 1 — Run synchronously and return the result
    #     report = "MOCK REPORT HERE" #generate_full_report(temp_path)

    #     # Option 2 — If pipeline is heavy, use background task:
    #     # background_tasks.add_task(end_to_end_pipeline, temp_path)
    #     # return {"message": "Video upload received. Processing in background."}

    #     return {"message": "Processing complete.", "report": report}

    # except Exception as e:
    #     return JSONResponse(status_code=500, content={"error": str(e)})
