#!/usr/bin/env python3
import os, sys, argparse, json, subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
UTILS = HERE / "utils"
sys.path.insert(0, str(UTILS))

# Local utils
from video_preprocessing import standardize_video
from frame_extraction import extract_frames

# Landmarks optional
try:
    from landmark_detection import detect_landmarks
    HAVE_LANDMARKS = True
except Exception:
    HAVE_LANDMARKS = False


def main():
    ap = argparse.ArgumentParser(
        description="End-to-end: video → frames → Py-Feat CSV → slim JSON"
    )

    # Inputs / outputs
    ap.add_argument("--video", required=True, help="Path to input video")
    ap.add_argument("--workdir", default=".", help="Working directory")
    ap.add_argument("--overwrite", action="store_true", help="Overwrite existing outputs")
    ap.add_argument("--verbose", action="store_true", help="Verbose logs")

    # Standardize video
    ap.add_argument("--std_fps", type=int, default=25)
    ap.add_argument("--width", type=int, default=640)
    ap.add_argument("--height", type=int, default=480)

    # Frames
    ap.add_argument("--frame_every_ms", type=int, default=1000, help="Save one frame every N ms")
    ap.add_argument("--frames_dir", default="frames", help="Frames subdir")

    # Landmarks (optional)
    ap.add_argument("--run_landmarks", action="store_true", help="Run MediaPipe Holistic")
    ap.add_argument("--landmarks_dir", default="landmarks", help="Landmarks subdir")

    # Py-Feat
    ap.add_argument("--pyfeat_csv", default="output/pyfeat_results.csv", help="Py-Feat CSV path")

    # AU flags → JSON
    ap.add_argument("--out_json", default="output_flags.json", help="Final JSON path")
    ap.add_argument("--include_frames", action="store_true", help="Include per-frame JSON (bigger)")

    # Segmenting & sparsification
    ap.add_argument("--fps_for_segments", type=float, default=1.0,
                    help="Rows→seconds when no timestamp; use 1.0 if 1 frame/sec.")
    ap.add_argument("--win_sec", type=float, default=5.0)
    ap.add_argument("--hop_sec", type=float, default=2.0)
    ap.add_argument("--emo_min", type=float, default=0.35)
    ap.add_argument("--emo_margin", type=float, default=0.15)
    ap.add_argument("--cluster_min_rate", type=float, default=0.40)

    args = ap.parse_args()

    workdir = Path(args.workdir).resolve()
    workdir.mkdir(parents=True, exist_ok=True)

    video_in = Path(args.video).resolve()
    if not video_in.exists():
        print(f"[error] Video not found: {video_in}", flush=True)
        return 2

    processed_video = workdir / "processed_video.mp4"
    frames_dir = workdir / args.frames_dir
    landmarks_dir = workdir / args.landmarks_dir
    pyfeat_csv = workdir / args.pyfeat_csv
    out_json = workdir / args.out_json
    au_flags_py = HERE / "utils" / "au_flags.py"

    # 1) Standardize video
    if processed_video.exists() and not args.overwrite:
        print(f"[skip] Standardized video exists: {processed_video}", flush=True)
    else:
        print("[1/5] Standardizing video…", flush=True)
        standardize_video(str(video_in), str(processed_video),
                          fps=args.std_fps, resolution=(args.width, args.height))
        print(f"[ok] Saved: {processed_video}", flush=True)

    # 2) Extract frames (clear old if overwriting)
    if frames_dir.exists() and any(frames_dir.glob("*.jpg")) and not args.overwrite:
        count = len(list(frames_dir.glob("*.jpg")))
        print(f"[skip] Frames already present: {frames_dir} ({count} jpgs)", flush=True)
    else:
        print("[2/5] Extracting frames…", flush=True)
        frames_dir.mkdir(parents=True, exist_ok=True)
        if args.overwrite:
            for p in frames_dir.glob("*.jpg"):
                try: p.unlink()
                except Exception: pass
        extract_frames(str(processed_video), str(frames_dir),
                       frame_interval_ms=args.frame_every_ms,
                       resize_dim=(args.width, args.height))

    # 3) Landmarks (optional; clear old if overwriting)
    if args.run_landmarks:
        if not HAVE_LANDMARKS:
            print("[warn] landmark_detection unavailable; skipping.", flush=True)
        else:
            print("[3/5] Running landmarks…", flush=True)
            landmarks_dir.mkdir(parents=True, exist_ok=True)
            if args.overwrite:
                for p in landmarks_dir.glob("*.json"):
                    try: p.unlink()
                    except Exception: pass
            detect_landmarks(str(frames_dir), output_json_dir=str(landmarks_dir))

    # 4) Py-Feat → CSV (subprocess; avoids Windows handle issues)
    if pyfeat_csv.exists() and not args.overwrite:
        print(f"[skip] Py-Feat CSV exists: {pyfeat_csv}", flush=True)
    else:
        print("[4/5] Running Py-Feat on frames…", flush=True)
        pyfeat_csv.parent.mkdir(parents=True, exist_ok=True)
        runner = HERE / "utils" / "pyfeat_runner.py"
        cmd = [
            sys.executable, str(runner),
            "--frame_dir", str(frames_dir),
            "--output_csv", str(pyfeat_csv),
        ]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in proc.stdout:
            print(line, end="", flush=True)
        proc.wait()
        if proc.returncode != 0 or not pyfeat_csv.exists():
            print("[error] Py-Feat did not produce the CSV.", flush=True)
            return 3

    # 5) AU flags → slim JSON (force frame-based time)
    print("[5/5] Building slim JSON segments…", flush=True)
    cmd = [
        sys.executable, str(au_flags_py),
        "--in_csv", str(pyfeat_csv),
        "--out_json", str(out_json),
        "--fps", str(args.fps_for_segments),
        "--win_sec", str(args.win_sec),
        "--hop_sec", str(args.hop_sec),
        "--emo_min", str(args.emo_min),
        "--emo_margin", str(args.emo_margin),
        "--cluster_min_rate", str(args.cluster_min_rate),
        "--prefer_frame_time",
    ]
    if args.include_frames:
        cmd.append("--include_frames")
    if args.verbose:
        cmd.append("--verbose")

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in proc.stdout:
        print(line, end="", flush=True)
    proc.wait()
    if proc.returncode != 0:
        print("[error] au_flags.py failed.", flush=True)
        return 4

    print("\n=== DONE ===", flush=True)
    print(f"Video     : {video_in}", flush=True)
    print(f"Frames    : {frames_dir}", flush=True)
    print(f"Py-Feat   : {pyfeat_csv}", flush=True)
    print(f"JSON      : {out_json}", flush=True)
    print(json.dumps({"json_path": str(out_json)}, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
