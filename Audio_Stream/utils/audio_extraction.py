import subprocess

input_file = r"/Users/erencimentepe/Desktop/VSCode Projects/Capstone-2T6/Audio_Stream/utils/input_video.MOV"
# Can change this to mp3 or wav they both work
output_file = "output_audio.wav"

# Extract the audio as mp3 using ffmpeg
subprocess.run([
    "ffmpeg",
    "-i", input_file,  # input video
    "-q:a", "0",       # highest audio quality
    "-map", "a",       # select only audio streams
    output_file
], check=True)

print(f"Audio extracted to {output_file}")
