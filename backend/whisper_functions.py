import whisper
import sounddevice as sd
from scipy.io.wavfile import write
import json
import math

def record_audio(filename="recorded.wav", duration=5, samplerate=44100):
    print(f"🎤 Recording for {duration} seconds...")
    recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1)
    sd.wait()
    write(filename, samplerate, recording)
    print(f"💾 Audio saved to {filename}")
    return filename

def transcribe_audio(file_path, model_size="base", output_json="transcript.json"): #sentence by sentence in timestamps
    print(f"📥 Loading Whisper model ({model_size})...")
    model = whisper.load_model(model_size)

    print(f"🎧 Transcribing '{file_path}'...")
    result = model.transcribe(file_path)

    # Convert segments to your JSON format
    transcript_data = []
    for seg in result["segments"]:
        start = seg["start"]
        end = seg["end"]
        text = seg["text"].strip()

        entry = {
            "timestamp": f"{start:.2f} - {end:.2f}",
            "transcription": text
        }
        transcript_data.append(entry)

    # Save JSON file
    with open(output_json, "w") as f:
        json.dump(transcript_data, f, indent=2)

    print(f"✅ Transcription saved to {output_json}")
    return transcript_data

def transcribe_audio_chunks(file_path, model_size="base", chunk_seconds=30, overlap_seconds=2.5, output_json="transcript.json"):
    import math, json, whisper

    print(f"📥 Loading Whisper model ({model_size})...")
    model = whisper.load_model(model_size)

    print(f"🎧 Transcribing '{file_path}'...")
    result = model.transcribe(file_path)

    total_duration = math.ceil(result["segments"][-1]["end"]) if result["segments"] else 0

    # Calculate the step between chunks (chunk_seconds minus overlap)
    step = chunk_seconds - overlap_seconds
    num_chunks = math.ceil((total_duration - overlap_seconds) / step)

    # Prepare empty chunks
    chunks = []
    for i in range(num_chunks):
        start = i * step
        end = min(start + chunk_seconds, total_duration)
        chunks.append({"start": start, "end": end, "text": ""})

    # Assign each segment text to the correct chunks
    for seg in result["segments"]:
        seg_start = seg["start"]
        seg_end = seg["end"]
        text = seg["text"].strip()

        for chunk in chunks:
            # Check if the segment overlaps with the chunk
            if seg_end > chunk["start"] and seg_start < chunk["end"]:
                chunk["text"] += (" " + text).strip()

    # Format final JSON
    transcript_data = []
    for c in chunks:
        start_min = int(c["start"] // 60)
        start_sec = int(c["start"] % 60)
        end_min = int(c["end"] // 60)
        end_sec = int(c["end"] % 60)
        timestamp = f"{start_min:02d}:{start_sec:02d} - {end_min:02d}:{end_sec:02d}"
        transcript_data.append({
            "timestamp": timestamp,
            "transcription": c["text"]
        })

    # Save JSON
    with open(output_json, "w") as f:
        json.dump(transcript_data, f, indent=2)

    print(f"✅ Transcription saved to {output_json}")
    return output_json


if __name__ == "__main__":
    #audio_file = record_audio(duration=5)
    audio_file = r"C:\Users\Jeslyn\OneDrive\Desktop\capstone\Capstone-2T6\backend\MacBeth_Voiceover.mp3"
    transcribe_audio_chunks(file_path=audio_file, chunk_seconds=5)
