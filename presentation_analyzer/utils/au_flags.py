#!/usr/bin/env python3
"""
Compute 5 AU cluster flags per frame from a Py-Feat AU CSV and output JSON.
Also copies emotion columns (anger, disgust, fear, happiness, sadness, surprise, neutral)
directly into the JSON for each frame.

Usage:
  python au_flags.py --in_csv path/to/aus.csv --out_json path/to/flags.json
  [--thr_hi 1.5] [--thr_lo 0.3] [--verbose] [--print_cols] [--dump_stats] [--sample_n 5]
"""

import argparse, json, math
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd

DEFAULTS = {"thr_hi": 1.5, "thr_lo": 0.3}

# Base clusters (expressive_speech will adapt based on available AUs)
BASE_CLUSTERS = {
    "authentic_smile":   {"aus": ["AU6", "AU12"],          "rule": "min_and"},
    "eyebrow_engagement":{"aus": ["AU1", "AU2", "AU5"],    "rule": "avg_and_majority"},
    "focused_thinking":  {"aus": ["AU4", "AU7"],           "rule": "min_and"},
    "tension":           {"aus": ["AU14", "AU15", "AU17"], "rule": "avg_and_majority"},
}
EMOTION_COLS = ["anger","disgust","fear","happiness","sadness","surprise","neutral"]

# ---------- AU column handling ----------
def canonical_au_variants(base_au: str) -> List[Tuple[str,str]]:
    """
    Return possible column name variants for intensity and presence.
    Supports:
      AU01_r / AU01_c / AU1_r / AU1_c
      AU01 (treated as intensity) / AU1 (treated as intensity)
    """
    num = base_au.replace("AU", "")
    try:
        n = int(num)
    except ValueError:
        n = num
    z = f"{int(n):02d}" if isinstance(n, int) else str(n)
    return [
        (f"AU{z}_r", "intensity"),
        (f"AU{z}_c", "presence"),
        (f"AU{z}",   "intensity"),   # plain zero-padded
        (f"AU{n}_r", "intensity"),
        (f"AU{n}_c", "presence"),
        (f"AU{n}",   "intensity"),   # plain non-padded
    ]

def locate_column(df: pd.DataFrame, base_au: str) -> Optional[Tuple[str,str]]:
    for col, kind in canonical_au_variants(base_au):
        if col in df.columns:
            return col, kind
    return None

def to_intensity(df: pd.DataFrame, base_au: str) -> Optional[pd.Series]:
    # prefer intensity
    for col, kind in canonical_au_variants(base_au):
        if col in df.columns and kind == "intensity":
            return pd.to_numeric(df[col], errors="coerce")
    # fallback to presence mapped to [0,1]
    for col, kind in canonical_au_variants(base_au):
        if col in df.columns and kind == "presence":
            return pd.to_numeric(df[col], errors="coerce").fillna(0.0).clip(lower=0.0, upper=1.0)
    return None

# ---------- Thresholding & rules ----------
def auto_threshold(df_intensities: pd.DataFrame, thr_hi: float, thr_lo: float) -> float:
    if df_intensities.empty:
        return thr_hi
    # pandas >= 2.1 prefers future_stack=True and forbids dropna with it
    try:
        s = df_intensities.stack(future_stack=True)
    except TypeError:
        # older pandas: no future_stack, use dropna=True
        s = df_intensities.stack(dropna=True)
    q95 = s.quantile(0.95)
    if pd.isna(q95):
        return thr_hi
    return thr_hi if q95 > 1.0 else thr_lo

def compute_cluster_flag(row_vals: List[float], rule: str, thr: float) -> bool:
    vals = [0.0 if (isinstance(v, float) and math.isnan(v)) else float(v) for v in row_vals]
    if not vals:
        return False
    if rule == "min_and":           # all must be above thr
        return min(vals) >= thr
    if rule == "avg_and_majority":  # average above thr AND majority above thr
        avg_ok = sum(vals)/len(vals) >= thr
        count_ok = sum(v >= thr for v in vals) >= math.ceil(len(vals)/2)
        return avg_ok and count_ok
    if rule == "any_max":           # any one above thr
        return max(vals) >= thr
    return False

def describe_series(s: pd.Series) -> Dict[str, float]:
    s = pd.to_numeric(s, errors="coerce")
    return {
        "count": int(s.notna().sum()),
        "min": float(s.min(skipna=True)) if s.notna().any() else float("nan"),
        "p25": float(s.quantile(0.25)) if s.notna().any() else float("nan"),
        "p50": float(s.quantile(0.50)) if s.notna().any() else float("nan"),
        "p95": float(s.quantile(0.95)) if s.notna().any() else float("nan"),
        "max": float(s.max(skipna=True)) if s.notna().any() else float("nan"),
    }

def build_clusters_with_availability(df: pd.DataFrame, verbose: bool=False) -> Dict[str, Dict]:
    clusters = dict(BASE_CLUSTERS)
    # expressive_speech: use whichever of AU25/26/27 exist
    available = []
    for au in ["AU25","AU26","AU27"]:
        if locate_column(df, au) is not None:
            available.append(au)
    if available:
        clusters["expressive_speech"] = {"aus": available, "rule": "any_max"}
        if verbose and set(available) != {"AU25","AU26","AU27"}:
            print(f"[warn] expressive_speech missing some AUs; using {available}")
    else:
        if verbose:
            print("[warn] expressive_speech cannot be computed (AU25/AU26/AU27 all missing)")
    return clusters

