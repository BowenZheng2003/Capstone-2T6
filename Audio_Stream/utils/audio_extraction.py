import subprocess

def extract_mp3(input_file: str, output_file: str = "output_audio.wav"):
    # Extract the audio as mp3 using ffmpeg
    subprocess.run([
        "ffmpeg",
        "-i", input_file,  # input video
        "-q:a", "0",       # highest audio quality
        "-map", "a",       # select only audio streams
        output_file
    ], check=True)

    print(f"Audio extracted to {output_file}")

    return output_file

