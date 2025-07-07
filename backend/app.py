# in your FastAPI code (e.g. main.py)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from whisper_testing import transcribe_audio

app = FastAPI()

origins = [
    "http://localhost:3000",                        # for local React dev
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

@app.get("/echo/{text}")
async def echo(text: str) -> JSONResponse:
    return JSONResponse({"echo": text})

@app.get("/transcribe_macbeth")
async def transcribe() -> str:
    transcription = transcribe_audio("MacBeth_Voiceover.mp3")
    return transcription
