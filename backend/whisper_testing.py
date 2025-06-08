import whisper
import sounddevice as sd
from scipy.io.wavfile import write

def record_audio(filename="recorded.wav", duration=5, samplerate=44100):
    print(f"🎤 Recording for {duration} seconds...")
    recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1)
    sd.wait()
    write(filename, samplerate, recording)
    print(f"💾 Audio saved to {filename}")
    return filename

def transcribe_audio(file_path, model_size="base"):
    print(f"📥 Loading Whisper model ({model_size})...")
    model = whisper.load_model(model_size)

    print(f"🎧 Transcribing '{file_path}'...")
    result = model.transcribe(file_path)

    print("✅ Transcription complete:")
    print(result["text"])
    return result["text"]

if __name__ == "__main__":
    audio_file = record_audio(duration=5)
    # audio_file = "MacBeth_Voiceover.mp3"
    transcribe_audio(audio_file)
