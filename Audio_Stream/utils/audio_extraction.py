import subprocess

input_file = r"C:\Users\Jeslyn\OneDrive\Desktop\capstone\Capstone-2T6\IMG_4027.MOV"
output_file = "output_audio.mp3"

# Extract the audio as mp3 using ffmpeg
subprocess.run([
    "ffmpeg",
    "-i", input_file,  # input video
    "-q:a", "0",       # highest audio quality
    "-map", "a",       # select only audio streams
    output_file
], check=True)

print(f"Audio extracted to {output_file}")
