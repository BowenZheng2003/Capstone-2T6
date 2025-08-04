import os
import sys  
import subprocess

# Check for and import utils with error guards
try:
    from utils.video_preprocessing import standardize_video
    print("[✓] Imported: video_preprocessing")
except Exception as e:
    print("[IMPORT ERROR] video_preprocessing:", e)

try:
    from utils.frame_extraction import extract_frames
    print("[✓] Imported: frame_extraction")
except Exception as e:
    print("[IMPORT ERROR] frame_extraction:", e)

try:
    from utils.landmark_detection import detect_landmarks
    print("[✓] Imported: landmark_detection")
except Exception as e:
    print("[IMPORT ERROR] landmark_detection:", e)

def run_pyfeat_subprocess():
    print("\n[4] Running py-feat facial expression analysis...")
    try:
        result = subprocess.run(
            [sys.executable, "utils/pyfeat_runner.py"],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print("[pyfeat subprocess STDERR]", result.stderr)

        print("[4.1] py-feat subprocess completed.")

        if os.path.exists("output/pyfeat_results.csv"):
            print(">>> py-feat results confirmed at output/pyfeat_results.csv")
        else:
            print(">>> [WARNING] py-feat output not found.")

    except Exception as e:
        print("[ERROR in Step 4]", e)

def main():
    print("\n>>> main.py is running...")

    video_input = "uploads/sample_presentation.mp4"
    print(f">>> Looking for input video: {video_input}")
    print(f">>> File exists? {os.path.exists(video_input)}")

    if not os.path.exists(video_input):
        print("[ERROR] Video file not found.")
        return

    try:
        print("\n[1] Standardizing video...")
        processed_video = standardize_video(video_input)
        print(f"[1.1] Processed video saved: {processed_video}")
    except Exception as e:
        print("[ERROR in Step 1]", e)
        return

    try:
        print("\n[2] Extracting frames from video...")
        frame_dir = extract_frames(processed_video)
        print(f"[2.1] Extracted to directory: {frame_dir}")
    except Exception as e:
        print("[ERROR in Step 2]", e)
        return

    try:
        print("\n[3] Detecting face/pose/hand landmarks...")
        detect_landmarks(frame_dir)
        print("[3.1] Landmarks saved.")
    except Exception as e:
        print("[ERROR in Step 3]", e)
        return

    run_pyfeat_subprocess()

if __name__ == "__main__":
    main()
