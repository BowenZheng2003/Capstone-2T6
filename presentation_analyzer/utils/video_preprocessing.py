import ffmpeg
import os

def standardize_video(input_path, output_path="processed_video.mp4", fps=25, resolution=(640, 480)):
    print(">>> [FFmpeg] Standardizing video...")
    try:
        (
            ffmpeg
            .input(input_path)
            .filter('fps', fps=fps)
            .filter('scale', resolution[0], resolution[1])
            .output(output_path, vcodec='libx264', acodec='aac')
            .run(overwrite_output=True)
        )
    except ffmpeg.Error as e:
        print("[FFmpeg ERROR]", e.stderr.decode())
        raise e
    return output_path
