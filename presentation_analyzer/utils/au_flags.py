#!/usr/bin/env python3
"""
Compute 4 AU cluster flags per frame from a Py-Feat AU CSV and output JSON.

Outputs:
- Slim segment summaries for LLM (dominant emotions + active clusters)
- Optional per-frame blob if --include_frames is passed
"""

import argparse, json, math
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd
from pathlib import Path
import subprocess
import tempfile
import os

DEFAULTS = {
    "thr_hi": 1.5,
    "thr_lo": 0.3,
    "fps": 1.0,
    "win_sec": 5.0,
    "hop_sec": 2.0,
    "emo_min": 0.35,
    "emo_margin": 0.15,
    "cluster_min_rate": 0.40,
}

# ---------- Time base ----------
def resolve_time_series(
    df: pd.DataFrame,
    fps_fallback: float = 1.0,
    prefer_frame_time: bool = False,
    min_span_sec: float = 1e-3,
) -> pd.Series:
    """
    Return per-row seconds.

    If prefer_frame_time=True, ignore any CSV columns and just use the row index
    (0..N-1) / fps_fallback. This is robust even if the CSV has a non-numeric
    'frame' column like 'frame_0003.jpg'.
    """
    # 1) Force row-index-based time if requested
    if prefer_frame_time:
        idx = pd.RangeIndex(len(df))
        return pd.Series(idx, index=df.index, dtype=float) / float(max(fps_fallback, 1e-9))

    # 2) Try timestamp-like columns only if they have span
    for tcol in ["timestamp", "time", "Timestamp", "Time"]:
        if tcol in df.columns:
            raw = pd.to_numeric(df[tcol], errors="coerce")
            if raw.notna().any():
                s = raw.fillna(method="ffill").fillna(0.0).astype(float)
                if float(s.max() - s.min()) >= min_span_sec:
                    return s

    # 3) Try a numeric frame column / fps
    for fcol in ["frame", "Frame"]:
        if fcol in df.columns:
            frames = pd.to_numeric(df[fcol], errors="coerce")
            if frames.notna().any():
                frames = frames.fillna(method="ffill").fillna(0.0)
                return frames.astype(float) / float(max(fps_fallback, 1e-9))

    # 4) Fallback to row index / fps
    idx = pd.RangeIndex(len(df))
    return pd.Series(idx, index=df.index, dtype=float) / float(max(fps_fallback, 1e-9))


def make_overlapping_segments(times: pd.Series, win_sec: float = 5.0, hop_sec: float = 2.0):
    end_time = float(times.max()) if len(times) else 0.0
    # Always produce at least one window
    t0 = 0.0
    if end_time <= 0.0:
        mask = (times >= 0.0) & (times < win_sec)
        yield (0.0, win_sec, mask)
        return
    while t0 <= end_time:
        t1 = t0 + win_sec
        mask = (times >= t0) & (times < t1)
        yield (t0, t1, mask)
        t0 += hop_sec


def fmt_range(a: float, b: float) -> str:
    s0, s1 = int(round(a)), int(round(b))
    m0, r0 = divmod(s0, 60)
    m1, r1 = divmod(s1, 60)
    return f"{m0}:{r0:02d}-{m1}:{r1:02d}"

# ---------- Clusters/emotions ----------
BASE_CLUSTERS = {
    "authentic_smile":   {"aus": ["AU6", "AU12"],          "rule": "min_and"},
    "eyebrow_engagement":{"aus": ["AU1", "AU2", "AU5"],    "rule": "avg_and_majority"},
    "focused_thinking":  {"aus": ["AU4", "AU7"],           "rule": "min_and"},
    "tension":           {"aus": ["AU14", "AU15", "AU17"], "rule": "avg_and_majority"},
}
EMOTION_COLS = ["anger","disgust","fear","happiness","sadness","surprise","neutral"]

def canonical_au_variants(base_au: str) -> List[Tuple[str,str]]:
    num = base_au.replace("AU", "")
    try: n = int(num)
    except ValueError: n = num
    z = f"{int(n):02d}" if isinstance(n, int) else str(n)
    return [
        (f"AU{z}_r","intensity"), (f"AU{z}_c","presence"), (f"AU{z}","intensity"),
        (f"AU{n}_r","intensity"), (f"AU{n}_c","presence"), (f"AU{n}","intensity"),
    ]

def locate_column(df: pd.DataFrame, base_au: str) -> Optional[Tuple[str,str]]:
    for col, kind in canonical_au_variants(base_au):
        if col in df.columns:
            return col, kind
    return None

