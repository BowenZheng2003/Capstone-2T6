# in your FastAPI code (e.g. main.py)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
<<<<<<< HEAD
=======
from fastapi import FastAPI, File, UploadFile
>>>>>>> origin

from whisper_testing import transcribe_audio

app = FastAPI()

origins = [
    "http://localhost:3000",                        # for local React dev
<<<<<<< HEAD
    "https://capstone-backend-test.onrender.com", # if you deploy frontend to Render
=======
    #"https://capstone-backend-test.onrender.com", # if you deploy frontend to Render
>>>>>>> origin
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
<<<<<<< HEAD
    return JSONResponse({"message": "Hello, World from FastAPI on Render!"})
=======
    return JSONResponse({"message": "Hi Divas!"})
>>>>>>> origin

@app.get("/ping")
async def ping() -> str:
    return "pong"

<<<<<<< HEAD
=======
@app.get("/sodapop")
async def ping() -> str:
    return "You're all I can think of. Every drop I drink up. You're my soda pop. My little soda pop (Yeah, yeah). Cool me down, you're so hot. Pour me up, I won't stop (Oh, oh). You're my soda pop. My little soda pop"

>>>>>>> origin
@app.get("/echo/{text}")
async def echo(text: str) -> JSONResponse:
    return JSONResponse({"echo": text})

@app.get("/transcribe_macbeth")
async def transcribe() -> str:
    transcription = transcribe_audio("MacBeth_Voiceover.mp3")
    return transcription
<<<<<<< HEAD
=======

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    # Process the file here
    return {"filename": file.filename, "size": len(contents)}
>>>>>>> origin
