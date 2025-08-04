import os
from feat import Detector
import pandas as pd

def run_pyfeat_on_frames(frame_dir="frames", output_csv="output/pyfeat_results.csv"):
    print(">>> Starting py-feat test inside safe shell...")

    image_paths = [
        os.path.join(frame_dir, f)
        for f in sorted(os.listdir(frame_dir))
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

    print(f">>> Found {len(image_paths)} images")

    if not image_paths:
        print(">>> No valid images found. Exiting.")
        return

    try:
        detector = Detector(device="cpu")  # simplified init
        print(">>> Detector initialized.")

        results = detector.detect(image_paths)

        if results is None or results.empty:
            print(">>> [ERROR] py-feat detection returned empty results.")
            return

        os.makedirs(os.path.dirname(output_csv), exist_ok=True)
        results.to_csv(output_csv, index=False)
        print(f">>> py-feat results saved to: {output_csv}")

    except Exception as e:
        print(f">>> [EXCEPTION] py-feat failed: {e}")

if __name__ == "__main__":
    run_pyfeat_on_frames()