def to_intensity(df: pd.DataFrame, base_au: str) -> Optional[pd.Series]:
    for col, kind in canonical_au_variants(base_au):
        if col in df.columns and kind == "intensity":
            return pd.to_numeric(df[col], errors="coerce")
    for col, kind in canonical_au_variants(base_au):
        if col in df.columns and kind == "presence":
            return pd.to_numeric(df[col], errors="coerce").fillna(0.0).clip(lower=0.0, upper=1.0)
    return None

def auto_threshold(df_intensities: pd.DataFrame, thr_hi: float, thr_lo: float) -> float:
    if df_intensities.empty: return thr_hi
    try: s = df_intensities.stack(future_stack=True)
    except TypeError: s = df_intensities.stack(dropna=True)
    q95 = s.quantile(0.95)
    if pd.isna(q95): return thr_hi
    return thr_hi if q95 > 1.0 else thr_lo

def compute_cluster_flag(row_vals: List[float], rule: str, thr: float) -> bool:
    vals = [0.0 if (isinstance(v, float) and math.isnan(v)) else float(v) for v in row_vals]
    if not vals: return False
    if rule == "min_and": return min(vals) >= thr
    if rule == "avg_and_majority":
        avg_ok = sum(vals)/len(vals) >= thr
        count_ok = sum(v >= thr for v in vals) >= math.ceil(len(vals)/2)
        return avg_ok and count_ok
    if rule == "any_max": return max(vals) >= thr
    return False

# ---------- Segment sparsification ----------
def sparsify_emotions(emo_means: Dict[str, Optional[float]], p_min: float, margin: float) -> Dict[str, float]:
    vals = {k: float(v) for k, v in emo_means.items() if v is not None}
    if not vals: return {}
    max_p = max(vals.values())
    kept = {k: round(v, 2) for k, v in vals.items() if (v >= p_min and (max_p - v) <= margin)}
    if not kept and max_p >= 0.2:
        top1_k = max(vals, key=lambda x: vals[x])
        kept = {top1_k: round(vals[top1_k], 2)}
    return kept

def sparsify_clusters(cluster_rates: Dict[str, float], min_rate: float) -> Dict[str, float]:
    return {k: round(float(v), 2) for k, v in cluster_rates.items() if v is not None and float(v) >= min_rate}

