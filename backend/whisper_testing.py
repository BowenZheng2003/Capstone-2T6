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
    audio_file = record_audio(duration=5)
    print(f"📥 Loading Whisper model ({model_size})...")
    model = whisper.load_model(model_size)

    print(f"🎧 Transcribing '{audio_file}'...")
    result = model.transcribe(audio_file)

    print("✅ Transcription complete:")
    print(result["text"])

    result = model.transcribe(audio_file, word_timestamps=True)
    # for segment in result["segments"]:
    #     for word_info in segment["words"]:
    #         print(f"{word_info['word']} ({word_info['start']}s - {word_info['end']}s)")


    return result["text"]

if __name__ == "__main__":
    #audio_file = record_audio(duration=5)
    #audio_file = "C:\Users\Jeslyn\Downloads\Recording (32).m4a"
    transcribe_audio("tmp")