# ---------- Main ----------
def main(in_csv: str, out_json: str, thr_hi: float, thr_lo: float,
         verbose: bool, print_cols: bool, dump_stats: bool, sample_n: int):
    if verbose: print("[info] Loading CSV:", in_csv)
    df = pd.read_csv(in_csv)

    if print_cols:
        print("[info] CSV columns:")
        for c in df.columns:
            print("  -", c)

    clusters = build_clusters_with_availability(df, verbose=verbose)

    # collect AU columns we actually use + map which column variant was chosen
    needed_aus = sorted({au for spec in clusters.values() for au in spec["aus"]})
    au_series: Dict[str, pd.Series] = {}
    au_resolved_cols: Dict[str, str] = {}
    au_kinds: Dict[str, str] = {}

    for au in needed_aus:
        loc = locate_column(df, au)
        if loc is None:
            # fallback to zeros if missing
            au_series[au] = pd.Series([0.0]*len(df), index=df.index, dtype=float)
            au_resolved_cols[au] = "<missing>"
            au_kinds[au] = "none"
        else:
            col, kind = loc
            s = to_intensity(df, au)
            if s is None:
                s = pd.Series([0.0]*len(df), index=df.index, dtype=float)
            au_series[au] = s
            au_resolved_cols[au] = col
            au_kinds[au] = kind

    if verbose:
        print("[info] AU column resolution (base -> used column [type]):")
        for au in needed_aus:
            print(f"{au:>4} -> {au_resolved_cols[au]} [{au_kinds[au]}]")

    aus_df = pd.DataFrame(au_series)

    thr = auto_threshold(aus_df, thr_hi=thr_hi, thr_lo=thr_lo)
    if verbose:
        print(f"[info] Threshold auto-detected: {thr:.3f} (hi={thr_hi}, lo={thr_lo})")
        if dump_stats:
            print("[info] AU intensity summary (after presence→intensity mapping):")
            for au in needed_aus:
                stats = describe_series(aus_df[au])
                print(f"{au:>4} count={stats['count']:>6} min={stats['min']:.3f} "
                      f"p50={stats['p50']:.3f} p95={stats['p95']:.3f} max={stats['max']:.3f}")

    # Optional sample rows for sanity check
    if sample_n > 0:
        n = min(sample_n, len(aus_df))
        print(f"[info] Sample of first {n} rows for needed AUs:")
        # printing directly to avoid pandas display formatting issues in some shells
        print(aus_df.head(n).to_string(index=False))

    # Compute flags
    flags_df = pd.DataFrame(index=df.index)
    for cname, spec in clusters.items():
        aus = spec["aus"]
        if not aus:
            continue
        rule = spec["rule"]
        vals_mat = aus_df[aus].values
        flags = []
        for row in vals_mat:
            flags.append(compute_cluster_flag(list(row), rule, thr))
        flags_df[cname] = flags
        if verbose:
            on_count = int(flags_df[cname].sum())
            print(f"[info] Cluster '{cname}': active frames = {on_count}/{len(flags_df)}")

    # Frame key (optional)
    frame_key = None
    for candidate in ["frame","timestamp","time","Frame","Timestamp"]:
        if candidate in df.columns:
            frame_key = candidate; break

    # Emotions: only include those present
    available_emotions = [col for col in EMOTION_COLS if col in df.columns]
    if verbose and available_emotions:
        print("[info] Emotions found:", available_emotions)

    # Build per-frame JSON records (AUs + emotions)
    frames = []
    for i in range(len(flags_df)):
        rec = {k: bool(flags_df.iloc[i][k]) for k in flags_df.columns}
        rec["index"] = int(i)
        if frame_key is not None:
            val = df.loc[i, frame_key]
            # serialize frame id safely
            try: rec[frame_key] = int(val)
            except Exception:
                try: rec[frame_key] = float(val)
                except Exception: rec[frame_key] = str(val)
        # add emotions if present
        if available_emotions:
            emo = {}
            for col in available_emotions:
                v = df.loc[i, col]
                try:
                    emo[col] = float(v)
                except Exception:
                    # if non-numeric, keep as string fallback
                    emo[col] = v if pd.notna(v) else None
            rec["emotions"] = emo

        frames.append(rec)

    out = {
        "metadata": {
            "input_csv": str(Path(in_csv).name),
            "threshold_used": thr,
            "threshold_hi_param": thr_hi,
            "threshold_lo_param": thr_lo,
            "clusters": clusters,
            "au_scale_hint": "auto-detected via 95th percentile",
            "au_column_resolution": {au: {"column": au_resolved_cols[au], "type": au_kinds[au]} for au in needed_aus},
            "emotions_included": available_emotions,
        },
        "frames": frames,
    }

    Path(out_json).parent.mkdir(parents=True, exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"[done] Wrote {out_json} with {len(frames)} frame records.")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--in_csv", required=True)
    ap.add_argument("--out_json", required=True)
    ap.add_argument("--thr_hi", type=float, default=DEFAULTS["thr_hi"])
    ap.add_argument("--thr_lo", type=float, default=DEFAULTS["thr_lo"])
    ap.add_argument("--verbose", action="store_true", help="Print detailed diagnostics")
    ap.add_argument("--print_cols", action="store_true", help="Print every CSV column name")
    ap.add_argument("--dump_stats", action="store_true", help="Print per-AU stats (min/median/p95)")
    ap.add_argument("--sample_n", type=int, default=5, help="Print first N rows of used AU columns")
    args = ap.parse_args()
    main(args.in_csv, args.out_json, args.thr_hi, args.thr_lo,
         args.verbose, args.print_cols, args.dump_stats, args.sample_n)