# ---------- Main ----------
def extract_video_features_to_json(in_csv: str, out_json: str, thr_hi: float, thr_lo: float,
         verbose: bool, print_cols: bool, dump_stats: bool, sample_n: int,
         fps: float, win_sec: float, hop_sec: float,
         emo_min: float, emo_margin: float, cluster_min_rate: float,
         prefer_frame_time: bool, include_frames: bool):

    if verbose: print(f"[info] Loading CSV: {in_csv}")
    df = pd.read_csv(in_csv)

    if print_cols:
        print("[info] CSV columns:")
        for c in df.columns: print("  -", c)

    clusters = dict(BASE_CLUSTERS)
    needed_aus = sorted({au for spec in clusters.values() for au in spec["aus"]})
    au_series: Dict[str, pd.Series] = {}
    au_resolved_cols: Dict[str, str] = {}
    au_kinds: Dict[str, str] = {}

    for au in needed_aus:
        loc = locate_column(df, au)
        if loc is None:
            au_series[au] = pd.Series([0.0]*len(df), index=df.index, dtype=float)
            au_resolved_cols[au] = "<missing>"; au_kinds[au] = "none"
        else:
            col, kind = loc
            s = to_intensity(df, au)
            if s is None:
                s = pd.Series([0.0]*len(df), index=df.index, dtype=float)
            au_series[au] = s; au_resolved_cols[au] = col; au_kinds[au] = kind

    if verbose:
        print("[info] AU column resolution (base -> used column [type]):")
        for au in needed_aus:
            print(f"{au:>4} -> {au_resolved_cols[au]} [{au_kinds[au]}]")

    aus_df = pd.DataFrame(au_series)
    thr = auto_threshold(aus_df, thr_hi=thr_hi, thr_lo=thr_lo)
    if verbose:
        print(f"[info] Threshold auto-detected: {thr:.3f} (hi={thr_hi}, lo={thr_lo})")
        if dump_stats:
            for au in needed_aus:
                s = pd.to_numeric(aus_df[au], errors="coerce")
                print(f"{au:>4} count={int(s.notna().sum()):>6} "
                      f"min={s.min(skipna=True):.3f} p50={s.quantile(0.5):.3f} "
                      f"p95={s.quantile(0.95):.3f} max={s.max(skipna=True):.3f}")

    if sample_n > 0:
        n = min(sample_n, len(aus_df))
        print(f"[info] Sample of first {n} rows for needed AUs:")
        print(aus_df.head(n).to_string(index=False))

    # Per-frame flags
    flags_df = pd.DataFrame(index=df.index)
    for cname, spec in clusters.items():
        vals_mat = aus_df[spec["aus"]].values
        flags_df[cname] = [compute_cluster_flag(list(row), spec["rule"], thr) for row in vals_mat]
        if verbose:
            print(f"[info] Cluster '{cname}': active frames = {int(flags_df[cname].sum())}/{len(flags_df)}")

    # Frame key (optional)
    frame_key = None
    for cand in ["frame","timestamp","time","Frame","Timestamp"]:
        if cand in df.columns: frame_key = cand; break

    # Emotions present?
    available_emotions = [c for c in EMOTION_COLS if c in df.columns]

    # Optional per-frame JSON
    frames = None
    if include_frames:
        frames = []
        for i in range(len(flags_df)):
            rec = {k: bool(flags_df.iloc[i][k]) for k in flags_df.columns}
            rec["index"] = int(i)
            if frame_key is not None:
                val = df.loc[i, frame_key]
                try: rec[frame_key] = int(val)
                except Exception:
                    try: rec[frame_key] = float(val)
                    except Exception: rec[frame_key] = str(val)
            if available_emotions:
                emo = {}
                for col in available_emotions:
                    v = df.loc[i, col]
                    try: emo[col] = float(v)
                    except Exception: emo[col] = v if pd.notna(v) else None
                rec["emotions"] = emo
            frames.append(rec)

    # Segments
    times = resolve_time_series(df, fps_fallback=fps, prefer_frame_time=prefer_frame_time)
    if verbose:
        duration = float(times.max()) if len(times) else 0.0
        print(f"[info] Time base: {'frame/fps' if prefer_frame_time else 'auto'} "
            f"(fps={fps:.3f}) -> duration~{duration:.3f}s, rows={len(times)}")

    segments_out = []
    for seg_start, seg_end, m in make_overlapping_segments(times, win_sec=win_sec, hop_sec=hop_sec):
        n = int(m.sum())
        if n == 0:
            cluster_rates = {name: 0.0 for name in flags_df.columns}
            emo_means = {col: None for col in available_emotions}
        else:
            cluster_rates = {name: float(flags_df.loc[m, name].mean()) for name in flags_df.columns}
            if available_emotions:
                emo_means = (df.loc[m, available_emotions]
                               .apply(pd.to_numeric, errors="coerce")
                               .mean(skipna=True)
                               .to_dict())
                emo_means = {k: (None if pd.isna(v) else float(v)) for k, v in emo_means.items()}
            else:
                emo_means = {}

        emotions_sparse = sparsify_emotions(emo_means, p_min=emo_min, margin=emo_margin) if available_emotions else {}
        clusters_sparse = sparsify_clusters(cluster_rates, min_rate=cluster_min_rate)

        seg = {"timestamp": fmt_range(seg_start, seg_end)}
        if emotions_sparse: seg["emotions"] = emotions_sparse
        if clusters_sparse: seg["clusters"] = clusters_sparse
        segments_out.append(seg)

    if verbose:
        print(f"[info] Segments produced: {len(segments_out)} (win={win_sec:.2f}s, hop={hop_sec:.2f}s)")

    out = {
        "metadata": {
            "input_csv": str(Path(in_csv).name),
            "threshold_used": thr,
            "threshold_hi_param": thr_hi,
            "threshold_lo_param": thr_lo,
            "clusters": BASE_CLUSTERS,
            "au_scale_hint": "auto-detected via 95th percentile",
            "fps_used": fps,
            "window_sec": win_sec,
            "hop_sec": hop_sec,
            "emo_min": emo_min,
            "emo_margin": emo_margin,
            "cluster_min_rate": cluster_min_rate,
            "num_frames": int(len(df)),
            "num_segments": int(len(segments_out)),
        },
        "segments": segments_out
    }
    if include_frames and frames is not None:
        out["frames"] = frames

    Path(out_json).parent.mkdir(parents=True, exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"[done] Wrote {out_json} with {len(segments_out)} segments.")


# if __name__ == "__main__":
#     ap = argparse.ArgumentParser()
#     ap.add_argument("--in_csv", required=True)
#     ap.add_argument("--out_json", required=True)

