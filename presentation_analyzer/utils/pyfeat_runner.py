# presentation_analyzer/utils/pyfeat_runner.py
import os
import sys
import argparse
import inspect
from typing import List
import pandas as pd
import cv2

def _list_images(frame_dir: str) -> List[str]:
    return [
        os.path.join(frame_dir, f)
        for f in sorted(os.listdir(frame_dir))
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

def _load_rgb(img_path: str):
    # Robust OpenCV load → RGB numpy array
    img_bgr = cv2.imread(img_path, cv2.IMREAD_COLOR)
    if img_bgr is None:
        raise RuntimeError(f"cv2.imread() returned None for {img_path}")
    return cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

def _make_detector():
    """Create a Detector instance compatible with the installed py-feat version."""
    from feat import Detector

    # Be conservative with threads on Windows
    try:
        import torch
        torch.set_num_threads(1)
        torch.set_num_interop_threads(1)
    except Exception:
        pass

    # Introspect signature to avoid unsupported kwargs
    sig = inspect.signature(Detector.__init__)
    allowed = set(sig.parameters.keys())

    # Try a few safe variants, from most explicit to simplest
    candidates = []
    if "device" in allowed:
        candidates.append({"device": "cpu"})
    candidates.append({})  # bare init

    last_err = None
    for kw in candidates:
        try:
            det = Detector(**kw)
            print(f">>> Detector initialized with kwargs={kw}.")
            return det
        except Exception as e:
            last_err = e
            print(f">>> Detector init failed with kwargs={kw}: {e}")

    raise RuntimeError(f"Detector init failed; last error: {last_err}")

def run_pyfeat_on_frames(frame_dir="frames", output_csv="output/pyfeat_results.csv"):
    abs_frames = os.path.abspath(frame_dir)
    print(">>> Py-Feat runner starting…")
    print(f">>> Frame dir: {abs_frames}")

    image_paths = _list_images(frame_dir)
    print(f">>> Found {len(image_paths)} images")
    if not image_paths:
        print(">>> No valid images found. Exiting.")
        return

    try:
        from feat import Detector  # noqa: F401 (import to ensure module present)
    except Exception as e:
        print(f">>> [EXCEPTION] Could not import py-feat: {e}")
        return

    try:
        detector = _make_detector()
    except Exception as e:
        print(f">>> [EXCEPTION] Detector init failed: {e}")
        return

    detect_img = getattr(detector, "detect_image", None)
    dfs = []

    for i, img_path in enumerate(image_paths, 1):
        try:
            if callable(detect_img):
                rgb = _load_rgb(img_path)
                df = detect_img(rgb)
            else:
                df = detector.detect(img_path)

            if df is None or df.empty:
                print(f"[warn] Empty result for {img_path}")
                continue

            df["image_path"] = os.path.abspath(img_path)
            dfs.append(df)

            if i % 10 == 0 or i == len(image_paths):
                print(f"    ... processed {i}/{len(image_paths)}")
        except Exception as e:
            print(f"[warn] detect failed on {img_path}: {e}")

    if not dfs:
        print(">>> [ERROR] No successful detections; not writing CSV.")
        return

    results = pd.concat(dfs, ignore_index=True)
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    results.to_csv(output_csv, index=False)
    print(f">>> py-feat results saved to: {os.path.abspath(output_csv)}")
    return output_csv

def get_csv(frame_dir: str = "frames", output_csv: str = "output/pyfeat_results.csv"):
    # ap = argparse.ArgumentParser()
    # ap.add_argument("--frame_dir", default="frames")
    # ap.add_argument("--output_csv", default="output/pyfeat_results.csv")
    # args = ap.parse_args()
    run_pyfeat_on_frames(frame_dir, output_csv)

# if __name__ == "__main__":
#     main()