#     ap.add_argument("--thr_hi", type=float, default=DEFAULTS["thr_hi"])
#     ap.add_argument("--thr_lo", type=float, default=DEFAULTS["thr_lo"])

#     ap.add_argument("--verbose", action="store_true")
#     ap.add_argument("--print_cols", action="store_true")
#     ap.add_argument("--dump_stats", action="store_true")
#     ap.add_argument("--sample_n", type=int, default=5)

#     ap.add_argument("--fps", type=float, default=DEFAULTS["fps"])
#     ap.add_argument("--win_sec", type=float, default=DEFAULTS["win_sec"])
#     ap.add_argument("--hop_sec", type=float, default=DEFAULTS["hop_sec"])

#     ap.add_argument("--emo_min", type=float, default=DEFAULTS["emo_min"])
#     ap.add_argument("--emo_margin", type=float, default=DEFAULTS["emo_margin"])
#     ap.add_argument("--cluster_min_rate", type=float, default=DEFAULTS["cluster_min_rate"])

#     ap.add_argument("--prefer_frame_time", action="store_true",
#                     help="Use frame/FPS-derived time even if a timestamp column exists")
#     ap.add_argument("--include_frames", action="store_true",
#                     help="Include per-frame JSON records")

#     args = ap.parse_args()
#     extract_video_features_to_json(args.in_csv, args.out_json, args.thr_hi, args.thr_lo,
#          args.verbose, args.print_cols, args.dump_stats, args.sample_n,
#          args.fps, args.win_sec, args.hop_sec,
#          args.emo_min, args.emo_margin, args.cluster_min_rate,
#          args.prefer_frame_time, args.include_frames)


from presentation_analyzer.utils.frame_extraction import extract_frames
from presentation_analyzer.utils.pyfeat_runner import run_pyfeat_on_frames

def end_to_end_video(video_path: str,
                     json_out_path: str = None,
                     thr_hi: float = DEFAULTS["thr_hi"],
                     thr_lo: float = DEFAULTS["thr_lo"],
                     fps: float = DEFAULTS["fps"],
                     win_sec: float = DEFAULTS["win_sec"],
                     hop_sec: float = DEFAULTS["hop_sec"],
                     emo_min: float = DEFAULTS["emo_min"],
                     emo_margin: float = DEFAULTS["emo_margin"],
                     cluster_min_rate: float = DEFAULTS["cluster_min_rate"],
                     include_frames: bool = False,
                     verbose: bool = False) -> str:
    """
    Takes an input video, extracts AUs, then runs extract_video_features_to_json.
    Returns the JSON output file path.
    """
    video_path = Path(video_path)
    if not video_path.exists():
        raise FileNotFoundError(video_path)
    
    frames_dir = extract_frames(video_path=video_path)
    csv_path = "presentation_analyzer/output/pyfeat_results.csv"
    run_pyfeat_on_frames(frame_dir=frames_dir, output_csv=csv_path)

    # 1. Decide where to write the intermediate AU CSV
    # tmp_dir = tempfile.mkdtemp(prefix="au_features_")
    # au_csv_path = Path(tmp_dir) / (csv_path)
    # au_csv_path.parent.mkdir(parents=True, exist_ok=True)  # <- make sure directory exists

    # 2. Run your AU extractor here (this is just an example, adjust to your pipeline)
    # Example using py-feat CLI:
    # subprocess.run(["feat", "extract", "-i", str(video_path), "-o", str(au_csv_path)], check=True)
    #
    # Or, if you already have a Python function to extract AUs:
    # my_extract_aus(video_path, au_csv_path)

    # 3. Decide on JSON output path
    if json_out_path is None:
        json_out_path = (video_path.stem + "_features.json")
    else:
        json_out_path = Path(json_out_path)

    # 4. Run your existing extraction function
    extract_video_features_to_json(
        in_csv=str(csv_path),
        out_json=str(json_out_path),
        thr_hi=thr_hi,
        thr_lo=thr_lo,
        verbose=verbose,
        print_cols=False,
        dump_stats=False,
        sample_n=5,
        fps=fps,
        win_sec=win_sec,
        hop_sec=hop_sec,
        emo_min=emo_min,
        emo_margin=emo_margin,
        cluster_min_rate=cluster_min_rate,
        include_frames=include_frames,
        prefer_frame_time=True,
    )

    return str(json_out_path)

# json_path = end_to_end_video(r"C:\Users\Jeslyn\OneDrive\Desktop\capstone\Capstone-2T6\IMG_4027.MOV", include_frames=True, verbose=True)
